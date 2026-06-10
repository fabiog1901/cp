(function () {
  const CP_ADMIN_VIEWS = new Set([
    "versions",
    "node_counts",
    "cpu_counts",
    "disk_sizes",
    "database_role_templates",
    "regions",
  ]);

  const EXCLUDED_LEGACY_METHODS = new Set(["init"]);
  const CPKIT_STATE_KEYS = new Set([
    "view",
    "apiBase",
    "authChecked",
    "isAuthenticated",
    "authClaims",
    "authLoginPath",
    "authDisplayNameClaim",
    "authSessionCookieName",
    "authError",
    "viewNotice",
    "viewNoticeJobId",
    "jobs",
    "jobStats",
    "jobsVisibleRows",
    "jobsFilterQuery",
    "jobsLastUpdatedUtc",
    "jobsSortIndex",
    "jobsSortDir",
    "jobsLoading",
    "jobsAutoRefreshEnabled",
    "_jobsAutoTimer",
    "selectedJobId",
    "selectedJobDetails",
    "jobLoading",
    "events",
    "eventsVisibleRows",
    "eventsFilterQuery",
    "eventsLastUpdatedUtc",
    "eventsSortIndex",
    "eventsSortDir",
    "eventsLoading",
    "eventsAutoRefreshEnabled",
    "_eventsAutoTimer",
    "apiKeys",
    "apiKeysVisibleRows",
    "apiKeysFilterQuery",
    "apiKeysLastUpdatedUtc",
    "apiKeysLoading",
    "settings",
    "settingsVisibleRows",
    "settingsFilterQuery",
    "settingsCategoryTab",
    "settingsLastUpdatedUtc",
    "settingsDrafts",
    "settingsLoading",
    "settingsAutoRefreshEnabled",
    "settingsToast",
    "_settingsAutoTimer",
    "_settingsToastTimer",
    "selectedPlaybook",
    "pbLoading",
    "pbToast",
    "pbLastUpdatedUtc",
    "pbDefaultVersion",
    "pbSelectedVersion",
    "pbVersions",
    "_ace",
    "_aceReady",
  ]);
  const CPKIT_METHODS = new Set([
    "loadExtensionHtml",
    "applyExtensionHooks",
    "applyExtensionBrand",
    "isPlainObject",
    "restoreLocalState",
    "checkAuth",
    "setAuthRequired",
    "applyAuthMetadata",
    "refreshAuthMeSnapshot",
    "loginWithSSO",
    "logout",
    "routeForView",
    "canAccessView",
    "handleForbiddenView",
    "viewLabel",
    "refreshDashboardOverview",
    "refreshJobs",
    "refreshJobStats",
    "openJob",
    "refreshSelectedJobDetails",
    "rescheduleSelectedJob",
    "jobsCellText",
    "jobsRowText",
    "sortJobs",
    "jobsSortClass",
    "applyJobsFilterSort",
    "refreshEvents",
    "eventsCellText",
    "eventsRowText",
    "sortEvents",
    "eventsSortClass",
    "applyEventsFilterSort",
    "recentEvents",
    "refreshApiKeys",
    "applyApiKeysFilterSort",
    "openApiKeyCreateModal",
    "closeApiKeyCreateModal",
    "createApiKey",
    "deleteApiKey",
    "refreshSettings",
    "settingsCategories",
    "setSettingsCategory",
    "settingDraftValue",
    "setSettingDraft",
    "applySettingsFilterSort",
    "saveSetting",
    "resetSetting",
    "showSettingsToast",
    "ensureAce",
    "applyPlaybookPayload",
    "loadPlaybookSelection",
    "onSelectPlaybookVersion",
    "savePlaybook",
    "setDefaultPlaybookVersion",
    "deletePlaybookVersion",
    "safeJson",
    "formatJson",
    "rolesText",
    "defaultApiKeyValidUntilLocal",
    "openUserInfoModal",
    "closeUserInfoModal",
  ]);
  const CPKIT_MODAL_KEYS = new Set([
    "userInfo",
    "apiKeyCreate",
    "apiKeyDeleteConfirm",
    "apiKeySecret",
    "settingResetConfirm",
    "playbookVersionDeleteConfirm",
    "jobRescheduleConfirm",
  ]);

  function loadLegacyApp() {
    const request = new XMLHttpRequest();
    request.open("GET", "/app/script.js", false);
    request.send(null);
    if (request.status < 200 || request.status >= 300) return {};

    const legacyWindow = {};
    const legacyFactory = new Function(
      "window",
      `${request.responseText}\nreturn window.app;`,
    )(legacyWindow);
    if (typeof legacyFactory !== "function") return {};
    return legacyFactory();
  }

  function splitLegacyApp(legacyApp) {
    const state = {};
    const methods = {};
    for (const [key, value] of Object.entries(legacyApp)) {
      if (typeof value === "function") {
        if (!EXCLUDED_LEGACY_METHODS.has(key) && !CPKIT_METHODS.has(key)) methods[key] = value;
      } else if (key === "modal" && value && typeof value === "object") {
        state.modal = Object.fromEntries(
          Object.entries(value).filter(([modalKey]) => !CPKIT_MODAL_KEYS.has(modalKey)),
        );
      } else if (!CPKIT_STATE_KEYS.has(key)) {
        state[key] = value;
      }
    }

    methods.ensureViewData = async function () {
      if (typeof this.ensureCurrentView === "function") {
        await this.ensureCurrentView();
      }
    };
    methods.applyRouteFromHash = function () {
      if (typeof this.applyHashRoute === "function") {
        this.applyHashRoute();
      }
    };

    return { state, methods };
  }

  function route(view, path, label, subtitle, ensure, adminOnly = false) {
    return { path, label, subtitle, ensure, adminOnly };
  }

  function ensureScript(src) {
    if ([...document.scripts].some((script) => script.src === src)) return;
    const script = document.createElement("script");
    script.src = src;
    script.defer = true;
    document.head.appendChild(script);
  }

  const legacy = splitLegacyApp(loadLegacyApp());

  window.cpkitWebappExtension = {
    htmlPath: "/app/extension.html",
    navItems: [
      { view: "clusters", label: "Clusters" },
      { view: "alerts", label: "Alerts" },
      { view: "versions", label: "CP Admin" },
    ],
    routes: {
      clusters: route("clusters", "/clusters", "Clusters", "Managed CockroachDB clusters", "ensureServersView"),
      cluster: route("cluster", "/clusters/detail", "Cluster", "Cluster details", "ensureClusterDetailView"),
      cluster_backups: route(
        "cluster_backups",
        "/clusters/backups",
        "Backups",
        "Cluster backup catalog",
        "ensureClusterBackupsView",
      ),
      cluster_artifacts: route(
        "cluster_artifacts",
        "/clusters/artifacts",
        "Artifacts",
        "Cluster artifacts",
        "ensureClusterArtifactsView",
      ),
      cluster_recovery: route(
        "cluster_recovery",
        "/clusters/recovery",
        "Recovery",
        "Cluster recovery",
        "ensureClusterRecoveryView",
      ),
      cluster_users: route(
        "cluster_users",
        "/clusters/users",
        "Users",
        "Cluster users",
        "ensureClusterUsersView",
      ),
      cluster_databases: route(
        "cluster_databases",
        "/clusters/databases",
        "Databases",
        "Cluster databases",
        "ensureClusterDatabasesView",
      ),
      cluster_dashboard: route(
        "cluster_dashboard",
        "/clusters/dashboard",
        "Cluster Dashboard",
        "Cluster metrics",
        "ensureClusterDashboardView",
      ),
      alerts: route("alerts", "/alerts", "Alerts", "Alertmanager alerts", "ensureAlertsView"),
      versions: route("versions", "/admin/versions", "Versions", "CP versions", "ensureVersionsView", true),
      node_counts: route(
        "node_counts",
        "/admin/node-counts",
        "Node Counts",
        "Cluster node count options",
        "ensureNodeCountsView",
        true,
      ),
      cpu_counts: route(
        "cpu_counts",
        "/admin/cpu-counts",
        "Node CPUs",
        "Cluster CPU options",
        "ensureCpuCountsView",
        true,
      ),
      disk_sizes: route(
        "disk_sizes",
        "/admin/disk-sizes",
        "Disk Sizes",
        "Cluster disk options",
        "ensureDiskSizesView",
        true,
      ),
      database_role_templates: route(
        "database_role_templates",
        "/admin/database-role-templates",
        "Database Role Templates",
        "Database role SQL templates",
        "ensureDatabaseRoleTemplatesView",
        true,
      ),
      regions: route("regions", "/admin/regions", "Regions", "Deployment regions", "ensureRegionsView", true),
    },
    state: legacy.state,
    methods: {
      ...legacy.methods,
      isAdminSectionView(viewName = this.view) {
        return CP_ADMIN_VIEWS.has(viewName) || ["admin", "api_keys", "settings", "playbooks"].includes(viewName);
      },
    },
    async init() {
      ensureScript("https://cdn.jsdelivr.net/npm/uplot@1.6.32/dist/uPlot.iife.min.js");
    },
  };
})();
