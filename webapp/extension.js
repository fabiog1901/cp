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
    "applyRouteFromHash",
    "isPlainObject",
    "ensureViewData",
    "restoreLocalState",
    "setManagedInterval",
    "checkAuth",
    "setAuthRequired",
    "applyAuthMetadata",
    "refreshAuthMeSnapshot",
    "loginWithSSO",
    "logout",
    "parseHashRoute",
    "routeForView",
    "setView",
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

    return { state, methods };
  }

  function route(view, path, label, subtitle, ensure, adminOnly = false, match = null) {
    const config = { path, label, subtitle, ensure, adminOnly };
    if (match) config.match = match;
    return config;
  }

  function splitPath(path) {
    return String(path || "/")
      .split("/")
      .filter(Boolean)
      .map((segment) => {
        try {
          return decodeURIComponent(segment);
        } catch (_e) {
          return segment;
        }
      });
  }

  function matchClusterPath(section = "") {
    return (path) => {
      const parts = splitPath(path);
      if (parts[0] !== "clusters" || !parts[1]) return false;
      if (!section) return parts.length === 2;
      return parts[2] === section;
    };
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
    ],
    adminItems: [
      {
        view: "versions",
        label: "Versions",
        kicker: "Cluster Versions",
        description: "Manage CockroachDB versions available for cluster operations.",
      },
      {
        view: "node_counts",
        label: "Node Counts",
        kicker: "Cluster Shape",
        description: "Manage allowed node counts for cluster sizing.",
      },
      {
        view: "cpu_counts",
        label: "Node CPUs",
        kicker: "Compute Shape",
        description: "Manage allowed CPU counts per node.",
      },
      {
        view: "disk_sizes",
        label: "Disk Sizes",
        kicker: "Storage Shape",
        description: "Manage allowed disk sizes for cluster nodes.",
      },
      {
        view: "database_role_templates",
        label: "Database Role Templates",
        kicker: "Database Access",
        description: "Manage SQL templates for generated database roles.",
      },
      {
        view: "regions",
        label: "Regions",
        kicker: "Placement",
        description: "Manage cloud regions, zones, network metadata, and images.",
      },
    ],
    routes: {
      clusters: route("clusters", "/clusters", "Clusters", "Managed CockroachDB clusters", "ensureServersView"),
      cluster: route(
        "cluster",
        "/clusters/detail",
        "Cluster",
        "Cluster details",
        "ensureClusterRouteView",
        false,
        matchClusterPath(),
      ),
      cluster_backups: route(
        "cluster_backups",
        "/clusters/backups",
        "Backups",
        "Cluster backup catalog",
        "ensureClusterBackupsRouteView",
        false,
        matchClusterPath("backups"),
      ),
      cluster_artifacts: route(
        "cluster_artifacts",
        "/clusters/artifacts",
        "Artifacts",
        "Cluster artifacts",
        "ensureClusterArtifactsRouteView",
        false,
        matchClusterPath("artifacts"),
      ),
      cluster_recovery: route(
        "cluster_recovery",
        "/clusters/recovery",
        "Recovery",
        "Cluster recovery",
        "ensureClusterRecoveryRouteView",
        false,
        matchClusterPath("recovery"),
      ),
      cluster_users: route(
        "cluster_users",
        "/clusters/users",
        "Users",
        "Cluster users",
        "ensureClusterUsersRouteView",
        false,
        matchClusterPath("users"),
      ),
      cluster_databases: route(
        "cluster_databases",
        "/clusters/databases",
        "Databases",
        "Cluster databases",
        "ensureClusterDatabasesRouteView",
        false,
        matchClusterPath("databases"),
      ),
      cluster_dashboard: route(
        "cluster_dashboard",
        "/clusters/dashboard",
        "Cluster Dashboard",
        "Cluster metrics",
        "ensureClusterDashboardRouteView",
        false,
        matchClusterPath("dashboard"),
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
      syncClusterRouteState() {
        const route =
          typeof this.parseHashRoute === "function"
            ? this.parseHashRoute()
            : { parts: [], query: {} };
        const parts = route.parts || [];
        const query = route.query || {};
        if (parts[0] !== "clusters" || !parts[1]) return;

        const nextClusterId = String(parts[1] || "").trim();
        const clusterChanged =
          nextClusterId && String(this.selectedClusterId || "").trim() !== nextClusterId;
        if (nextClusterId) {
          this.selectedClusterId = nextClusterId;
          localStorage.setItem("cp_selected_cluster_id", nextClusterId);
          this.clusterConnectCopiedFor = "";
        }
        if (clusterChanged) {
          this.selectedCluster = null;
          this.clearClusterDatabaseObjectsState();
          this.clearClusterUsersState();
          this.clusterBackups = [];
          this.clusterBackupDetails = [];
          this.clearClusterArtifactsState();
          this.clusterRecoveryBackups = [];
          this.clusterRecoveryExpanded = {};
          this.clusterRecoveryLastUpdatedUtc = null;
          this.clusterDashboardSnapshot = null;
          this.clusterDashboardChartData = [];
          this.clusterDashboardCurrentNodes = [];
        }

        if (this.view === "cluster_backups") {
          this.selectedClusterBackupPath = String(query.path || "").trim();
        } else {
          this.selectedClusterBackupPath = "";
        }

        if (this.view === "cluster_artifacts") {
          this.selectedClusterArtifactKind = String(parts[3] || "debug_zip").trim();
        }

        if (this.view === "cluster_dashboard") {
          const period = Number.parseInt(query.period, 10);
          const step = Number.parseInt(query.step, 10);
          if (Number.isFinite(period) && period > 0) this.clusterDashboardPeriodMins = period;
          if (Number.isFinite(step) && step > 0) this.clusterDashboardIntervalSecs = step;
        }

        if (this.view !== "cluster" && this.view !== "cluster_databases") {
          this.clearClusterDatabaseObjectsState();
        }
        if (this.view !== "cluster_users") {
          this.clearClusterUsersState();
        }
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
      },
      async ensureClusterRouteView() {
        this.syncClusterRouteState();
        if (this.clusterLoading.details) await this.ensureClusterDetailView();
        else await this.refreshSelectedCluster();
      },
      async ensureClusterDashboardRouteView() {
        this.syncClusterRouteState();
        if (this.clusterDashboardLoading.snapshot) await this.ensureClusterDashboardView();
        else await this.refreshClusterDashboard();
      },
      async ensureClusterUsersRouteView() {
        this.syncClusterRouteState();
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        if (this.clusterUsersLoading.snapshot) await this.ensureClusterUsersView();
        else await this.refreshClusterUsers();
      },
      async ensureClusterDatabasesRouteView() {
        this.syncClusterRouteState();
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        if (this.clusterDatabaseObjectsLoading.list) await this.ensureClusterDatabasesView();
        else await this.refreshClusterDatabaseObjects();
      },
      async ensureClusterBackupsRouteView() {
        this.syncClusterRouteState();
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        if (this.clusterBackupsLoading.snapshot) await this.ensureClusterBackupsView();
        else await this.refreshClusterBackups();
        if (this.selectedClusterBackupPath && !this.clusterBackupsLoading.details) {
          await this.refreshSelectedBackupDetails();
        }
      },
      async ensureClusterArtifactsRouteView() {
        this.syncClusterRouteState();
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        if (this.clusterArtifactsLoading.list) await this.ensureClusterArtifactsView();
        else await this.refreshClusterArtifacts();
      },
      async ensureClusterRecoveryRouteView() {
        this.syncClusterRouteState();
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        if (this.clusterRecoveryLoading.list) await this.ensureClusterRecoveryView();
        else await this.refreshClusterRecoveryBackups();
      },
      clusterHref(clusterId, suffix = "") {
        const nextId = String(clusterId || "").trim();
        if (!nextId) return "#/clusters";
        const tail = String(suffix || "").replace(/^\/+/, "");
        const path = `/clusters/${encodeURIComponent(nextId)}${tail ? `/${tail}` : ""}`;
        return `#${path}`;
      },
      setClusterHash(clusterId, suffix = "", query = null) {
        if (typeof window === "undefined") return;
        const nextId = String(clusterId || "").trim();
        if (!nextId) return;
        const tail = String(suffix || "").replace(/^\/+/, "");
        const path = `/clusters/${encodeURIComponent(nextId)}${tail ? `/${tail}` : ""}`;
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(query || {})) {
          const nextValue = String(value || "").trim();
          if (nextValue) params.set(key, nextValue);
        }
        const nextHash = `#${path}${params.toString() ? `?${params.toString()}` : ""}`;
        if (window.location.hash !== nextHash) window.location.hash = nextHash;
      },
      async openCluster(clusterId) {
        const nextId = String(clusterId || "").trim();
        if (!nextId) return;
        this.selectedClusterId = nextId;
        localStorage.setItem("cp_selected_cluster_id", nextId);
        this.clusterConnectCopiedFor = "";
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.clearClusterArtifactsState();
        this.view = "cluster";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(nextId);
        await this.refreshSelectedCluster();
      },
      async openClusterDashboard() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.view = "cluster_dashboard";
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, "dashboard", {
          period: this.clusterDashboardPeriodMins,
          step: this.clusterDashboardIntervalSecs,
        });
        await this.refreshClusterDashboard();
      },
      async openClusterUsers() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.clearClusterDatabaseObjectsState();
        this.view = "cluster_users";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, "users");
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterUsers();
      },
      async openClusterDatabases() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.clearClusterUsersState();
        this.view = "cluster_databases";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, "databases");
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterDatabaseObjects();
      },
      async openClusterBackups() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "cluster_backups";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, "backups");
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterBackups();
      },
      async openClusterDebugZips() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        this.selectedClusterArtifactKind = "debug_zip";
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "cluster_artifacts";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, `artifacts/${encodeURIComponent(this.selectedClusterArtifactKind || "debug_zip")}`);
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterArtifacts();
      },
      async openClusterRecovery() {
        const clusterId = this.selectedCluster?.cluster_id || this.selectedClusterId;
        if (!clusterId) return;
        this.selectedClusterId = String(clusterId).trim();
        localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "cluster_recovery";
        localStorage.setItem("cp_view", this.view);
        this.clearViewNotice();
        this.setClusterHash(this.selectedClusterId, "recovery");
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterRecoveryBackups();
      },
      isAdminSectionView(viewName = this.view) {
        return CP_ADMIN_VIEWS.has(viewName) || ["admin", "api_keys", "settings", "playbooks"].includes(viewName);
      },
    },
    async init() {
      ensureScript("https://cdn.jsdelivr.net/npm/uplot@1.6.32/dist/uPlot.iife.min.js");
    },
  };
})();
