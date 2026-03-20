"""Business logic for the playbooks vertical."""

import gzip

from ..models import EventType, Playbook, PlaybookOverview, STRFTIME
from ..repos.postgres import events, playbooks


def load_playbook_selection(name: str) -> dict:
    versions = playbooks.list_playbook_versions(name)
    version_strings = sorted([x.version.strftime(STRFTIME) for x in versions])
    selected_version = _find_default_version(versions)

    playbook = playbooks.get_playbook(name, selected_version)
    content = _decode_playbook(playbook)

    return {
        "playbook_name": name,
        "playbook_version": selected_version,
        "default_version": selected_version,
        "playbook_versions": version_strings,
        "original_content": content,
        "modified_content": content,
    }


def load_playbook_version(name: str, version: str) -> dict:
    playbook = playbooks.get_playbook(name, version)
    content = _decode_playbook(playbook)
    return {
        "playbook_version": version,
        "original_content": content,
        "modified_content": content,
    }


def set_default_playbook(name: str, version: str, updated_by: str) -> None:
    playbooks.set_default_playbook(name, version, updated_by)
    events.insert_event_log(
        updated_by,
        EventType.PLAYBOOK_SET_DEFAULT,
        {"name": name, "version": version},
    )


def delete_playbook_version(
    name: str,
    version: str,
    default_version: str,
    deleted_by: str,
) -> dict:
    if version == default_version:
        raise ValueError("Cannot delete the default version")

    playbooks.remove_playbook(name, version)
    events.insert_event_log(
        deleted_by,
        EventType.PLAYBOOK_REMOVE,
        {"name": name, "version": version},
    )

    versions = playbooks.list_playbook_versions(name)
    selected_version = default_version
    playbook = playbooks.get_playbook(name, selected_version)
    content = _decode_playbook(playbook)

    return {
        "playbook_versions": sorted([x.version.strftime(STRFTIME) for x in versions]),
        "playbook_version": selected_version,
        "default_version": default_version,
        "original_content": content,
        "modified_content": content,
    }


def save_playbook_content(name: str, content: str, created_by: str) -> dict:
    saved = playbooks.add_playbook(
        name,
        gzip.compress(content.encode("utf-8")),
        created_by,
    )
    saved_version = saved.version.strftime(STRFTIME)
    events.insert_event_log(
        created_by,
        EventType.PLAYBOOK_ADD,
        {"name": name, "version": saved_version},
    )

    versions = playbooks.list_playbook_versions(name)
    return {
        "playbook_versions": sorted([x.version.strftime(STRFTIME) for x in versions]),
        "playbook_version": saved_version,
        "original_content": content,
        "modified_content": content,
    }


def _find_default_version(versions: list[PlaybookOverview]) -> str:
    selected_version = ""
    running_default = ""
    for item in versions:
        if item.default_version and item.default_version.strftime(STRFTIME) > running_default:
            running_default = item.default_version.strftime(STRFTIME)
            selected_version = item.version.strftime(STRFTIME)

    if selected_version:
        return selected_version
    if versions:
        return versions[-1].version.strftime(STRFTIME)
    raise ValueError("No playbook versions found")


def _decode_playbook(playbook: Playbook) -> str:
    if playbook.playbook is None:
        return ""
    return gzip.decompress(playbook.playbook).decode("utf-8")
