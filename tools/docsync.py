#!/usr/bin/env python3
"""Generate deterministic documentation indexes from the CP codebase.

`docsync.py` owns structural facts: packages, modules, symbols, imports, API
routes, and command-handler maps. It does not summarize intent; human-authored
docs and LLM-assisted summaries should use this output as their source map.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOTS = (ROOT / "cp", ROOT / "tools")
DOCS = ROOT / "docs"
GENERATED = DOCS / "generated"
GENERATED_API = GENERATED / "api"
BUILD = ROOT / ".build"
PROJECT_INDEX = BUILD / "project-index.json"
GENERATED_MARKER = "<!-- GENERATED FILE: DO NOT EDIT -->"
SKIP_PARTS = {"__pycache__", ".venv", ".ruff_cache", ".git", ".archive"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


@dataclass(frozen=True)
class ImportInfo:
    module: str
    names: list[str] = field(default_factory=list)
    level: int = 0


@dataclass(frozen=True)
class RouteInfo:
    method: str
    path: str
    full_path: str
    function: str
    lineno: int
    response_model: str | None = None
    dependencies: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FunctionInfo:
    name: str
    lineno: int
    signature: str
    docstring: str | None
    decorators: list[str] = field(default_factory=list)
    is_async: bool = False


@dataclass(frozen=True)
class ClassInfo:
    name: str
    lineno: int
    docstring: str | None
    bases: list[str] = field(default_factory=list)
    methods: list[FunctionInfo] = field(default_factory=list)


@dataclass(frozen=True)
class ModuleInfo:
    path: str
    module_name: str
    package: str
    docstring: str | None
    imports: list[ImportInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    routes: list[RouteInfo] = field(default_factory=list)
    command_handlers: dict[str, str] = field(default_factory=dict)


def ast_to_str(node: ast.AST | None) -> str:
    """Return a deterministic source-like representation for an AST node."""
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return node.__class__.__name__


def literal_string(node: ast.AST | None) -> str | None:
    """Return a string literal value when an AST node is a string constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def module_name_from_path(path: Path) -> str:
    """Convert a Python file path under the repo into an import-style name."""
    rel = path.relative_to(ROOT).with_suffix("")
    if rel.name == "__init__":
        rel = rel.parent
    return ".".join(rel.parts)


def iter_python_files() -> list[Path]:
    """Return all Python source files that should be part of the docs index."""
    files: list[Path] = []
    for root in PYTHON_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(path)
    return sorted(files)


def extract_imports(tree: ast.Module) -> list[ImportInfo]:
    """Extract top-level imports from a module."""
    imports: list[ImportInfo] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.append(
                ImportInfo(
                    module="",
                    names=sorted(alias.name for alias in node.names),
                    level=0,
                )
            )
        elif isinstance(node, ast.ImportFrom):
            imports.append(
                ImportInfo(
                    module=node.module or "",
                    names=sorted(alias.name for alias in node.names),
                    level=node.level,
                )
            )
    return imports


def join_paths(prefix: str, path: str) -> str:
    """Join FastAPI router prefix and route path into one normalized path."""
    if not prefix:
        return path
    if path == "/":
        return prefix
    return f"{prefix.rstrip('/')}/{path.lstrip('/')}"


def extract_router_prefix(tree: ast.Module) -> str:
    """Extract `APIRouter(prefix=...)` when a module defines a router."""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "router"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        if ast_to_str(node.value.func) != "APIRouter":
            continue
        for keyword in node.value.keywords:
            if keyword.arg == "prefix":
                return literal_string(keyword.value) or ""
    return ""


def function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build a readable signature for a function without importing the module."""
    args = ast_to_str(node.args)
    returns = f" -> {ast_to_str(node.returns)}" if node.returns else ""
    return f"{node.name}({args}){returns}"


def decorator_strings(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return decorators as source-like strings."""
    return [ast_to_str(decorator) for decorator in node.decorator_list]


def public_function_info(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> FunctionInfo | None:
    """Return function metadata for public functions and methods."""
    if node.name.startswith("_"):
        return None
    return FunctionInfo(
        name=node.name,
        lineno=node.lineno,
        signature=function_signature(node),
        docstring=ast.get_docstring(node),
        decorators=decorator_strings(node),
        is_async=isinstance(node, ast.AsyncFunctionDef),
    )


def extract_classes(tree: ast.Module) -> list[ClassInfo]:
    """Extract public classes and their public methods."""
    classes: list[ClassInfo] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name.startswith("_"):
            continue
        methods = [
            info
            for item in node.body
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef)
            for info in [public_function_info(item)]
            if info is not None
        ]
        classes.append(
            ClassInfo(
                name=node.name,
                lineno=node.lineno,
                docstring=ast.get_docstring(node),
                bases=[ast_to_str(base) for base in node.bases],
                methods=methods,
            )
        )
    return classes


def extract_functions(tree: ast.Module) -> list[FunctionInfo]:
    """Extract public top-level functions."""
    return [
        info
        for node in tree.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        for info in [public_function_info(node)]
        if info is not None
    ]


def route_from_decorator(
    decorator: ast.AST,
    function_name: str,
    lineno: int,
    router_prefix: str,
) -> RouteInfo | None:
    """Extract FastAPI route metadata from `@router.<method>(...)` decorators."""
    if not isinstance(decorator, ast.Call):
        return None
    func = decorator.func
    if not isinstance(func, ast.Attribute):
        return None
    if func.attr not in HTTP_METHODS:
        return None
    if ast_to_str(func.value) != "router":
        return None

    route_path = literal_string(decorator.args[0]) if decorator.args else None
    if route_path is None:
        return None

    keyword_map = {kw.arg: kw.value for kw in decorator.keywords if kw.arg}
    response_model = ast_to_str(keyword_map.get("response_model")) or None
    dependencies = []
    responses = keyword_map.get("dependencies")
    if isinstance(responses, ast.List):
        dependencies = [ast_to_str(item) for item in responses.elts]

    return RouteInfo(
        method=func.attr.upper(),
        path=route_path,
        full_path=join_paths(router_prefix, route_path),
        function=function_name,
        lineno=lineno,
        response_model=response_model,
        dependencies=dependencies,
    )


def extract_routes(tree: ast.Module) -> list[RouteInfo]:
    """Extract FastAPI routes from public top-level route handlers."""
    routes: list[RouteInfo] = []
    router_prefix = extract_router_prefix(tree)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for decorator in node.decorator_list:
            route = route_from_decorator(
                decorator,
                node.name,
                node.lineno,
                router_prefix,
            )
            if route is not None:
                routes.append(route)
    return routes


def extract_command_handlers(tree: ast.Module) -> dict[str, str]:
    """Extract `COMMAND_HANDLERS` mappings from worker dispatch modules."""
    handlers: dict[str, str] = {}
    for node in tree.body:
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "COMMAND_HANDLERS"
                for target in node.targets
            ):
                value = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "COMMAND_HANDLERS"
        ):
            value = node.value

        if value is None:
            continue
        if not isinstance(value, ast.Dict):
            continue
        for key, handler in zip(value.keys, value.values, strict=False):
            if key is None:
                continue
            handlers[ast_to_str(key)] = ast_to_str(handler)
    return dict(sorted(handlers.items()))


def parse_python_file(path: Path) -> ModuleInfo:
    """Parse one Python file into deterministic metadata."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    module_name = module_name_from_path(path)
    return ModuleInfo(
        path=str(path.relative_to(ROOT)),
        module_name=module_name,
        package=module_name.split(".")[0],
        docstring=ast.get_docstring(tree),
        imports=extract_imports(tree),
        classes=extract_classes(tree),
        functions=extract_functions(tree),
        routes=extract_routes(tree),
        command_handlers=extract_command_handlers(tree),
    )


def scan_project() -> list[ModuleInfo]:
    """Scan Python source roots and return sorted module metadata."""
    return [parse_python_file(path) for path in iter_python_files()]


def first_sentence(text: str | None) -> str:
    """Return a short docstring summary suitable for tables."""
    if not text:
        return "_No docstring._"
    stripped = " ".join(text.strip().split())
    return stripped.split(". ")[0].rstrip(".") + "."


def route_sort_key(route: dict[str, Any]) -> tuple[str, str, str]:
    """Sort routes by path, method, then handler."""
    return (route["full_path"], route["method"], route["function"])


def build_project_index(modules: list[ModuleInfo]) -> dict[str, Any]:
    """Build the machine-readable project index consumed by docs and agents."""
    module_dicts = [asdict(module) for module in modules]
    routes = [
        asdict(route) | {"module": module.module_name}
        for module in modules
        for route in module.routes
    ]
    routes = sorted(routes, key=route_sort_key)
    commands = [
        {"command": command, "handler": handler, "module": module.module_name}
        for module in modules
        for command, handler in module.command_handlers.items()
    ]
    commands = sorted(commands, key=lambda row: (row["command"], row["module"]))

    packages: dict[str, dict[str, int]] = {}
    for module in modules:
        stats = packages.setdefault(
            module.package,
            {
                "modules": 0,
                "classes": 0,
                "functions": 0,
                "routes": 0,
            },
        )
        stats["modules"] += 1
        stats["classes"] += len(module.classes)
        stats["functions"] += len(module.functions)
        stats["routes"] += len(module.routes)

    return {
        "schema_version": 1,
        "source_roots": [
            str(path.relative_to(ROOT)) for path in PYTHON_ROOTS if path.exists()
        ],
        "packages": dict(sorted(packages.items())),
        "modules": module_dicts,
        "routes": routes,
        "command_handlers": commands,
    }


def generated_header(title: str) -> list[str]:
    """Return a standard generated Markdown header."""
    return [GENERATED_MARKER, "", f"# {title}", ""]


def render_code_map(index: dict[str, Any]) -> str:
    """Render a module-oriented generated code map."""
    lines = generated_header("Generated Code Map")
    lines.append("> Generated by `tools/docsync.py`. Do not edit manually.")
    lines.append("")

    current_package = None
    for module in index["modules"]:
        package = module["package"]
        if package != current_package:
            current_package = package
            lines.append(f"## `{package}`")
            lines.append("")

        lines.append(f"### `{module['module_name']}`")
        lines.append("")
        lines.append(f"Path: `{module['path']}`")
        lines.append("")
        lines.append(first_sentence(module["docstring"]))
        lines.append("")

        if module["classes"]:
            lines.append("Classes:")
            for cls in module["classes"]:
                lines.append(
                    f"- `{cls['name']}` — line {cls['lineno']}: "
                    f"{first_sentence(cls['docstring'])}"
                )
            lines.append("")

        if module["functions"]:
            lines.append("Functions:\n")
            for fn in module["functions"]:
                async_marker = "async " if fn["is_async"] else ""
                lines.append(
                    f"- `{async_marker}{fn['signature']}` — line {fn['lineno']}: "
                    f"{first_sentence(fn['docstring'])}"
                )
            lines.append("")

        if module["routes"]:
            lines.append("Routes:")
            for route in module["routes"]:
                lines.append(
                    f"- `{route['method']} {route['full_path']}` -> "
                    f"`{route['function']}()`"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_package_index(index: dict[str, Any]) -> str:
    """Render package/module summary tables."""
    lines = generated_header("Generated Package Index")
    lines.extend(
        [
            "| Package | Modules | Classes | Functions | Routes |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for package, stats in index["packages"].items():
        lines.append(
            f"| `{package}` | {stats['modules']} | {stats['classes']} | "
            f"{stats['functions']} | {stats['routes']} |"
        )
    lines.append("")
    lines.append("## Modules")
    lines.append("")
    lines.append("| Module | Path | Summary |")
    lines.append("| --- | --- | --- |")
    for module in index["modules"]:
        lines.append(
            f"| `{module['module_name']}` | `{module['path']}` | "
            f"{first_sentence(module['docstring'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_api_routes(index: dict[str, Any]) -> str:
    """Render FastAPI route inventory."""
    lines = generated_header("Generated API Route Index")
    if not index["routes"]:
        lines.append("_No routes found._")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("| Method | Path | Handler | Response Model |")
    lines.append("| --- | --- | --- | --- |")
    for route in index["routes"]:
        response_model = route["response_model"] or "-"
        lines.append(
            f"| `{route['method']}` | `{route['full_path']}` | "
            f"`{route['module']}.{route['function']}` | `{response_model}` |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_llm_index(index: dict[str, Any]) -> str:
    """Render a compact agent-facing navigation index."""
    lines = generated_header("Generated LLM Index")
    lines.extend(
        [
            "Use this file as a compact starting point before opening source files.",
            "",
            "## Source Roots",
            "",
        ]
    )
    for source_root in index["source_roots"]:
        lines.append(f"- `{source_root}`")
    lines.append("")
    lines.append("## Packages")
    lines.append("")
    for package, stats in index["packages"].items():
        lines.append(
            f"- `{package}`: {stats['modules']} modules, "
            f"{stats['classes']} classes, {stats['functions']} functions, "
            f"{stats['routes']} routes"
        )
    lines.append("")
    lines.append("## API Route Count")
    lines.append("")
    lines.append(f"- `{len(index['routes'])}` FastAPI routes")
    lines.append("")
    lines.append("## Command Handlers")
    lines.append("")
    if index["command_handlers"]:
        for command in index["command_handlers"]:
            lines.append(
                f"- `{command['command']}` -> `{command['module']}.{command['handler']}`"
            )
    else:
        lines.append("- _No command handlers found._")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    lines.append("- `docs/generated/code-map.md`")
    lines.append("- `docs/generated/package-index.md`")
    lines.append("- `docs/generated/api/routes.md`")
    lines.append("- `docs/generated/python-reference.md`")
    lines.append("- `.build/project-index.json`")
    return "\n".join(lines).rstrip() + "\n"


def render_python_reference(index: dict[str, Any]) -> str:
    """Render a MkDocstrings reference page for importable Python modules."""
    lines = generated_header("Generated Python Reference")
    lines.extend(
        [
            "> Generated by `tools/docsync.py` using MkDocstrings directives.",
            "",
        ]
    )

    current_package = None
    for module in index["modules"]:
        module_name = module["module_name"]
        if module_name.endswith(".__init__"):
            continue
        if module_name == "cp" or module_name.startswith("tools"):
            continue

        package = ".".join(module_name.split(".")[:2])
        if package != current_package:
            current_package = package
            lines.append(f"## `{package}`")
            lines.append("")

        lines.append(f"### `{module_name}`")
        lines.append("")
        lines.append(f"::: {module_name}")
        lines.append("    options:")
        lines.append("      show_source: true")
        lines.append("      show_root_heading: false")
        lines.append("      show_root_toc_entry: false")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def json_dumps(data: dict[str, Any]) -> str:
    """Serialize JSON deterministically with a trailing newline."""
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def file_hash(content: str) -> str:
    """Return a stable content hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_or_check(path: Path, content: str, check: bool) -> bool:
    """Write a generated file or report it stale in check mode."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if file_hash(existing) == file_hash(content):
        return True

    if check:
        print(f"STALE: {path.relative_to(ROOT)}")
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path.relative_to(ROOT)}")
    return True


def generated_outputs(index: dict[str, Any]) -> dict[Path, str]:
    """Return all deterministic generated outputs."""
    return {
        PROJECT_INDEX: json_dumps(index),
        GENERATED / "code-map.md": render_code_map(index),
        GENERATED / "package-index.md": render_package_index(index),
        GENERATED_API / "routes.md": render_api_routes(index),
        GENERATED / "llm-index.md": render_llm_index(index),
        GENERATED / "python-reference.md": render_python_reference(index),
    }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated outputs")
    mode.add_argument("--check", action="store_true", help="verify generated outputs")
    args = parser.parse_args()

    try:
        modules = scan_project()
        index = build_project_index(modules)
        outputs = generated_outputs(index)
        ok = all(
            write_or_check(path, content, check=args.check)
            for path, content in outputs.items()
        )
        return 0 if ok else 1
    except SyntaxError as err:
        print(f"ERROR: unable to parse {err.filename}: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
