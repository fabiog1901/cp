// CP cpkit webapp extension.
//
// cpkit owns the shell, auth/session UI, shared pages, notices, and API plumbing.
// This file contributes only CP-specific state, routes, views, and browser logic.

function createCPExtensionParts() {
  return {
    // CP asset helpers
    cloudLogoKeys: ["aws", "azr", "gcp", "vmw"],

    // Shared UTC timestamps

    // ---------- Servers state ----------
    servers: [],
    clusterStats: {
      total: 0,
      active: 0,
      creating: 0,
      unhealthy: 0,
      failed: 0,
    },
    serversVisibleRows: [],
    deletedServersVisibleRows: [],
    serversFilterQuery: "",
    serversLastUpdatedUtc: null,
    serversSortIndex: null,
    serversSortDir: "asc",
    serversSortTypeByIndex: {
      0: "string", // cluster_id
      1: "string", // grp
      2: "string", // created_by
      3: "string", // status
      4: "string", // version
      5: "number", // node_count
      6: "number", // node_cpus
      7: "number", // disk_size
    },
    serversLoading: { list: false, action: false },
    serversAutoRefreshEnabled: true,
    _serversAutoTimer: null,
    clusterDetailsAutoRefreshEnabled: true,
    _clusterDetailsAutoTimer: null,
    clusterDashboardAutoRefreshEnabled: true,
    _clusterDashboardAutoTimer: null,
    selectedClusterId: "",
    selectedCluster: null,
    clusterDashboardLastUpdatedUtc: null,
    clusterDashboardLoading: { snapshot: false },
    clusterDashboardPeriodMins: 30,
    clusterDashboardIntervalSecs: 10,
    clusterDashboardChartData: [],
    clusterDashboardCurrentNodes: [],
    clusterDashboardSnapshot: null,
    _clusterDashboardCharts: {},
    _suppressNextHashChange: false,
    _hashChangeHandlerRegistered: false,
    clusterLoading: {
      details: false,
      delete: false,
      healthcheck: false,
      create: false,
      upgrade: false,
      scale: false,
    },
    clusterDatabaseObjects: [],
    clusterDatabaseObjectsVisibleRows: [],
    clusterDatabaseObjectsFilterQuery: "",
    clusterDatabaseObjectsLastUpdatedUtc: null,
    clusterDatabaseObjectsAutoRefreshEnabled: true,
    _clusterDatabasesAutoTimer: null,
    clusterDatabaseObjectsLoading: {
      list: false,
      create: false,
      delete: false,
      groupMappings: false,
    },
    clusterDatabaseRoleGroupDrafts: {},
    clusterDatabaseRoleGroupSaving: {},
    clusterUsers: [],
    clusterUsersVisibleRows: [],
    clusterUsersClusterId: "",
    clusterUsersFilterQuery: "",
    clusterUsersLastUpdatedUtc: null,
    clusterUsersAutoRefreshEnabled: true,
    _clusterUsersAutoTimer: null,
    clusterUsersLoading: {
      snapshot: false,
      create: false,
      delete: false,
      password: false,
      revokeDatabaseRole: false,
      grantDatabaseRoles: false,
    },
    clusterBackups: [],
    clusterBackupDetails: [],
    selectedClusterBackupPath: "",
    clusterBackupsLastUpdatedUtc: null,
    clusterBackupsAutoRefreshEnabled: true,
    _clusterBackupsAutoTimer: null,
    clusterBackupsLoading: {
      snapshot: false,
      details: false,
      restore: false,
    },
    clusterArtifacts: [],
    clusterArtifactsVisibleRows: [],
    selectedClusterArtifactKind: "debug_zip",
    clusterArtifactsFilterQuery: "",
    clusterArtifactsLastUpdatedUtc: null,
    clusterArtifactsAutoRefreshEnabled: true,
    _clusterArtifactsAutoTimer: null,
    clusterArtifactsSortIndex: 4,
    clusterArtifactsSortDir: "desc",
    clusterArtifactsSortTypeByIndex: {
      0: "string", // artifact_name
      1: "string", // status
      2: "number", // size_bytes
      3: "string", // redacted
      4: "date", // created_at
      5: "date", // expires_at
      6: "number", // job_id
      7: "string", // sha256
    },
    clusterArtifactsLoading: {
      list: false,
      download: false,
    },
    clusterArtifactDownloadingId: "",
    clusterRecoveryBackups: [],
    clusterRecoveryExpanded: {},
    clusterRecoveryLastUpdatedUtc: null,
    clusterRecoveryAutoRefreshEnabled: true,
    _clusterRecoveryAutoTimer: null,
    clusterRecoveryLoading: {
      list: false,
      restore: false,
    },
    clusterConnectCopiedFor: "",
    clusterCreateOptions: {
      versions: [],
      node_counts: [],
      cpus_per_node: [],
      disk_sizes: [],
      regions: [],
    },

    // ---------- Alerts state ----------
    alerts: [],
    alertsVisibleRows: [],
    alertsFilterQuery: "",
    alertsLastUpdatedUtc: null,
    alertsSortIndex: 0,
    alertsSortDir: "desc",
    alertsSortTypeByIndex: {
      0: "date", // starts_at
      1: "string", // alert_type
      2: "string", // cluster
      3: "string", // nodes_text
      4: "string", // summary
      5: "date", // ends_at
      6: "date", // age
    },
    alertsLoading: { list: false },
    alertsAutoRefreshEnabled: true,
    _alertsAutoTimer: null,

    // ---------- Versions state ----------
    versions: [],
    versionsVisibleRows: [],
    versionsFilterQuery: "",
    versionsLastUpdatedUtc: null,
    versionsLoading: { list: false, create: false, delete: false },
    versionsAutoRefreshEnabled: true,
    _versionsAutoTimer: null,

    // ---------- Cluster option state ----------
    nodeCounts: [],
    nodeCountsVisibleRows: [],
    nodeCountsFilterQuery: "",
    nodeCountsLastUpdatedUtc: null,
    nodeCountsLoading: { list: false, create: false, delete: false },
    nodeCountsAutoRefreshEnabled: true,
    _nodeCountsAutoTimer: null,

    cpuCounts: [],
    cpuCountsVisibleRows: [],
    cpuCountsFilterQuery: "",
    cpuCountsLastUpdatedUtc: null,
    cpuCountsLoading: { list: false, create: false, delete: false },
    cpuCountsAutoRefreshEnabled: true,
    _cpuCountsAutoTimer: null,

    diskSizes: [],
    diskSizesVisibleRows: [],
    diskSizesFilterQuery: "",
    diskSizesLastUpdatedUtc: null,
    diskSizesLoading: { list: false, create: false, delete: false },
    diskSizesAutoRefreshEnabled: true,
    _diskSizesAutoTimer: null,

    databaseRoleTemplates: [],
    databaseRoleTemplatesVisibleRows: [],
    databaseRoleTemplatesFilterQuery: "",
    databaseRoleTemplatesLastUpdatedUtc: null,
    databaseRoleTemplatesLoading: { list: false, create: false, delete: false },
    databaseRoleTemplatesAutoRefreshEnabled: true,
    _databaseRoleTemplatesAutoTimer: null,
    databaseRoles: [],

    // ---------- Regions state ----------
    regions: [],
    regionsVisibleRows: [],
    regionsFilterQuery: "",
    regionsLastUpdatedUtc: null,
    regionsLoading: { list: false, create: false, delete: false },
    regionsAutoRefreshEnabled: true,
    _regionsAutoTimer: null,

    renderedAtUtc: "now",

    modal: {
      userInfo: { open: false },
      versionCreate: {
        open: false,
        version: "",
      },
      versionDeleteConfirm: {
        open: false,
        version: "",
      },
      nodeCountCreate: {
        open: false,
        node_count: "",
      },
      nodeCountDeleteConfirm: {
        open: false,
        node_count: "",
      },
      cpuCountCreate: {
        open: false,
        cpu_count: "",
      },
      cpuCountDeleteConfirm: {
        open: false,
        cpu_count: "",
      },
      diskSizeCreate: {
        open: false,
        size_gb: "",
      },
      diskSizeDeleteConfirm: {
        open: false,
        size_gb: "",
      },
      databaseRoleTemplateCreate: {
        open: false,
        database_role_template: "",
        scope_type: "schema",
        sql_statement: "CREATE ROLE IF NOT EXISTS {database_role};",
      },
      databaseRoleTemplateDeleteConfirm: {
        open: false,
        database_role_template: "",
      },
      regionCreate: {
        open: false,
        cloud: "",
        region: "",
        zone: "",
        vpc_id: "",
        security_groups_text: "",
        subnet: "",
        image: "",
        extras_text: "{}",
      },
      regionDeleteConfirm: {
        open: false,
        cloud: "",
        region: "",
        zone: "",
      },
      clusterDeleteConfirm: {
        open: false,
        cluster_id: "",
      },
      clusterHealthcheckConfirm: {
        open: false,
        cluster_id: "",
      },
      clusterCreate: {
        open: false,
        name: "",
        node_count: "",
        node_cpus: "",
        disk_size: "",
        regions: [],
        version: "",
        owner: "",
      },
      clusterUpgrade: {
        open: false,
        version: "",
        upgrade_versions: [],
      },
      clusterScale: {
        open: false,
        node_count: "",
        node_cpus: "",
        disk_size: "",
        regions: [],
        original: null,
        options: {
          node_counts: [],
          cpus_per_node: [],
          disk_sizes: [],
          regions: [],
        },
      },
      clusterDatabaseObjectCreate: {
        open: false,
        database_name: "",
      },
      clusterDatabaseObjectDeleteConfirm: {
        open: false,
        database_name: "",
      },
      clusterBackupObjectRestore: {
        open: false,
        row: null,
        object_type: "",
        object_name: "",
        backup_path: "",
        restore_aost: "",
        use_restore_option: false,
        into_db: "",
        new_db_name: "",
      },
      clusterRecoveryRestoreConfirm: {
        open: false,
        source_cluster_id: "",
        backup_path: "",
        restore_aost: "",
        start_time: "",
      },
      clusterUserCreate: {
        open: false,
        username: "",
        password: "",
        database_roles: [],
      },
      clusterUserDeleteConfirm: {
        open: false,
        username: "",
      },
      clusterUserPassword: {
        open: false,
        username: "",
        password: "",
      },
      clusterUserRoles: {
        open: false,
        username: "",
        databaseRoles: [],
        grantDatabaseRoles: [],
      },
    },
    modalErrors: {
      versionCreate: "",
      versionDeleteConfirm: "",
      nodeCountCreate: "",
      nodeCountDeleteConfirm: "",
      cpuCountCreate: "",
      cpuCountDeleteConfirm: "",
      diskSizeCreate: "",
      diskSizeDeleteConfirm: "",
      databaseRoleTemplateCreate: "",
      databaseRoleTemplateDeleteConfirm: "",
      regionCreate: "",
      regionDeleteConfirm: "",
      clusterDeleteConfirm: "",
      clusterHealthcheckConfirm: "",
      clusterCreate: "",
      clusterUpgrade: "",
      clusterScale: "",
      clusterDatabaseObjectCreate: "",
      clusterDatabaseObjectDeleteConfirm: "",
      clusterBackupObjectRestore: "",
      clusterRecoveryRestoreConfirm: "",
      clusterUserCreate: "",
      clusterUserDeleteConfirm: "",
      clusterUserPassword: "",
      clusterUserRoles: "",
    },
    // Ace


    _databaseRoleTemplateAce: null,
    _databaseRoleTemplateAceReady: false,

    clusterDashboardPalette: [
      "#1f77b4",
      "#ff7f0e",
      "#2ca02c",
      "#d62728",
      "#9467bd",
      "#8c564b",
      "#e377c2",
      "#7f7f7f",
      "#bcbd22",
      "#17becf",
      "#393b79",
      "#637939",
      "#8c6d31",
      "#843c39",
      "#7b4173",
      "#3182bd",
      "#31a354",
      "#756bb1",
      "#636363",
      "#969696",
    ],

    // ---------- UTC helpers ----------
    funnyWords: [
      "abracadabra",
      "amazeballs",
      "arglebargle",
      "awesomesauce",
      "balderdash",
      "bamboozle",
      "bazinga",
      "brouhaha",
      "bubblegum",
      "buckaroo",
      "bumfuzzle",
      "cacophony",
      "catawampus",
      "chortle",
      "codswallop",
      "collywobbles",
      "defenestrate",
      "dillydally",
      "dingbat",
      "doohickey",
      "flabbergasted",
      "flapdoodle",
      "flibbertigibbet",
      "flummox",
      "folderol",
      "gadzooks",
      "gobbledygook",
      "goofball",
      "hocuspocus",
      "hodgepodge",
      "hootenanny",
      "hornswoggle",
      "hullabaloo",
      "humdinger",
      "jabberwocky",
      "jamboree",
      "kerfuffle",
      "knickknack",
      "kookaburra",
      "lollygag",
      "malarkey",
      "mumbojumbo",
      "nincompoop",
      "poppycock",
      "rigmarole",
      "skedaddle",
      "thingamabob",
      "whatchamacallit",
      "whimsy",
      "widdershins",
      "wonky",
      "yippee",
      "zoinks",
    ],

    getFunnyName() {
      const pick = () =>
        this.funnyWords[Math.floor(Math.random() * this.funnyWords.length)];
      return `${pick()}-${pick()}`;
    },

    getHumanSize(valueInGb) {
      const suffixes = [
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
      ];
      const base = 1000;
      const bytes = Number(valueInGb) * 1_000_000_000;

      if (!Number.isFinite(bytes) || bytes <= 0) {
        return `0 ${suffixes[0]}`;
      }

      const exponent = Math.min(
        Math.floor(Math.log(bytes) / Math.log(base)),
        suffixes.length - 1,
      );
      const scaled = bytes / base ** exponent;
      const rounded = scaled.toFixed(1);

      if (rounded.endsWith(".0")) {
        return `${rounded.slice(0, -2)} ${suffixes[exponent]}`;
      }
      return `${rounded} ${suffixes[exponent]}`;
    },

    cloudKeyFromRegion(regionId) {
      return String(regionId || "")
        .trim()
        .slice(0, 3)
        .toLowerCase();
    },

    cloudKey(value) {
      return String(value || "")
        .trim()
        .slice(0, 3)
        .toLowerCase();
    },

    appStaticAsset(path) {
      const assetPath = String(path || "").trim().replace(/^\/+/, "");
      return assetPath ? `/app/static/${assetPath}` : "";
    },

    cloudLogoForCloud(cloud) {
      const cloudKey = this.cloudKey(cloud);
      return this.cloudLogoKeys?.includes(cloudKey)
        ? this.appStaticAsset(`${cloudKey}.png`)
        : "";
    },

    cloudLogoForRegion(regionId) {
      return this.cloudLogoForCloud(this.cloudKeyFromRegion(regionId));
    },

    regionLabel(regionId) {
      const raw = String(regionId || "").trim();
      if (!raw) return "-";
      return raw.includes(":") ? raw.split(":").slice(1).join(":") : raw;
    },

    alertClusterCount() {
      return new Set(
        this.alerts
          .map((alert) => String(alert?.cluster || "").trim())
          .filter(Boolean),
      ).size;
    },

    alertNodeCount() {
      return new Set(
        this.alerts.flatMap((alert) =>
          Array.isArray(alert?.nodes)
            ? alert.nodes.map((node) => String(node || "").trim()).filter(Boolean)
            : [],
        ),
      ).size;
    },

    dashboardClusterCount(kind) {
      return Number(this.clusterStats?.[kind] || 0);
    },


    dashboardNeedsAttentionCount() {
      return (
        this.dashboardClusterCount("unhealthy") +
        this.dashboardClusterCount("failed") +
        this.alerts.length
      );
    },

    recentAlerts(limit = 10) {
      return this.alerts
        .slice()
        .sort((a, b) => this.parseValue("date", b?.ts) - this.parseValue("date", a?.ts))
        .slice(0, limit);
    },

    alertStatusClass(alert) {
      return alert?.ends_at ? "status-muted" : "status-offline";
    },

    alertNodesText(alert) {
      return Array.isArray(alert?.nodes) && alert.nodes.length
        ? alert.nodes.join(", ")
        : "-";
    },

    normalizeAlertTimestamp(value) {
      if (!value) return null;
      const raw = String(value).trim();
      if (!raw) return null;
      if (raw.startsWith("0001-01-01")) return null;

      const parsed = new Date(raw);
      if (isNaN(parsed.getTime())) return value;
      if (parsed.getUTCFullYear() <= 1) return null;
      return value;
    },

    normalizeAlertRow(alert) {
      return {
        ...alert,
        alert_id:
          alert?.fingerprint || `${alert?.alert_type || "alert"}-${alert?.starts_at || ""}`,
        ts: alert?.starts_at || null,
        ends_at: this.normalizeAlertTimestamp(alert?.ends_at),
        nodes: Array.isArray(alert?.nodes) ? alert.nodes : [],
        nodes_text: this.alertNodesText(alert),
        summary: alert?.summary || alert?.alert_type || "-",
        description: alert?.description || "-",
      };
    },

    actionPillStyle(action) {
      const name = String(action || "")
        .trim()
        .toUpperCase();
      const palette = [
        {
          background: "rgba(30, 64, 175, 0.92)",
          borderColor: "rgba(147, 197, 253, 0.55)",
          color: "#eff6ff",
        },
        {
          background: "rgba(154, 52, 18, 0.92)",
          borderColor: "rgba(253, 186, 116, 0.55)",
          color: "#fff7ed",
        },
        {
          background: "rgba(6, 95, 70, 0.92)",
          borderColor: "rgba(110, 231, 183, 0.5)",
          color: "#ecfdf5",
        },
        {
          background: "rgba(91, 33, 182, 0.92)",
          borderColor: "rgba(196, 181, 253, 0.5)",
          color: "#f5f3ff",
        },
        {
          background: "rgba(190, 24, 93, 0.92)",
          borderColor: "rgba(251, 182, 206, 0.5)",
          color: "#fff1f2",
        },
        {
          background: "rgba(15, 23, 42, 0.96)",
          borderColor: "rgba(148, 163, 184, 0.45)",
          color: "#e5e7eb",
        },
        {
          background: "rgba(20, 83, 45, 0.92)",
          borderColor: "rgba(134, 239, 172, 0.45)",
          color: "#f0fdf4",
        },
        {
          background: "rgba(127, 29, 29, 0.92)",
          borderColor: "rgba(252, 165, 165, 0.45)",
          color: "#fef2f2",
        },
      ];

      const preferred = [
        {
          match: ["LOGIN", "_LOGIN"],
          style: palette[0],
        },
        {
          match: ["LOGOUT", "_LOGOUT"],
          style: palette[5],
        },
        {
          match: ["ALLOCATE", "ALLOCATION"],
          style: palette[1],
        },
        {
          match: ["DEALLOCATE", "DEALLOCATION"],
          style: palette[3],
        },
        {
          match: ["INIT", "CREATE"],
          style: palette[2],
        },
        {
          match: ["DECOMM", "DELETE", "REMOVE"],
          style: palette[7],
        },
        {
          match: ["UPDATE", "PATCH"],
          style: palette[4],
        },
      ];

      for (const entry of preferred) {
        if (entry.match.some((token) => name.includes(token))) {
          return entry.style;
        }
      }

      let hash = 0;
      for (let i = 0; i < name.length; i += 1) {
        hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
      }
      return palette[hash % palette.length];
    },

    alertTypePillStyle(alertType) {
      return this.actionPillStyle(alertType);
    },

    clearModalError(modalName) {
      if (!modalName) return;
      this.modalErrors[modalName] = "";
    },

    setModalError(modalName, err, fallback = "Request failed.") {
      this.modalErrors[modalName] = this.errorMessage(err, fallback);
    },

    // ---------- CP refresh lifecycle ----------
    stopAutoRefreshTimers() {
      if (typeof window !== "undefined" && window.__cpAutoRefreshTimers) {
        Object.values(window.__cpAutoRefreshTimers).forEach((timerId) => {
          clearInterval(timerId);
        });
        window.__cpAutoRefreshTimers = {};
      }
      if (this._serversAutoTimer) {
        clearInterval(this._serversAutoTimer);
        this._serversAutoTimer = null;
      }
      if (this._clusterDetailsAutoTimer) {
        clearInterval(this._clusterDetailsAutoTimer);
        this._clusterDetailsAutoTimer = null;
      }
      if (this._clusterDashboardAutoTimer) {
        clearInterval(this._clusterDashboardAutoTimer);
        this._clusterDashboardAutoTimer = null;
      }
      if (this._clusterUsersAutoTimer) {
        clearInterval(this._clusterUsersAutoTimer);
        this._clusterUsersAutoTimer = null;
      }
      if (this._clusterDatabasesAutoTimer) {
        clearInterval(this._clusterDatabasesAutoTimer);
        this._clusterDatabasesAutoTimer = null;
      }
      if (this._clusterBackupsAutoTimer) {
        clearInterval(this._clusterBackupsAutoTimer);
        this._clusterBackupsAutoTimer = null;
      }
      if (this._clusterArtifactsAutoTimer) {
        clearInterval(this._clusterArtifactsAutoTimer);
        this._clusterArtifactsAutoTimer = null;
      }
      if (this._alertsAutoTimer) {
        clearInterval(this._alertsAutoTimer);
        this._alertsAutoTimer = null;
      }
      if (this._versionsAutoTimer) {
        clearInterval(this._versionsAutoTimer);
        this._versionsAutoTimer = null;
      }
      if (this._nodeCountsAutoTimer) {
        clearInterval(this._nodeCountsAutoTimer);
        this._nodeCountsAutoTimer = null;
      }
      if (this._cpuCountsAutoTimer) {
        clearInterval(this._cpuCountsAutoTimer);
        this._cpuCountsAutoTimer = null;
      }
      if (this._diskSizesAutoTimer) {
        clearInterval(this._diskSizesAutoTimer);
        this._diskSizesAutoTimer = null;
      }
      if (this._regionsAutoTimer) {
        clearInterval(this._regionsAutoTimer);
        this._regionsAutoTimer = null;
      }
      this.destroyClusterDashboardCharts();
    },

    clusterOwnerGroups() {
      return typeof this.authGroups === "function" ? this.authGroups() : [];
    },

    canManageCompute() {
      return (
        typeof this.hasRole === "function" &&
        (this.hasRole("CP_USER") || this.hasRole("CP_ADMIN"))
      );
    },

    buildPath(path, params = {}) {
      const qs = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value === null || value === undefined || value === "") return;
        if (Array.isArray(value)) {
          value.forEach((entry) => {
            if (entry !== null && entry !== undefined && entry !== "") {
              qs.append(key, String(entry));
            }
          });
          return;
        }
        qs.set(key, String(value));
      });
      const query = qs.toString();
      return query ? `${path}?${query}` : path;
    },

    visibilityPath(path, extra = {}) {
      return this.buildPath(path, extra);
    },

    routeHash(path, params = {}) {
      return `#${this.buildPath(path, params)}`;
    },

    currentRouteHash() {
      if (typeof window === "undefined") return "";
      return String(window.location.hash || "").trim();
    },

    parseCurrentHashRoute() {
      if (typeof window === "undefined") {
        return { hasHash: false, parts: [], query: {}, path: "/" };
      }

      const rawHash = String(window.location.hash || "").trim();
      if (!rawHash) {
        return { hasHash: false, parts: [], query: {}, path: "/" };
      }

      const fragment = rawHash.startsWith("#") ? rawHash.slice(1) : rawHash;
      const normalized = fragment.startsWith("/") ? fragment : `/${fragment}`;
      const [pathPart, queryString = ""] = normalized.split("?");
      const parts = pathPart
        .split("/")
        .filter(Boolean)
        .map((segment) => {
          try {
            return decodeURIComponent(segment);
          } catch (_e) {
            return segment;
          }
        });
      const query = {};
      const params = new URLSearchParams(queryString);
      params.forEach((value, key) => {
        query[key] = value;
      });

      return {
        hasHash: true,
        path: pathPart || "/",
        parts,
        query,
      };
    },

    routeHashForState() {
      switch (this.view) {
        case "dashboard":
          return this.routeHash("/dashboard");
        case "clusters":
          return this.routeHash("/clusters");
        case "cluster":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}`,
              )
            : this.routeHash("/clusters");
        case "cluster_dashboard":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/dashboard`,
                {
                  period: this.clusterDashboardPeriodMins,
                  step: this.clusterDashboardIntervalSecs,
                },
              )
            : this.routeHash("/clusters");
        case "cluster_users":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/users`,
              )
            : this.routeHash("/clusters");
        case "cluster_databases":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/databases`,
              )
            : this.routeHash("/clusters");
        case "cluster_backups":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/backups`,
                { path: this.selectedClusterBackupPath },
              )
            : this.routeHash("/clusters");
        case "cluster_artifacts":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/artifacts/${encodeURIComponent(this.selectedClusterArtifactKind || "debug_zip")}`,
              )
            : this.routeHash("/clusters");
        case "cluster_recovery":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/recovery`,
              )
            : this.routeHash("/clusters");
        case "alerts":
          return this.routeHash("/alerts");
        case "admin":
          return this.routeHash("/admin");
        case "versions":
          return this.routeHash("/admin/versions");
        case "node_counts":
          return this.routeHash("/admin/node-counts");
        case "cpu_counts":
          return this.routeHash("/admin/cpu-counts");
        case "disk_sizes":
          return this.routeHash("/admin/disk-sizes");
        case "database_role_templates":
          return this.routeHash("/admin/database-role-templates");
        case "regions":
          return this.routeHash("/admin/regions");
        default:
          return this.routeHash("/dashboard");
      }
    },

    syncHashFromState(replace = false) {
      if (typeof window === "undefined") return;

      const nextHash = this.routeHashForState();
      const currentHash = this.currentRouteHash();
      if (!nextHash || currentHash === nextHash) return;

      if (replace) {
        const nextUrl = `${window.location.pathname}${window.location.search}${nextHash}`;
        window.history.replaceState(null, "", nextUrl);
        return;
      }

      this._suppressNextHashChange = true;
      window.location.hash = nextHash.slice(1);
    },

    unauthorizedViewMessage(viewName = this.view) {
      const labels = {
        clusters: "Clusters",
        alerts: "Alerts",
        admin: "Admin",
        versions: "Versions",
        node_counts: "Node Counts",
        cpu_counts: "Node CPUs",
        disk_sizes: "Disk Sizes",
        database_role_templates: "Database Role Templates",
        regions: "Regions",
      };
      const label = labels[viewName] || "This view";
      return `${label} is available only to admin users.`;
    },

    // ---------- Servers lifecycle ----------
    async ensureServersView() {
      if (!this.serversLoading.list) await this.refreshServers();
      else this.applyServersFilterSort();
    },

    async ensureClusterDetailView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      else if (
        !this.clusterDatabaseObjectsLoading.list &&
        !this.clusterDatabaseObjectsLastUpdatedUtc
      ) {
        await this.refreshClusterDatabaseObjects();
      }
    },

    async ensureClusterDashboardView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterDashboardLoading.snapshot) {
        await this.refreshClusterDashboard();
        return;
      }
      this.renderClusterDashboardCharts();
    },

    async ensureClusterUsersView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      if (!this.clusterUsersLoading.snapshot) await this.refreshClusterUsers();
      else this.applyClusterUsersFilter();
    },

    async ensureClusterDatabasesView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      if (
        !this.clusterDatabaseObjectsLoading.list &&
        !this.clusterDatabaseObjectsLastUpdatedUtc
      )
        await this.refreshClusterDatabaseObjects();
      else this.applyClusterDatabaseObjectsFilter();
    },

    async ensureClusterBackupsView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      if (!this.clusterBackupsLoading.snapshot) {
        await this.refreshClusterBackups();
      } else if (!this.clusterBackupsLoading.details) {
        if (this.selectedClusterBackupPath) await this.refreshSelectedBackupDetails();
      }
    },

    async ensureClusterArtifactsView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.clearClusterArtifactsState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      if (!this.clusterArtifactsLoading.list) await this.refreshClusterArtifacts();
      else this.applyClusterArtifactsFilterSort();
    },

    async ensureClusterRecoveryView() {
      if (!this.selectedClusterId) {
        this.clearClusterDatabaseObjectsState();
        this.clearClusterUsersState();
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (!this.clusterLoading.details) await this.refreshSelectedCluster();
      if (!this.clusterRecoveryLoading.list) {
        await this.refreshClusterRecoveryBackups();
      }
    },




    async ensureAlertsView() {
      if (!this.alertsLoading.list) await this.refreshAlerts();
      else this.applyAlertsFilterSort();
    },

    async ensureCPDashboard() {
      await Promise.all([
        this.refreshClusterStats(),
        this.refreshAlerts({ limit: 10 }),
      ]);
    },



    async ensureVersionsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("versions", { fallback: false });
        return;
      }
      if (!this.versionsLoading.list) await this.refreshVersions();
      else this.applyVersionsFilter();
    },

    async ensureNodeCountsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("node_counts", { fallback: false });
        return;
      }
      if (!this.nodeCountsLoading.list) await this.refreshNodeCounts();
      else this.applyNodeCountsFilter();
    },

    async ensureCpuCountsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("cpu_counts", { fallback: false });
        return;
      }
      if (!this.cpuCountsLoading.list) await this.refreshCpuCounts();
      else this.applyCpuCountsFilter();
    },

    async ensureDiskSizesView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("disk_sizes", { fallback: false });
        return;
      }
      if (!this.diskSizesLoading.list) await this.refreshDiskSizes();
      else this.applyDiskSizesFilter();
    },

    async ensureDatabaseRoleTemplatesView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("database_role_templates", { fallback: false });
        return;
      }
      if (!this.databaseRoleTemplatesLoading.list) await this.refreshDatabaseRoleTemplates();
      else this.applyDatabaseRoleTemplatesFilter();
    },

    async ensureRegionsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("regions", { fallback: false });
        return;
      }
      if (!this.regionsLoading.list) await this.refreshRegions();
      else this.applyRegionsFilter();
    },

    serversRowText(s) {
      return [
        s.cluster_id,
        s.grp,
        s.created_by,
        s.status,
        s.version,
        s.node_count,
        s.node_cpus,
        s.disk_size,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    serversCellText(s, colIndex) {
      switch (colIndex) {
        case 0:
          return s.cluster_id || "";
        case 1:
          return s.grp || "";
        case 2:
          return s.created_by || "";
        case 3:
          return s.status || "";
        case 4:
          return s.version || "";
        case 5:
          return s.node_count ?? "";
        case 6:
          return s.node_cpus ?? "";
        case 7:
          return s.disk_size ?? "";
        default:
          return "";
      }
    },

    isDeletedCluster(row) {
      return String(row?.status || "").trim().toLowerCase() === "deleted";
    },

    sortServerRows(rows) {
      const sortedRows = rows.slice();
      if (this.serversSortIndex === null) return sortedRows;

      const type =
        this.serversSortTypeByIndex[this.serversSortIndex] || "string";
      const idx = this.serversSortIndex;
      const dir = this.serversSortDir;

      sortedRows.sort((a, b) => {
        const av = this.parseValue(type, this.serversCellText(a, idx));
        const bv = this.parseValue(type, this.serversCellText(b, idx));
        if (av < bv) return dir === "asc" ? -1 : 1;
        if (av > bv) return dir === "asc" ? 1 : -1;
        return 0;
      });

      return sortedRows;
    },

    serversStatusClass(status) {
      const s = String(status || "").toLowerCase();

      if (!s || s === "unknown") return "status-muted";

      // Async operation states
      if (s === "completed") return "status-online";
      if (s === "running") return "status-warning";
      if (s === "queued") return "status-pending status-pulse";
      if (s === "failed") return "status-offline";

      // Cluster states
      if (s === "ready" || s === "active") return "status-online";
      if (
        ["creating", "scaling", "upgrading", "restoring", "deleting"].includes(
          s,
        )
      )
        return "status-pending status-pulse";
      if (s === "decommissioned" || s === "deleted") return "status-muted";
      if (
        [
          "unhealthy",
          "create_failed",
          "scale_failed",
          "restore_failed",
          "delete_failed",
          "upgrade_failed",
        ].includes(s)
      )
        return "status-offline";

      // Fallback heuristic
      if (s.includes("ing")) return "status-pending status-pulse";

      return "status-default";
    },

    serversSortClass(index) {
      if (this.serversSortIndex !== index) return "";
      return this.serversSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleServersSort(index) {
      if (this.serversSortIndex === index)
        this.serversSortDir = this.serversSortDir === "asc" ? "desc" : "asc";
      else {
        this.serversSortIndex = index;
        this.serversSortDir = "asc";
      }

      localStorage.setItem(
        "cp_servers_sort_index",
        String(this.serversSortIndex),
      );
      localStorage.setItem("cp_servers_sort_dir", this.serversSortDir);
      this.applyServersFilterSort();
    },

    applyServersFilterSort() {
      const q = (this.serversFilterQuery || "").toLowerCase().trim();
      let rows = this.servers.slice();
      if (q) rows = rows.filter((s) => this.serversRowText(s).includes(q));

      this.serversVisibleRows = this.sortServerRows(
        rows.filter((row) => !this.isDeletedCluster(row)),
      );
      this.deletedServersVisibleRows = this.sortServerRows(
        rows.filter((row) => this.isDeletedCluster(row)),
      );
    },

    async refreshServers() {
      this.serversLoading.list = true;
      try {
        const data = await this.apiFetch(this.visibilityPath("/clusters/"), {
          method: "GET",
        });
        this.servers = Array.isArray(data) ? data : [];
        this.serversLastUpdatedUtc = this.utcNowString();
        this.applyServersFilterSort();
      } catch (e) {
        console.error(e);
        this.serversLastUpdatedUtc = this.utcNowString();
      } finally {
        this.serversLoading.list = false;
      }
    },

    async refreshClusterStats() {
      this.serversLoading.list = true;
      try {
        const data = await this.apiFetch(this.visibilityPath("/clusters/stats"), {
          method: "GET",
        });
        this.clusterStats = {
          total: Number(data?.total || 0),
          active: Number(data?.active || 0),
          creating: Number(data?.creating || 0),
          unhealthy: Number(data?.unhealthy || 0),
          failed: Number(data?.failed || 0),
        };
        this.serversLastUpdatedUtc = this.utcNowString();
      } catch (e) {
        console.error(e);
        this.serversLastUpdatedUtc = this.utcNowString();
      } finally {
        this.serversLoading.list = false;
      }
    },

    clusterCreateRegionOptions() {
      return Array.isArray(this.clusterCreateOptions?.regions)
        ? this.clusterCreateOptions.regions
        : [];
    },

    clusterCreateAvailableRegions() {
      return this.clusterCreateRegionOptions().filter(
        (region) => !this.clusterCreateHasRegion(region?.region_id),
      );
    },

    clusterCreateSelectedRegions() {
      return Array.isArray(this.modal.clusterCreate.regions)
        ? this.modal.clusterCreate.regions
        : [];
    },

    clusterCreateHasRegion(regionId) {
      return this.clusterCreateSelectedRegions().includes(
        String(regionId || ""),
      );
    },

    addClusterCreateRegion(regionId) {
      const normalized = String(regionId || "").trim();
      if (!normalized || this.clusterCreateHasRegion(normalized)) return;
      this.modal.clusterCreate.regions = [
        ...this.clusterCreateSelectedRegions(),
        normalized,
      ];
    },

    removeClusterCreateRegion(regionId) {
      const normalized = String(regionId || "").trim();
      this.modal.clusterCreate.regions =
        this.clusterCreateSelectedRegions().filter(
          (entry) => entry !== normalized,
        );
    },

    toggleClusterCreateRegion(regionId) {
      if (this.clusterCreateHasRegion(regionId)) {
        this.removeClusterCreateRegion(regionId);
        return;
      }
      this.addClusterCreateRegion(regionId);
    },

    clusterCreateDiskSizeLabel(sizeValue) {
      const size = Number(sizeValue);
      if (!Number.isFinite(size) || size <= 0) return "-";
      return `${size} GB`;
    },

    fullRegionId(cloud, region) {
      const normalizedCloud = String(cloud || "").trim();
      const normalizedRegion = String(region || "").trim();
      if (!normalizedRegion) return "";
      if (normalizedRegion.includes(":")) return normalizedRegion;
      return normalizedCloud
        ? `${normalizedCloud}:${normalizedRegion}`
        : normalizedRegion;
    },

    normalizeRegionIds(regionIds, regionOptions = []) {
      const optionMap = new Map(
        (Array.isArray(regionOptions) ? regionOptions : [])
          .map((entry) => String(entry?.region_id || "").trim())
          .filter(Boolean)
          .flatMap((regionId) => {
            const shortRegion = regionId.includes(":")
              ? regionId.split(":").slice(1).join(":")
              : regionId;
            return [
              [regionId, regionId],
              [shortRegion, regionId],
            ];
          }),
      );

      return [
        ...new Set(
          (Array.isArray(regionIds) ? regionIds : [])
            .map((regionId) => String(regionId || "").trim())
            .filter(Boolean)
            .map((regionId) => optionMap.get(regionId) || regionId),
        ),
      ];
    },

    clusterRegionIdsFromCluster(cluster = this.selectedCluster) {
      const inventory = Array.isArray(cluster?.cluster_inventory)
        ? cluster.cluster_inventory
        : [];
      return [
        ...new Set(
          inventory
            .map((entry) => this.fullRegionId(entry?.cloud, entry?.region))
            .filter(Boolean),
        ),
      ];
    },

    clusterScaleRegionOptions() {
      return Array.isArray(this.modal.clusterScale.options?.regions)
        ? this.modal.clusterScale.options.regions
        : [];
    },

    clusterScaleSelectedRegions() {
      return Array.isArray(this.modal.clusterScale.regions)
        ? this.modal.clusterScale.regions
        : [];
    },

    clusterScaleHasRegion(regionId) {
      return this.clusterScaleSelectedRegions().includes(
        String(regionId || ""),
      );
    },

    clusterScaleAvailableRegions() {
      return this.clusterScaleRegionOptions().filter(
        (region) => !this.clusterScaleHasRegion(region?.region_id),
      );
    },

    addClusterScaleRegion(regionId) {
      const normalized = String(regionId || "").trim();
      if (!normalized || this.clusterScaleHasRegion(normalized)) return;
      this.modal.clusterScale.regions = [
        ...this.clusterScaleSelectedRegions(),
        normalized,
      ];
    },

    removeClusterScaleRegion(regionId) {
      const normalized = String(regionId || "").trim();
      this.modal.clusterScale.regions =
        this.clusterScaleSelectedRegions().filter(
          (entry) => entry !== normalized,
        );
    },

    clusterScaleOriginalState() {
      return this.modal.clusterScale.original;
    },

    clusterScaleResetToOriginal() {
      const original = this.clusterScaleOriginalState();
      if (!original) return;
      this.modal.clusterScale.node_count = String(original.node_count);
      this.modal.clusterScale.node_cpus = String(original.node_cpus);
      this.modal.clusterScale.disk_size = String(original.disk_size);
      this.modal.clusterScale.regions = [...original.regions];
      this.clearModalError("clusterScale");
    },

    clusterScaleChanges() {
      const original = this.clusterScaleOriginalState();
      if (!original) return [];

      const changes = [];
      const nodeCount = Number(this.modal.clusterScale.node_count);
      const nodeCpus = Number(this.modal.clusterScale.node_cpus);
      const diskSize = Number(this.modal.clusterScale.disk_size);
      const selectedRegions = this.clusterScaleSelectedRegions();
      const originalRegions = Array.isArray(original.regions)
        ? original.regions
        : [];

      if (nodeCount !== Number(original.node_count)) {
        changes.push({
          label: "Node Count",
          from: String(original.node_count),
          to: String(nodeCount),
        });
      }
      if (nodeCpus !== Number(original.node_cpus)) {
        changes.push({
          label: "Node vCPUs",
          from: String(original.node_cpus),
          to: String(nodeCpus),
        });
      }
      if (diskSize !== Number(original.disk_size)) {
        changes.push({
          label: "Disk Size",
          from: this.clusterCreateDiskSizeLabel(original.disk_size),
          to: this.clusterCreateDiskSizeLabel(diskSize),
        });
      }

      const addedRegions = selectedRegions.filter(
        (region) => !originalRegions.includes(region),
      );
      const removedRegions = originalRegions.filter(
        (region) => !selectedRegions.includes(region),
      );

      if (addedRegions.length > 0) {
        changes.push({
          label: "Regions Added",
          from: "-",
          to: addedRegions.join(", "),
        });
      }
      if (removedRegions.length > 0) {
        changes.push({
          label: "Regions Removed",
          from: removedRegions.join(", "),
          to: "-",
        });
      }

      return changes;
    },

    refreshClusterCreateName() {
      this.modal.clusterCreate.name = this.getFunnyName();
    },

    async loadClusterCreateOptions() {
      this.clusterLoading.create = true;
      this.clearModalError("clusterCreate");
      try {
        const data = await this.apiFetch("/clusters/options", {
          method: "GET",
        });
        this.clusterCreateOptions = {
          versions: Array.isArray(data?.versions) ? data.versions : [],
          node_counts: Array.isArray(data?.node_counts) ? data.node_counts : [],
          cpus_per_node: Array.isArray(data?.cpus_per_node)
            ? data.cpus_per_node
            : [],
          disk_sizes: Array.isArray(data?.disk_sizes) ? data.disk_sizes : [],
          regions: Array.isArray(data?.regions) ? data.regions : [],
        };
      } catch (e) {
        this.setModalError(
          "clusterCreate",
          e,
          "Failed to load cluster create options.",
        );
      } finally {
        this.clusterLoading.create = false;
      }
    },

    async openClusterCreateModal() {
      this.clearModalError("clusterCreate");
      this.modal.clusterCreate.open = true;
      await this.loadClusterCreateOptions();

      const ownerGroups = this.clusterOwnerGroups();
      const nodeCounts = this.clusterCreateOptions.node_counts || [];
      const cpuOptions = this.clusterCreateOptions.cpus_per_node || [];
      const diskSizes = this.clusterCreateOptions.disk_sizes || [];
      const versionOptions = this.clusterCreateOptions.versions || [];
      const regionOptions = this.clusterCreateRegionOptions();

      this.refreshClusterCreateName();
      this.modal.clusterCreate.node_count = nodeCounts.length
        ? String(nodeCounts[0])
        : "";
      this.modal.clusterCreate.node_cpus = cpuOptions.length
        ? String(cpuOptions[0])
        : "";
      this.modal.clusterCreate.disk_size = diskSizes.length
        ? String(diskSizes[0])
        : "";
      this.modal.clusterCreate.version = versionOptions.length
        ? String(versionOptions[0])
        : "";
      this.modal.clusterCreate.regions = [];
      this.modal.clusterCreate.owner = ownerGroups.length ? ownerGroups[0] : "";

      if (ownerGroups.length === 0 && !this.modalErrors.clusterCreate) {
        this.modalErrors.clusterCreate =
          "No eligible owner groups were found in your CP role mappings.";
      }
    },

    closeClusterCreateModal() {
      this.modal.clusterCreate.open = false;
      this.modal.clusterCreate.name = "";
      this.modal.clusterCreate.node_count = "";
      this.modal.clusterCreate.node_cpus = "";
      this.modal.clusterCreate.disk_size = "";
      this.modal.clusterCreate.regions = [];
      this.modal.clusterCreate.version = "";
      this.modal.clusterCreate.owner = "";
      this.clearModalError("clusterCreate");
    },

    async createCluster() {
      const name = String(this.modal.clusterCreate.name || "").trim();
      const nodeCount = Number(this.modal.clusterCreate.node_count);
      const nodeCpus = Number(this.modal.clusterCreate.node_cpus);
      const diskSize = Number(this.modal.clusterCreate.disk_size);
      const regions = this.normalizeRegionIds(
        this.clusterCreateSelectedRegions(),
        this.clusterCreateRegionOptions(),
      );
      const version = String(this.modal.clusterCreate.version || "").trim();
      const owner = String(this.modal.clusterCreate.owner || "").trim();

      if (!name) {
        this.setModalError(
          "clusterCreate",
          new Error("Cluster name is required."),
          "Cluster name is required.",
        );
        return;
      }
      if (!Number.isFinite(nodeCount) || nodeCount <= 0) {
        this.setModalError(
          "clusterCreate",
          new Error("Node count is required."),
          "Node count is required.",
        );
        return;
      }
      if (!Number.isFinite(nodeCpus) || nodeCpus <= 0) {
        this.setModalError(
          "clusterCreate",
          new Error("Node vCPUs is required."),
          "Node vCPUs is required.",
        );
        return;
      }
      if (!version || !owner) {
        this.setModalError(
          "clusterCreate",
          new Error("Complete all cluster fields before submitting."),
          "Complete all cluster fields before submitting.",
        );
        return;
      }
      if (regions.length === 0) {
        this.setModalError(
          "clusterCreate",
          new Error("Select at least one region."),
          "Select at least one region.",
        );
        return;
      }
      if (regions.length * nodeCount < 3) {
        this.setModalError(
          "clusterCreate",
          new Error(
            "Selected regions multiplied by node count must be at least 3.",
          ),
          "Selected regions multiplied by node count must be at least 3.",
        );
        return;
      }
      if (!Number.isFinite(diskSize) || diskSize <= 0) {
        this.setModalError(
          "clusterCreate",
          new Error("Disk size is required."),
          "Disk size is required.",
        );
        return;
      }

      this.clusterLoading.create = true;
      this.clearModalError("clusterCreate");
      try {
        const result = await this.apiFetch("/clusters/", {
          method: "POST",
          body: {
            name,
            node_count: nodeCount,
            node_cpus: nodeCpus,
            disk_size: diskSize,
            regions,
            version,
            group: owner,
          },
        });
        this.closeClusterCreateModal();
        await this.refreshServers();
        this.showNotice(
          `Cluster '${name}' creation requested.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError("clusterCreate", e, "Failed to create cluster.");
      } finally {
        this.clusterLoading.create = false;
      }
    },

    openCluster(clusterId) {
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
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterDetailView();
    },

    backToClusters() {
      this.setView("clusters");
    },

    async refreshSelectedCluster() {
      const clusterId = String(this.selectedClusterId || "").trim();
      if (!clusterId) return;
      this.clusterLoading.details = true;
      try {
        this.selectedCluster = await this.apiFetch(
          this.visibilityPath(`/clusters/${encodeURIComponent(clusterId)}`),
          { method: "GET" },
        );
        await this.refreshClusterDatabaseObjects();
      } catch (e) {
        console.error(e);
        this.showNotice(
          this.errorMessage(e, "Failed to load cluster details."),
        );
        this.selectedCluster = null;
        this.clearClusterDatabaseObjectsState();
      } finally {
        this.clusterLoading.details = false;
      }
    },

    clearClusterDatabaseObjectsState() {
      this.clusterDatabaseObjects = [];
      this.clusterDatabaseObjectsVisibleRows = [];
      this.clusterDatabaseRoleGroupDrafts = {};
      this.clusterDatabaseRoleGroupSaving = {};
      this.clusterDatabaseObjectsLastUpdatedUtc = null;
      this.modal.clusterDatabaseObjectCreate.database_name = "";
      this.modal.clusterDatabaseObjectDeleteConfirm.database_name = "";
    },

    clearClusterArtifactsState() {
      this.clusterArtifacts = [];
      this.clusterArtifactsVisibleRows = [];
      this.clusterArtifactsLastUpdatedUtc = null;
      this.clusterArtifactDownloadingId = "";
    },

    persistClusterDatabaseObjectsFilter() {
      localStorage.setItem(
        "cp_cluster_database_objects_filter",
        this.clusterDatabaseObjectsFilterQuery || "",
      );
    },

    clusterDatabaseObjectRowText(row) {
      const roleText = Array.isArray(row?.database_roles)
        ? row.database_roles
            .flatMap((databaseRole) => [
              databaseRole?.database_role,
              databaseRole?.database_role_template,
              databaseRole?.scope_type,
              databaseRole?.schema_name,
              ...(Array.isArray(databaseRole?.groups) ? databaseRole.groups : []),
            ])
            .filter(Boolean)
            .join(" ")
        : "";
      return [
        row?.database_name,
        row?.created_by,
        row?.updated_by,
        roleText,
        this.toUtcStringMaybe(row?.created_at),
        this.toUtcStringMaybe(row?.updated_at),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    applyClusterDatabaseObjectsFilter() {
      const q = String(this.clusterDatabaseObjectsFilterQuery || "")
        .trim()
        .toLowerCase();
      let rows = Array.isArray(this.clusterDatabaseObjects)
        ? [...this.clusterDatabaseObjects]
        : [];
      if (q) {
        rows = rows.filter((row) =>
          this.clusterDatabaseObjectRowText(row).includes(q),
        );
      }
      rows.sort((a, b) =>
        String(a?.database_name || "").localeCompare(
          String(b?.database_name || ""),
        ),
      );
      this.clusterDatabaseObjectsVisibleRows = rows;
    },

    async refreshClusterDatabaseObjects() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;

      this.clusterDatabaseObjectsLoading.list = true;
      try {
        // Keep mappings as their own API resource; merge them into cards for display.
        const [databaseObjects, groupMappings] = await Promise.all([
          this.apiFetch(
            this.visibilityPath(
              `/clusters/${encodeURIComponent(clusterId)}/database-objects`,
            ),
            { method: "GET" },
          ),
          this.apiFetch(
            this.visibilityPath(
              `/clusters/${encodeURIComponent(clusterId)}/database-role-group-mappings`,
            ),
            { method: "GET" },
          ),
        ]);
        this.clusterDatabaseObjects = this.applyDatabaseRoleGroupMappings(
          Array.isArray(databaseObjects) ? databaseObjects : [],
          Array.isArray(groupMappings) ? groupMappings : [],
        );
        this.initializeClusterDatabaseRoleGroupDrafts();
        this.clusterDatabaseObjectsLastUpdatedUtc = this.utcNowString();
        this.applyClusterDatabaseObjectsFilter();
      } catch (e) {
        console.error(e);
        this.clearClusterDatabaseObjectsState();
        this.clusterDatabaseObjectsLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load database objects."),
        );
      } finally {
        this.clusterDatabaseObjectsLoading.list = false;
      }
    },

    applyDatabaseRoleGroupMappings(databaseObjects, groupMappings) {
      // The API returns raw mapping rows so the UI can display assigned groups.
      const groupsByRole = {};
      for (const mapping of groupMappings) {
        const roleName = String(mapping?.database_role || "").trim();
        const groupName = String(mapping?.group_name || "").trim();
        if (!roleName || !groupName) continue;
        groupsByRole[roleName] = groupsByRole[roleName] || [];
        if (!groupsByRole[roleName].includes(groupName)) {
          groupsByRole[roleName].push(groupName);
        }
      }

      return databaseObjects.map((databaseObject) => ({
        ...databaseObject,
        database_roles: Array.isArray(databaseObject?.database_roles)
          ? databaseObject.database_roles.map((databaseRole) => {
              const roleName = String(databaseRole?.database_role || "").trim();
              return {
                ...databaseRole,
                groups: groupsByRole[roleName] || [],
              };
            })
          : [],
      }));
    },

    initializeClusterDatabaseRoleGroupDrafts() {
      const drafts = {};
      const databaseObjects = Array.isArray(this.clusterDatabaseObjects)
        ? this.clusterDatabaseObjects
        : [];
      for (const databaseObject of databaseObjects) {
        const databaseRoles = Array.isArray(databaseObject?.database_roles)
          ? databaseObject.database_roles
          : [];
        for (const databaseRole of databaseRoles) {
          const roleName = String(databaseRole?.database_role || "").trim();
          if (!roleName) continue;
          const groups = Array.isArray(databaseRole?.groups)
            ? databaseRole.groups
            : [];
          drafts[roleName] = groups.join("\n");
        }
      }
      this.clusterDatabaseRoleGroupDrafts = drafts;
    },

    databaseRoleGroupsFromDraft(databaseRole) {
      const roleName = String(databaseRole?.database_role || "").trim();
      const raw = String(this.clusterDatabaseRoleGroupDrafts[roleName] || "");
      const groups = [];
      for (const groupName of raw.split(/[\n,]+/)) {
        const normalizedGroupName = String(groupName || "").trim();
        if (normalizedGroupName && !groups.includes(normalizedGroupName)) {
          groups.push(normalizedGroupName);
        }
      }
      return groups;
    },

    databaseRoleGroupSummary(databaseRole) {
      const groups = this.databaseRoleGroupsFromDraft(databaseRole);
      if (!groups.length) return "No IdP groups mapped";
      if (groups.length === 1) return "1 IdP group mapped";
      return `${groups.length} IdP groups mapped`;
    },

    isDatabaseRoleGroupMappingSaving(databaseRole) {
      const roleName = String(databaseRole?.database_role || "").trim();
      return Boolean(this.clusterDatabaseRoleGroupSaving[roleName]);
    },

    async updateClusterDatabaseRoleGroups(databaseRole) {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const roleName = String(databaseRole?.database_role || "").trim();
      if (!clusterId || !roleName) return;

      const groups = this.databaseRoleGroupsFromDraft(databaseRole);
      this.clusterDatabaseObjectsLoading.groupMappings = true;
      this.clusterDatabaseRoleGroupSaving = {
        ...this.clusterDatabaseRoleGroupSaving,
        [roleName]: true,
      };
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/database-role-group-mappings/${encodeURIComponent(roleName)}`,
          {
            method: "PUT",
            body: { groups },
          },
        );
        await this.refreshClusterDatabaseObjects();
        this.showNotice(
          `IdP group mapping updated for database role '${roleName}'.`,
        );
      } catch (e) {
        console.error(e);
        this.showNotice(
          this.errorMessage(e, "Failed to update IdP group mapping."),
        );
      } finally {
        this.clusterDatabaseObjectsLoading.groupMappings = false;
        this.clusterDatabaseRoleGroupSaving = {
          ...this.clusterDatabaseRoleGroupSaving,
          [roleName]: false,
        };
      }
    },

    openClusterDatabaseObjectCreateModal() {
      this.modal.clusterDatabaseObjectCreate.open = true;
      this.modal.clusterDatabaseObjectCreate.database_name = "";
      this.clearModalError("clusterDatabaseObjectCreate");
    },

    closeClusterDatabaseObjectCreateModal() {
      this.modal.clusterDatabaseObjectCreate.open = false;
      this.modal.clusterDatabaseObjectCreate.database_name = "";
      this.clearModalError("clusterDatabaseObjectCreate");
    },

    async createClusterDatabaseObject() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const databaseName = String(
        this.modal.clusterDatabaseObjectCreate.database_name || "",
      ).trim();
      if (!clusterId || !databaseName) {
        this.modalErrors.clusterDatabaseObjectCreate =
          "Database name is required.";
        return;
      }

      this.clusterDatabaseObjectsLoading.create = true;
      this.clearModalError("clusterDatabaseObjectCreate");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/database-objects`,
          {
            method: "POST",
            body: { database_name: databaseName },
          },
        );
        this.closeClusterDatabaseObjectCreateModal();
        this.clearClusterUsersState();
        await this.refreshClusterDatabaseObjects();
        this.showNotice(
          `Database object '${databaseName}' created and default roles materialized.`,
        );
      } catch (e) {
        this.setModalError(
          "clusterDatabaseObjectCreate",
          e,
          "Failed to create database object.",
        );
      } finally {
        this.clusterDatabaseObjectsLoading.create = false;
      }
    },

    openClusterDatabaseObjectDeleteConfirm(databaseObject) {
      const databaseName = String(databaseObject?.database_name || "").trim();
      if (!databaseName) return;
      this.modal.clusterDatabaseObjectDeleteConfirm.open = true;
      this.modal.clusterDatabaseObjectDeleteConfirm.database_name = databaseName;
      this.clearModalError("clusterDatabaseObjectDeleteConfirm");
    },

    closeClusterDatabaseObjectDeleteConfirm() {
      this.modal.clusterDatabaseObjectDeleteConfirm.open = false;
      this.modal.clusterDatabaseObjectDeleteConfirm.database_name = "";
      this.clearModalError("clusterDatabaseObjectDeleteConfirm");
    },

    async confirmClusterDatabaseObjectDelete() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const databaseName = String(
        this.modal.clusterDatabaseObjectDeleteConfirm.database_name || "",
      ).trim();
      if (!clusterId || !databaseName) return;

      this.clusterDatabaseObjectsLoading.delete = true;
      this.clearModalError("clusterDatabaseObjectDeleteConfirm");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/database-objects/${encodeURIComponent(databaseName)}`,
          { method: "DELETE" },
        );
        this.closeClusterDatabaseObjectDeleteConfirm();
        this.clearClusterUsersState();
        await this.refreshClusterDatabaseObjects();
        this.showNotice(`Database object '${databaseName}' deleted.`);
      } catch (e) {
        this.setModalError(
          "clusterDatabaseObjectDeleteConfirm",
          e,
          "Failed to delete database object.",
        );
      } finally {
        this.clusterDatabaseObjectsLoading.delete = false;
      }
    },

    clusterPrimaryDns(cluster = this.selectedCluster) {
      const lb = Array.isArray(cluster?.lbs_inventory)
        ? cluster.lbs_inventory.find((entry) => entry?.dns_address)
        : null;
      return String(lb?.dns_address || "");
    },

    clusterLbEndpoints(cluster = this.selectedCluster) {
      return Array.isArray(cluster?.lbs_inventory)
        ? cluster.lbs_inventory.filter((entry) => entry?.dns_address)
        : [];
    },

    clusterDbConsoleUrl(lbOrCluster = this.selectedCluster) {
      const dns = lbOrCluster?.dns_address
        ? String(lbOrCluster.dns_address || "").trim()
        : this.clusterPrimaryDns(lbOrCluster);
      return dns ? `https://${dns}:8080` : "";
    },

    clusterEndpointAddress(lbOrCluster = this.selectedCluster) {
      const dns = lbOrCluster?.dns_address
        ? String(lbOrCluster.dns_address || "").trim()
        : this.clusterPrimaryDns(lbOrCluster);
      return dns;
    },

    async copyClusterEndpointAddress(lbOrCluster = this.selectedCluster) {
      const dns = this.clusterEndpointAddress(lbOrCluster);
      if (!dns) return;
      if (
        typeof navigator !== "undefined" &&
        navigator.clipboard &&
        typeof navigator.clipboard.writeText === "function"
      ) {
        await navigator.clipboard.writeText(dns);
      } else if (typeof document !== "undefined") {
        const el = document.createElement("textarea");
        el.value = dns;
        el.setAttribute("readonly", "");
        el.style.position = "absolute";
        el.style.left = "-9999px";
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
      }
      this.clusterConnectCopiedFor = dns;
      this.showNotice(
        dns
          ? `Cluster endpoint copied for '${dns}'.`
          : "Cluster endpoint copied to clipboard.",
      );
    },

    openDbConsole(lbOrCluster = this.selectedCluster) {
      const url = this.clusterDbConsoleUrl(lbOrCluster);
      if (!url || typeof window === "undefined") return;
      window.open(url, "_blank", "noopener");
    },

    openClusterJobs() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      const filter = String(clusterId).trim();
      this.jobsFilterQuery = filter;
      if (typeof this.setView === "function") {
        this.setView("jobs");
      } else if (typeof window !== "undefined") {
        window.location.hash = `/jobs/filter=${encodeURIComponent(filter)}`;
      }
    },

    openClusterDashboard() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.view = "cluster_dashboard";
      this.clearClusterDatabaseObjectsState();
      this.clearClusterUsersState();
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterDashboardView();
    },

    backToClusterDetail() {
      if (!this.selectedClusterId) {
        this.setView("clusters");
        return;
      }
      this.clearClusterUsersState();
      this.view = "cluster";
      localStorage.setItem("cp_view", this.view);
      this.syncHashFromState();
      this.ensureClusterDetailView();
    },

    openClusterUsers() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.clearClusterDatabaseObjectsState();
      this.view = "cluster_users";
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterUsersView();
    },

    openClusterDatabases() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.clearClusterUsersState();
      this.view = "cluster_databases";
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterDatabasesView();
    },

    openClusterBackups() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.clearClusterDatabaseObjectsState();
      this.clearClusterUsersState();
      this.view = "cluster_backups";
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterBackupsView();
    },

    openClusterDebugZips() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      this.selectedClusterArtifactKind = "debug_zip";
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.clearClusterDatabaseObjectsState();
      this.clearClusterUsersState();
      this.view = "cluster_artifacts";
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterArtifactsView();
    },

    openClusterRecovery() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.clearClusterDatabaseObjectsState();
      this.clearClusterUsersState();
      this.view = "cluster_recovery";
      localStorage.setItem("cp_view", this.view);
      this.clearNotice();
      this.syncHashFromState();
      this.ensureClusterRecoveryView();
    },

    openClusterDeleteConfirm() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;
      this.modal.clusterDeleteConfirm.cluster_id = clusterId;
      this.clearModalError("clusterDeleteConfirm");
      this.modal.clusterDeleteConfirm.open = true;
    },

    closeClusterDeleteConfirm() {
      this.modal.clusterDeleteConfirm.open = false;
      this.modal.clusterDeleteConfirm.cluster_id = "";
      this.clearModalError("clusterDeleteConfirm");
    },

    openClusterHealthcheckConfirm() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;
      this.modal.clusterHealthcheckConfirm.cluster_id = clusterId;
      this.clearModalError("clusterHealthcheckConfirm");
      this.modal.clusterHealthcheckConfirm.open = true;
    },

    closeClusterHealthcheckConfirm() {
      this.modal.clusterHealthcheckConfirm.open = false;
      this.modal.clusterHealthcheckConfirm.cluster_id = "";
      this.clearModalError("clusterHealthcheckConfirm");
    },

    async openClusterUpgradeModal() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;

      this.clusterLoading.upgrade = true;
      this.clearModalError("clusterUpgrade");
      this.modal.clusterUpgrade.open = true;
      this.modal.clusterUpgrade.version = "";
      this.modal.clusterUpgrade.upgrade_versions = [];

      try {
        const options = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/options`,
          ),
          { method: "GET" },
        );
        const upgradeVersions = Array.isArray(options?.upgrade_versions)
          ? options.upgrade_versions
          : [];
        this.modal.clusterUpgrade.upgrade_versions = upgradeVersions;
        this.modal.clusterUpgrade.version = upgradeVersions.length
          ? String(upgradeVersions[0])
          : "";

        if (upgradeVersions.length === 0) {
          this.modalErrors.clusterUpgrade =
            "No upgrade versions are available for this cluster.";
        }
      } catch (e) {
        this.setModalError(
          "clusterUpgrade",
          e,
          "Failed to load upgrade options.",
        );
      } finally {
        this.clusterLoading.upgrade = false;
      }
    },

    closeClusterUpgradeModal() {
      this.modal.clusterUpgrade.open = false;
      this.modal.clusterUpgrade.version = "";
      this.modal.clusterUpgrade.upgrade_versions = [];
      this.clearModalError("clusterUpgrade");
    },

    async openClusterScaleModal() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId || !this.selectedCluster) return;

      this.clusterLoading.scale = true;
      this.clearModalError("clusterScale");
      this.modal.clusterScale.open = true;

      try {
        const options = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/options`,
          ),
          { method: "GET" },
        );
        const original = {
          node_count: Number(this.selectedCluster.node_count ?? 0),
          node_cpus: Number(this.selectedCluster.node_cpus ?? 0),
          disk_size: Number(this.selectedCluster.disk_size ?? 0),
          regions: this.clusterRegionIdsFromCluster(this.selectedCluster),
        };

        this.modal.clusterScale.options = {
          node_counts: Array.isArray(options?.node_counts)
            ? options.node_counts
            : [],
          cpus_per_node: Array.isArray(options?.cpus_per_node)
            ? options.cpus_per_node
            : [],
          disk_sizes: Array.isArray(options?.disk_sizes)
            ? options.disk_sizes
            : [],
          regions: Array.isArray(options?.regions) ? options.regions : [],
        };
        this.modal.clusterScale.original = original;
        this.modal.clusterScale.node_count = String(original.node_count);
        this.modal.clusterScale.node_cpus = String(original.node_cpus);
        this.modal.clusterScale.disk_size = String(original.disk_size);
        this.modal.clusterScale.regions = [...original.regions];
      } catch (e) {
        this.setModalError("clusterScale", e, "Failed to load scale options.");
      } finally {
        this.clusterLoading.scale = false;
      }
    },

    closeClusterScaleModal() {
      this.modal.clusterScale.open = false;
      this.modal.clusterScale.node_count = "";
      this.modal.clusterScale.node_cpus = "";
      this.modal.clusterScale.disk_size = "";
      this.modal.clusterScale.regions = [];
      this.modal.clusterScale.original = null;
      this.modal.clusterScale.options = {
        node_counts: [],
        cpus_per_node: [],
        disk_sizes: [],
        regions: [],
      };
      this.clearModalError("clusterScale");
    },

    async confirmClusterDelete() {
      const clusterId = String(
        this.modal.clusterDeleteConfirm.cluster_id || "",
      ).trim();
      if (!clusterId) return;

      this.clusterLoading.delete = true;
      this.clearModalError("clusterDeleteConfirm");
      try {
        const result = await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}`,
          {
            method: "DELETE",
          },
        );
        this.closeClusterDeleteConfirm();
        this.selectedCluster = null;
        this.selectedClusterId = "";
        localStorage.removeItem("cp_selected_cluster_id");
        await this.refreshServers();
        this.setView("clusters");
        this.showNotice(
          `Cluster '${clusterId}' delete requested.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterDeleteConfirm",
          e,
          "Failed to delete cluster.",
        );
      } finally {
        this.clusterLoading.delete = false;
      }
    },

    async confirmClusterHealthcheck() {
      const clusterId = String(
        this.modal.clusterHealthcheckConfirm.cluster_id || "",
      ).trim();
      if (!clusterId) return;

      this.clusterLoading.healthcheck = true;
      this.clearModalError("clusterHealthcheckConfirm");
      try {
        const result = await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/healthcheck`,
          {
            method: "POST",
          },
        );
        this.closeClusterHealthcheckConfirm();
        this.showNotice(
          `Cluster '${clusterId}' healthcheck requested.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterHealthcheckConfirm",
          e,
          "Failed to request cluster healthcheck.",
        );
      } finally {
        this.clusterLoading.healthcheck = false;
      }
    },

    triggerClusterAction(label) {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.showNotice(
        `${label} for cluster '${clusterId}' is not wired in the webapp yet.`,
      );
    },

    clusterDashboardNodeColor(nodeId) {
      const index = Number(nodeId);
      if (!Number.isFinite(index)) return this.clusterDashboardPalette[0];
      return this.clusterDashboardPalette[
        index % this.clusterDashboardPalette.length
      ];
    },

    clusterDashboardChartRows() {
      return Array.isArray(this.clusterDashboardChartData)
        ? this.clusterDashboardChartData
        : [];
    },

    clusterDashboardHasData() {
      return this.clusterDashboardChartRows().length > 0;
    },

    clusterDashboardTsToMs(tsValue) {
      const normalized = String(tsValue || "").trim();
      if (!normalized) return null;
      const parsed = Date.parse(`${normalized.replace(" ", "T")}Z`);
      return Number.isFinite(parsed) ? parsed : null;
    },

    clusterDashboardXAxisValue(tsValue) {
      const date = new Date(tsValue);
      if (Number.isNaN(date.getTime())) return "";
      return date.toISOString().slice(11, 19);
    },

    clusterDashboardChartWidth(containerId) {
      if (typeof document === "undefined") return 320;
      const el = document.getElementById(containerId);
      const width = Number(
        el?.clientWidth ||
          el?.offsetWidth ||
          el?.parentElement?.clientWidth ||
          0,
      );
      return Math.max(Math.floor(width || 320), 240);
    },

    clusterDashboardChartHeight(containerId) {
      if (typeof document === "undefined") return 320;
      const el = document.getElementById(containerId);
      const height = Number(
        el?.clientHeight ||
          el?.offsetHeight ||
          el?.parentElement?.clientHeight ||
          0,
      );
      return Math.max(Math.floor(height || 320), 240);
    },

    clusterDashboardAlignedData(seriesKeys) {
      const rows = this.clusterDashboardChartRows();
      const rawX = rows.map((row) => this.clusterDashboardTsToMs(row?.ts));
      const indices = rawX
        .map((value, index) => (value === null ? -1 : index))
        .filter((index) => index >= 0);

      return [
        indices.map((index) => rawX[index]),
        ...seriesKeys.map((key) =>
          indices.map((index) => {
            const value = rows[index]?.[key];
            return Number.isFinite(Number(value)) ? Number(value) : null;
          }),
        ),
      ];
    },

    clusterDashboardChartOptions({ yLabel, containerId, series }) {
      return {
        width: this.clusterDashboardChartWidth(containerId),
        height: this.clusterDashboardChartHeight(containerId),
        legend: { show: true },
        cursor: { drag: { x: true, y: false } },
        scales: { x: { time: false } },
        axes: [
          {
            stroke: "#94a3b8",
            grid: { stroke: "rgba(148, 163, 184, 0.12)" },
            values: (_u, splits) =>
              splits.map((value) => this.clusterDashboardXAxisValue(value)),
          },
          {
            stroke: "#94a3b8",
            grid: { stroke: "rgba(148, 163, 184, 0.12)" },
            label: yLabel,
            size: 48,
            labelSize: 11,
            labelGap: 4,
          },
        ],
        series: [
          {},
          ...series.map((entry) => ({
            label: entry.label,
            stroke: entry.stroke,
            width: 2,
            points: { show: false },
            spanGaps: true,
          })),
        ],
      };
    },

    destroyClusterDashboardCharts() {
      const charts = this._clusterDashboardCharts || {};
      Object.values(charts).forEach((chart) => {
        if (chart && typeof chart.destroy === "function") {
          chart.destroy();
        }
      });
      this._clusterDashboardCharts = {};
    },

    renderClusterDashboardCharts() {
      if (
        typeof window === "undefined" ||
        !this.clusterDashboardHasData()
      ) {
        this.destroyClusterDashboardCharts();
        return;
      }
      if (typeof window.uPlot !== "function") {
        ensureUPlotAssets().then(() => {
          if (this.view === "cluster_dashboard") {
            this.renderClusterDashboardCharts();
          }
        });
        return;
      }

      const chartConfigs = [
        {
          id: "clusterDashboardCpuChart",
          key: "cpu",
          title: "CPU Util",
          yLabel: "CPU Util (%)",
          series: this.clusterDashboardCurrentNodes.map((nodeId) => ({
            label: `n${nodeId}`,
            key: `cpu_n${nodeId}`,
            stroke: this.clusterDashboardNodeColor(nodeId),
          })),
        },
        {
          id: "clusterDashboardQueriesChart",
          key: "queries",
          title: "SQL Queries per Second",
          yLabel: "queries",
          series: [
            { label: "selects", key: "s", stroke: "#495eff" },
            { label: "updates", key: "u", stroke: "#CE8943" },
            { label: "deletes", key: "d", stroke: "#d20f0f" },
            { label: "inserts", key: "i", stroke: "#F68EFF" },
            { label: "total", key: "t", stroke: "#FFFFFF" },
          ],
        },
        {
          id: "clusterDashboardLatencyChart",
          key: "latency",
          title: "Service Latency p99",
          yLabel: "latency (ms)",
          series: this.clusterDashboardCurrentNodes.map((nodeId) => ({
            label: `n${nodeId}`,
            key: `p99_n${nodeId}`,
            stroke: this.clusterDashboardNodeColor(nodeId),
          })),
        },
      ];

      this.destroyClusterDashboardCharts();

      chartConfigs.forEach((config) => {
        const el =
          typeof document !== "undefined"
            ? document.getElementById(config.id)
            : null;
        if (!el || config.series.length === 0) return;

        const data = this.clusterDashboardAlignedData(
          config.series.map((entry) => entry.key),
        );
        if (!Array.isArray(data[0]) || data[0].length === 0) return;

        this._clusterDashboardCharts[config.key] = new window.uPlot(
          this.clusterDashboardChartOptions({
            yLabel: config.yLabel,
            containerId: config.id,
            series: config.series,
          }),
          data,
          el,
        );
      });
    },

    async refreshClusterDashboard() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;

      this.clusterDashboardLoading.snapshot = true;
      try {
        const end = Math.floor(Date.now() / 1000);
        const start = end - this.clusterDashboardPeriodMins * 60;
        const snapshot = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/dashboard`,
            {
              start,
              end,
              interval_secs: this.clusterDashboardIntervalSecs,
            },
          ),
          { method: "GET" },
        );

        this.clusterDashboardSnapshot = snapshot || null;
        this.clusterDashboardChartData = Array.isArray(
          snapshot?.metrics?.chart_data,
        )
          ? snapshot.metrics.chart_data
          : [];
        this.clusterDashboardCurrentNodes = Array.isArray(
          snapshot?.metrics?.current_nodes,
        )
          ? snapshot.metrics.current_nodes
          : [];
        this.clusterDashboardLastUpdatedUtc = this.utcNowString();

        if (snapshot?.cluster) {
          this.selectedCluster = snapshot.cluster;
          this.selectedClusterId = String(
            snapshot.cluster.cluster_id || clusterId,
          );
          localStorage.setItem(
            "cp_selected_cluster_id",
            this.selectedClusterId,
          );
        }

        if (typeof window !== "undefined") {
          window.requestAnimationFrame(() =>
            this.renderClusterDashboardCharts(),
          );
        }
      } catch (e) {
        console.error(e);
        this.clusterDashboardLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load cluster dashboard."),
        );
      } finally {
        this.clusterDashboardLoading.snapshot = false;
      }
    },

    persistClusterUsersFilter() {
      localStorage.setItem(
        "cp_cluster_users_filter",
        this.clusterUsersFilterQuery || "",
      );
    },

    clusterUsersRowText(row) {
      return [
        row?.username,
        row?.options,
        ...(Array.isArray(row?.member_of) ? row.member_of : []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    clearClusterUsersState() {
      this.clusterUsers = [];
      this.clusterUsersVisibleRows = [];
      this.clusterUsersClusterId = "";
      this.databaseRoles = [];
      this.modal.clusterUserCreate.database_roles = [];
      this.modal.clusterUserRoles.databaseRoles = [];
      this.modal.clusterUserRoles.grantDatabaseRoles = [];
    },

    applyClusterUsersFilter() {
      const q = String(this.clusterUsersFilterQuery || "")
        .trim()
        .toLowerCase();
      let rows = Array.isArray(this.clusterUsers) ? [...this.clusterUsers] : [];
      if (q) {
        rows = rows.filter((row) => this.clusterUsersRowText(row).includes(q));
      }
      rows.sort((a, b) =>
        String(a?.username || "").localeCompare(String(b?.username || "")),
      );
      this.clusterUsersVisibleRows = rows;
    },

    async refreshClusterUsers() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;
      if (this.clusterUsersClusterId !== clusterId) {
        this.clearClusterUsersState();
      }
      this.clusterUsersLoading.snapshot = true;
      try {
        const snapshot = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/users`,
          ),
          { method: "GET" },
        );
        this.clusterUsers = Array.isArray(snapshot?.database_users)
          ? snapshot.database_users
          : [];
        this.clusterUsersClusterId = clusterId;
        this.databaseRoleTemplates = Array.isArray(snapshot?.database_role_templates)
          ? snapshot.database_role_templates
          : this.databaseRoleTemplates;
        this.databaseRoles = Array.isArray(snapshot?.database_roles)
          ? snapshot.database_roles
          : this.databaseRoles;
        this.applyDatabaseRoleTemplatesFilter();
        if (snapshot?.cluster) {
          this.selectedCluster = snapshot.cluster;
        }
        this.clusterUsersLastUpdatedUtc = this.utcNowString();
        this.applyClusterUsersFilter();
      } catch (e) {
        console.error(e);
        this.clearClusterUsersState();
        this.clusterUsersLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load cluster users."),
        );
      } finally {
        this.clusterUsersLoading.snapshot = false;
      }
    },

    databaseRoleLabel(databaseRole) {
      const roleName = String(databaseRole?.database_role || "").trim();
      const databaseName = String(databaseRole?.database_name || "").trim();
      const schemaName = String(databaseRole?.schema_name || "").trim();
      const scope = schemaName ? `${databaseName}.${schemaName}` : databaseName;
      return scope ? `${roleName} (${scope})` : roleName || "-";
    },

    openClusterUserCreateModal() {
      this.modal.clusterUserCreate.open = true;
      this.modal.clusterUserCreate.username = "";
      this.modal.clusterUserCreate.password = "";
      this.modal.clusterUserCreate.database_roles = [];
      this.clearModalError("clusterUserCreate");
    },

    closeClusterUserCreateModal() {
      this.modal.clusterUserCreate.open = false;
      this.modal.clusterUserCreate.username = "";
      this.modal.clusterUserCreate.password = "";
      this.modal.clusterUserCreate.database_roles = [];
      this.clearModalError("clusterUserCreate");
    },

    async createClusterUser() {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(
        this.modal.clusterUserCreate.username || "",
      ).trim();
      const password = String(
        this.modal.clusterUserCreate.password || "",
      ).trim();
      const database_roles = Array.isArray(
        this.modal.clusterUserCreate.database_roles,
      )
        ? this.modal.clusterUserCreate.database_roles
            .map((databaseRoleTemplate) => String(databaseRoleTemplate || "").trim())
            .filter(Boolean)
        : [];
      if (!clusterId || !username || !password) {
        this.setModalError(
          "clusterUserCreate",
          new Error("Username and password are required."),
          "Username and password are required.",
        );
        return;
      }
      this.clusterUsersLoading.create = true;
      this.clearModalError("clusterUserCreate");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users`,
          {
            method: "POST",
            body: { username, password, database_roles },
          },
        );
        this.closeClusterUserCreateModal();
        await this.refreshClusterUsers();
        this.showNotice(`Database user '${username}' created.`);
      } catch (e) {
        this.setModalError(
          "clusterUserCreate",
          e,
          "Failed to create database user.",
        );
      } finally {
        this.clusterUsersLoading.create = false;
      }
    },

    openClusterUserDeleteConfirm(row) {
      this.modal.clusterUserDeleteConfirm.open = true;
      this.modal.clusterUserDeleteConfirm.username = String(
        row?.username || "",
      ).trim();
      this.clearModalError("clusterUserDeleteConfirm");
    },

    closeClusterUserDeleteConfirm() {
      this.modal.clusterUserDeleteConfirm.open = false;
      this.modal.clusterUserDeleteConfirm.username = "";
      this.clearModalError("clusterUserDeleteConfirm");
    },

    async confirmClusterUserDelete() {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(
        this.modal.clusterUserDeleteConfirm.username || "",
      ).trim();
      if (!clusterId || !username) return;
      this.clusterUsersLoading.delete = true;
      this.clearModalError("clusterUserDeleteConfirm");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users/${encodeURIComponent(username)}`,
          { method: "DELETE" },
        );
        this.closeClusterUserDeleteConfirm();
        await this.refreshClusterUsers();
        this.showNotice(`Database user '${username}' deleted.`);
      } catch (e) {
        this.setModalError(
          "clusterUserDeleteConfirm",
          e,
          "Failed to delete database user.",
        );
      } finally {
        this.clusterUsersLoading.delete = false;
      }
    },

    openClusterUserPasswordModal(row) {
      this.modal.clusterUserPassword.open = true;
      this.modal.clusterUserPassword.username = String(
        row?.username || "",
      ).trim();
      this.modal.clusterUserPassword.password = "";
      this.clearModalError("clusterUserPassword");
    },

    closeClusterUserPasswordModal() {
      this.modal.clusterUserPassword.open = false;
      this.modal.clusterUserPassword.username = "";
      this.modal.clusterUserPassword.password = "";
      this.clearModalError("clusterUserPassword");
    },

    async updateClusterUserPassword() {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(
        this.modal.clusterUserPassword.username || "",
      ).trim();
      const password = String(
        this.modal.clusterUserPassword.password || "",
      ).trim();
      if (!clusterId || !username || !password) {
        this.setModalError(
          "clusterUserPassword",
          new Error("A new password is required."),
          "A new password is required.",
        );
        return;
      }
      this.clusterUsersLoading.password = true;
      this.clearModalError("clusterUserPassword");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users/${encodeURIComponent(username)}/password`,
          {
            method: "POST",
            body: { password },
          },
        );
        this.closeClusterUserPasswordModal();
        this.showNotice(`Password updated for '${username}'.`);
      } catch (e) {
        this.setModalError(
          "clusterUserPassword",
          e,
          "Failed to update password.",
        );
      } finally {
        this.clusterUsersLoading.password = false;
      }
    },

    openClusterUserRolesModal(row) {
      this.modal.clusterUserRoles.open = true;
      this.modal.clusterUserRoles.username = String(row?.username || "").trim();
      this.modal.clusterUserRoles.databaseRoles = Array.isArray(row?.member_of)
        ? row.member_of.filter(Boolean)
        : [];
      this.modal.clusterUserRoles.grantDatabaseRoles = [];
      this.clearModalError("clusterUserRoles");
    },

    closeClusterUserRolesModal() {
      this.modal.clusterUserRoles.open = false;
      this.modal.clusterUserRoles.username = "";
      this.modal.clusterUserRoles.databaseRoles = [];
      this.modal.clusterUserRoles.grantDatabaseRoles = [];
      this.clearModalError("clusterUserRoles");
    },

    async revokeClusterUserDatabaseRole(databaseRole) {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(
        this.modal.clusterUserRoles.username || "",
      ).trim();
      const normalizedDatabaseRole = String(databaseRole || "").trim();
      if (!clusterId || !username || !normalizedDatabaseRole) return;
      this.clusterUsersLoading.revokeDatabaseRole = true;
      this.clearModalError("clusterUserRoles");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users/${encodeURIComponent(username)}/revoke-database-roles`,
          {
            method: "POST",
            body: { database_roles: [normalizedDatabaseRole] },
          },
        );
        this.modal.clusterUserRoles.databaseRoles =
          this.modal.clusterUserRoles.databaseRoles.filter(
            (entry) => entry !== normalizedDatabaseRole,
          );
        await this.refreshClusterUsers();
        this.showNotice(
          `Database role '${normalizedDatabaseRole}' revoked from '${username}'.`,
        );
      } catch (e) {
        this.setModalError(
          "clusterUserRoles",
          e,
          "Failed to revoke database role.",
        );
      } finally {
        this.clusterUsersLoading.revokeDatabaseRole = false;
      }
    },

    async grantClusterUserDatabaseRoles() {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(
        this.modal.clusterUserRoles.username || "",
      ).trim();
      const database_roles = Array.isArray(
        this.modal.clusterUserRoles.grantDatabaseRoles,
      )
        ? this.modal.clusterUserRoles.grantDatabaseRoles
            .map((databaseRole) => String(databaseRole || "").trim())
            .filter(Boolean)
        : [];
      if (!clusterId || !username || database_roles.length === 0) {
        this.setModalError(
          "clusterUserRoles",
          new Error("Select at least one synced database role to grant."),
          "Select at least one synced database role to grant.",
        );
        return;
      }
      this.clusterUsersLoading.grantDatabaseRoles = true;
      this.clearModalError("clusterUserRoles");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users/${encodeURIComponent(username)}/grant-database-roles`,
          {
            method: "POST",
            body: { database_roles },
          },
        );
        this.modal.clusterUserRoles.grantDatabaseRoles = [];
        await this.refreshClusterUsers();
        const refreshed = this.clusterUsers.find(
          (row) => String(row?.username || "") === username,
        );
        this.modal.clusterUserRoles.databaseRoles = Array.isArray(refreshed?.member_of)
          ? refreshed.member_of.filter(Boolean)
          : this.modal.clusterUserRoles.databaseRoles;
        this.showNotice(`Database roles granted to '${username}'.`);
      } catch (e) {
        this.setModalError(
          "clusterUserRoles",
          e,
          "Failed to grant database roles.",
        );
      } finally {
        this.clusterUsersLoading.grantDatabaseRoles = false;
      }
    },

    async refreshClusterRecoveryBackups() {
      if (!this.selectedClusterId) return;
      this.clusterRecoveryLoading.list = true;
      try {
        const snapshot = await this.apiFetch(
          this.visibilityPath("/cluster-recovery/backups", {
            full_cluster_only: true,
          }),
          { method: "GET" },
        );
        this.clusterRecoveryBackups = Array.isArray(snapshot?.backups)
          ? snapshot.backups.filter(
              (backup) =>
                String(backup?.status || "").toUpperCase() === "AVAILABLE" &&
                Boolean(backup?.is_full_cluster),
            )
          : [];
        this.clusterRecoveryLastUpdatedUtc = this.utcNowString();
      } catch (e) {
        console.error(e);
        this.clusterRecoveryBackups = [];
        this.clusterRecoveryLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load recovery backups."),
        );
      } finally {
        this.clusterRecoveryLoading.list = false;
      }
    },

    clusterRecoverySourceRows() {
      const groups = new Map();
      for (const backup of this.clusterRecoveryBackups || []) {
        const clusterId = String(backup?.cluster_id || "").trim();
        if (!clusterId) continue;
        if (!groups.has(clusterId)) {
          groups.set(clusterId, {
            cluster_id: clusterId,
            grp: backup?.grp || "",
            backups: [],
            latest_end_time: null,
            latest_seen_at: null,
          });
        }
        const group = groups.get(clusterId);
        group.backups.push(backup);
        if (
          backup?.end_time &&
          (!group.latest_end_time ||
            new Date(backup.end_time) > new Date(group.latest_end_time))
        ) {
          group.latest_end_time = backup.end_time;
        }
        if (
          backup?.last_seen_at &&
          (!group.latest_seen_at ||
            new Date(backup.last_seen_at) > new Date(group.latest_seen_at))
        ) {
          group.latest_seen_at = backup.last_seen_at;
        }
      }
      return Array.from(groups.values())
        .map((group) => ({
          ...group,
          backups: group.backups.sort(
            (a, b) => new Date(b?.end_time || 0) - new Date(a?.end_time || 0),
          ),
        }))
        .sort((a, b) => a.cluster_id.localeCompare(b.cluster_id));
    },

    clusterRecoveryBackupCountForSource(row) {
      return Array.isArray(row?.backups) ? row.backups.length : 0;
    },

    isClusterRecoveryExpanded(clusterId) {
      return Boolean(this.clusterRecoveryExpanded[String(clusterId || "")]);
    },

    toggleClusterRecoverySource(clusterId) {
      const key = String(clusterId || "").trim();
      if (!key) return;
      this.clusterRecoveryExpanded = {
        ...this.clusterRecoveryExpanded,
        [key]: !this.clusterRecoveryExpanded[key],
      };
    },

    openClusterRecoveryRestoreConfirm(backup) {
      const sourceClusterId = String(backup?.cluster_id || "").trim();
      const targetClusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const backupPath = String(backup?.backup_path || "").trim();
      if (!sourceClusterId || !targetClusterId || !backupPath) return;
      this.modal.clusterRecoveryRestoreConfirm.open = true;
      this.modal.clusterRecoveryRestoreConfirm.source_cluster_id =
        sourceClusterId;
      this.modal.clusterRecoveryRestoreConfirm.backup_path = backupPath;
      this.modal.clusterRecoveryRestoreConfirm.restore_aost =
        this.backupRestoreAostInputValue(backup?.start_time);
      this.modal.clusterRecoveryRestoreConfirm.start_time =
        backup?.start_time || "";
      this.clearModalError("clusterRecoveryRestoreConfirm");
    },

    closeClusterRecoveryRestoreConfirm() {
      this.modal.clusterRecoveryRestoreConfirm.open = false;
      this.modal.clusterRecoveryRestoreConfirm.source_cluster_id = "";
      this.modal.clusterRecoveryRestoreConfirm.backup_path = "";
      this.modal.clusterRecoveryRestoreConfirm.restore_aost = "";
      this.modal.clusterRecoveryRestoreConfirm.start_time = "";
      this.clearModalError("clusterRecoveryRestoreConfirm");
    },

    async restoreClusterFromCatalogBackup() {
      const targetClusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const restore = this.modal.clusterRecoveryRestoreConfirm;
      const sourceClusterId = String(restore.source_cluster_id || "").trim();
      const backupPath = String(restore.backup_path || "").trim();
      const restoreAost = this.backupRestoreAostApiValue(restore.restore_aost);
      if (!targetClusterId || !sourceClusterId || !backupPath) return;

      this.clusterRecoveryLoading.restore = true;
      this.clearModalError("clusterRecoveryRestoreConfirm");
      try {
        const result = await this.apiFetch("/cluster-recovery/restores", {
          method: "POST",
          body: {
            source_cluster_id: sourceClusterId,
            target_cluster_id: targetClusterId,
            backup_path: backupPath,
            restore_aost: restoreAost || null,
          },
        });
        this.closeClusterRecoveryRestoreConfirm();
        this.showNotice(
          `Cluster recovery requested for '${targetClusterId}' from '${sourceClusterId}'.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterRecoveryRestoreConfirm",
          e,
          "Failed to request cluster recovery.",
        );
      } finally {
        this.clusterRecoveryLoading.restore = false;
      }
    },

    async refreshClusterBackups() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;
      this.clusterBackupsLoading.snapshot = true;
      try {
        const snapshot = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/backups`,
          ),
          { method: "GET" },
        );
        this.clusterBackups = Array.isArray(snapshot?.backup_paths)
          ? snapshot.backup_paths
          : [];
        if (snapshot?.cluster) {
          this.selectedCluster = snapshot.cluster;
        }

        const previousSelectedBackupPath = this.selectedClusterBackupPath;
        const selectedStillExists = this.clusterBackups.some(
          (entry) =>
            String(entry?.path || "").trim() === this.selectedClusterBackupPath,
        );
        if (!selectedStillExists) {
          this.selectedClusterBackupPath = String(
            this.clusterBackups[0]?.path || "",
          ).trim();
          this.clusterBackupDetails = [];
        }

        this.clusterBackupsLastUpdatedUtc = this.utcNowString();
        if (
          this.view === "cluster_backups" &&
          previousSelectedBackupPath !== this.selectedClusterBackupPath
        ) {
          this.syncHashFromState(true);
        }
        if (this.selectedClusterBackupPath) {
          await this.refreshSelectedBackupDetails();
        }
      } catch (e) {
        console.error(e);
        this.clusterBackupsLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load cluster backups."),
        );
      } finally {
        this.clusterBackupsLoading.snapshot = false;
      }
    },

    async selectClusterBackup(path) {
      const normalizedPath = String(path || "").trim();
      if (!normalizedPath) return;
      this.selectedClusterBackupPath = normalizedPath;
      this.syncHashFromState();
      await this.refreshSelectedBackupDetails();
    },

    async refreshSelectedBackupDetails() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const backupPath = String(this.selectedClusterBackupPath || "").trim();
      if (!clusterId || !backupPath) return;
      this.clusterBackupsLoading.details = true;
      try {
        const details = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/backups/details`,
            { backup_path: backupPath },
          ),
          { method: "GET" },
        );
        this.clusterBackupDetails = Array.isArray(details) ? details : [];
      } catch (e) {
        console.error(e);
        this.showNotice(
          this.errorMessage(e, "Failed to load backup details."),
        );
        this.clusterBackupDetails = [];
      } finally {
        this.clusterBackupsLoading.details = false;
      }
    },

    backupObjectType(objectType) {
      return String(objectType || "").trim().toLowerCase();
    },

    backupObjectTypeLabel(objectType) {
      const normalized = this.backupObjectType(objectType);
      if (normalized === "database") return "Database";
      if (normalized === "table") return "Table";
      return normalized || "-";
    },

    clusterArtifactKindLabel(kind = this.selectedClusterArtifactKind) {
      const normalized = String(kind || "").trim().toLowerCase();
      if (normalized === "debug_zip") return "Debug ZIPs";
      return normalized ? normalized.replaceAll("_", " ") : "Artifacts";
    },

    formatBytes(bytes) {
      const value = Number(bytes);
      if (!Number.isFinite(value) || value <= 0) return "-";
      const units = ["B", "KB", "MB", "GB", "TB", "PB"];
      const exponent = Math.min(
        Math.floor(Math.log(value) / Math.log(1024)),
        units.length - 1,
      );
      const scaled = value / 1024 ** exponent;
      const rounded = exponent === 0 ? String(Math.round(scaled)) : scaled.toFixed(1);
      return `${rounded.endsWith(".0") ? rounded.slice(0, -2) : rounded} ${units[exponent]}`;
    },

    clusterArtifactRowText(row) {
      return [
        row?.artifact_name,
        row?.status,
        row?.kind,
        row?.job_id,
        row?.created_by,
        row?.sha256,
        this.toUtcStringMaybe(row?.created_at),
        this.toUtcStringMaybe(row?.expires_at),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    clusterArtifactCellText(row, colIndex) {
      switch (colIndex) {
        case 0:
          return row?.artifact_name || "";
        case 1:
          return row?.status || "";
        case 2:
          return row?.size_bytes ?? "";
        case 3:
          return row?.redacted ? "yes" : "no";
        case 4:
          return row?.created_at || "";
        case 5:
          return row?.expires_at || "";
        case 6:
          return row?.job_id ?? "";
        case 7:
          return row?.sha256 || "";
        default:
          return "";
      }
    },

    clusterArtifactsSortClass(index) {
      if (this.clusterArtifactsSortIndex !== index) return "";
      return this.clusterArtifactsSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleClusterArtifactsSort(index) {
      if (this.clusterArtifactsSortIndex === index)
        this.clusterArtifactsSortDir =
          this.clusterArtifactsSortDir === "asc" ? "desc" : "asc";
      else {
        this.clusterArtifactsSortIndex = index;
        this.clusterArtifactsSortDir = index >= 4 ? "desc" : "asc";
      }
      this.applyClusterArtifactsFilterSort();
    },

    applyClusterArtifactsFilterSort() {
      const q = String(this.clusterArtifactsFilterQuery || "")
        .trim()
        .toLowerCase();
      let rows = Array.isArray(this.clusterArtifacts)
        ? [...this.clusterArtifacts]
        : [];
      if (q) {
        rows = rows.filter((row) => this.clusterArtifactRowText(row).includes(q));
      }

      if (this.clusterArtifactsSortIndex !== null) {
        const type =
          this.clusterArtifactsSortTypeByIndex[this.clusterArtifactsSortIndex] ||
          "string";
        const idx = this.clusterArtifactsSortIndex;
        const dir = this.clusterArtifactsSortDir;
        rows.sort((a, b) => {
          const av = this.parseValue(type, this.clusterArtifactCellText(a, idx));
          const bv = this.parseValue(type, this.clusterArtifactCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }
      this.clusterArtifactsVisibleRows = rows;
    },

    async refreshClusterArtifacts() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      if (!clusterId) return;

      const kind = String(this.selectedClusterArtifactKind || "debug_zip").trim();
      this.clusterArtifactsLoading.list = true;
      try {
        const snapshot = await this.apiFetch(
          this.visibilityPath(
            `/clusters/${encodeURIComponent(clusterId)}/artifacts`,
            { kind },
          ),
          { method: "GET" },
        );
        this.clusterArtifacts = Array.isArray(snapshot?.artifacts)
          ? snapshot.artifacts
          : [];
        this.clusterArtifactsLastUpdatedUtc = this.utcNowString();
        this.applyClusterArtifactsFilterSort();
      } catch (e) {
        console.error(e);
        this.clearClusterArtifactsState();
        this.clusterArtifactsLastUpdatedUtc = this.utcNowString();
        this.showNotice(
          this.errorMessage(e, "Failed to load cluster artifacts."),
        );
      } finally {
        this.clusterArtifactsLoading.list = false;
      }
    },

    canDownloadClusterArtifact(row) {
      return String(row?.status || "").toUpperCase() === "READY";
    },

    async downloadClusterArtifact(row) {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const artifactId = String(row?.artifact_id || "").trim();
      if (!clusterId || !artifactId || !this.canDownloadClusterArtifact(row)) {
        return;
      }

      this.clusterArtifactsLoading.download = true;
      this.clusterArtifactDownloadingId = artifactId;
      try {
        const response = await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/artifacts/${encodeURIComponent(artifactId)}/download-url`,
          { method: "POST" },
        );
        const url = String(response?.url || "").trim();
        if (!url) throw new Error("Download URL was not returned.");

        if (typeof document !== "undefined") {
          const anchor = document.createElement("a");
          anchor.href = url;
          anchor.download = response?.artifact_name || row?.artifact_name || "";
          anchor.rel = "noopener";
          document.body.appendChild(anchor);
          anchor.click();
          document.body.removeChild(anchor);
        } else if (typeof window !== "undefined") {
          window.location.assign(url);
        }
        this.showNotice(
          `Download started for '${response?.artifact_name || row?.artifact_name || artifactId}'.`,
        );
      } catch (e) {
        console.error(e);
        this.showNotice(
          this.errorMessage(e, "Failed to create artifact download URL."),
        );
      } finally {
        this.clusterArtifactsLoading.download = false;
        this.clusterArtifactDownloadingId = "";
      }
    },

    backupRestoreObjectName(row) {
      const objectType = this.backupObjectType(row?.object_type);
      if (objectType === "table") {
        return [row?.database_name, row?.parent_schema_name, row?.object_name]
          .map((part) => String(part || "").trim())
          .filter(Boolean)
          .join(".");
      }
      if (objectType === "database") {
        return String(row?.database_name || row?.object_name || "").trim();
      }
      return String(row?.object_name || "").trim();
    },

    backupRestoreAostInputValue(value) {
      const raw = String(value || "").trim();
      if (!raw) return "";

      const parsed = new Date(raw);
      if (Number.isNaN(parsed.getTime())) {
        return raw.replace(" ", "T").slice(0, 19);
      }

      const pad = (part) => String(part).padStart(2, "0");
      return [
        parsed.getUTCFullYear(),
        "-",
        pad(parsed.getUTCMonth() + 1),
        "-",
        pad(parsed.getUTCDate()),
        "T",
        pad(parsed.getUTCHours()),
        ":",
        pad(parsed.getUTCMinutes()),
        ":",
        pad(parsed.getUTCSeconds()),
      ].join("");
    },

    backupRestoreAostApiValue(value) {
      return String(value || "").trim().replace("T", " ");
    },

    openClusterBackupObjectRestoreModal(row) {
      const objectType = this.backupObjectType(row?.object_type);
      const objectName = this.backupRestoreObjectName(row);
      if (!["database", "table"].includes(objectType) || !objectName) return;

      this.modal.clusterBackupObjectRestore.open = true;
      this.modal.clusterBackupObjectRestore.row = row || null;
      this.modal.clusterBackupObjectRestore.object_type = objectType;
      this.modal.clusterBackupObjectRestore.object_name = objectName;
      this.modal.clusterBackupObjectRestore.backup_path = String(
        this.selectedClusterBackupPath || "",
      ).trim();
      this.modal.clusterBackupObjectRestore.restore_aost =
        this.backupRestoreAostInputValue(row?.start_time);
      this.modal.clusterBackupObjectRestore.use_restore_option = false;
      this.modal.clusterBackupObjectRestore.into_db = "";
      this.modal.clusterBackupObjectRestore.new_db_name = "";
      this.clearModalError("clusterBackupObjectRestore");
    },

    closeClusterBackupObjectRestoreModal() {
      this.modal.clusterBackupObjectRestore.open = false;
      this.modal.clusterBackupObjectRestore.row = null;
      this.modal.clusterBackupObjectRestore.object_type = "";
      this.modal.clusterBackupObjectRestore.object_name = "";
      this.modal.clusterBackupObjectRestore.backup_path = "";
      this.modal.clusterBackupObjectRestore.restore_aost = "";
      this.modal.clusterBackupObjectRestore.use_restore_option = false;
      this.modal.clusterBackupObjectRestore.into_db = "";
      this.modal.clusterBackupObjectRestore.new_db_name = "";
      this.clearModalError("clusterBackupObjectRestore");
    },

    async restoreClusterBackupObject() {
      const clusterId = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const restore = this.modal.clusterBackupObjectRestore;
      const objectType = this.backupObjectType(restore.object_type);
      const objectName = String(restore.object_name || "").trim();
      const backupPath = String(restore.backup_path || "").trim();
      const restoreAost = this.backupRestoreAostApiValue(restore.restore_aost);
      const useRestoreOption = Boolean(restore.use_restore_option);
      const intoDb = String(restore.into_db || "").trim();
      const newDbName = String(restore.new_db_name || "").trim();

      if (!clusterId || !backupPath || !objectType || !objectName) return;
      this.clusterBackupsLoading.restore = true;
      this.clearModalError("clusterBackupObjectRestore");
      try {
        const body = {
          backup_path: backupPath,
          restore_aost: restoreAost || null,
          object_type: objectType,
          object_name: objectName,
          into_db:
            useRestoreOption && objectType === "table" && intoDb
              ? intoDb
              : null,
          new_db_name:
            useRestoreOption && objectType === "database" && newDbName
              ? newDbName
              : null,
        };
        const result = await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/restores/objects`,
          {
            method: "POST",
            body,
          },
        );
        this.closeClusterBackupObjectRestoreModal();
        this.showNotice(
          `Restore requested for ${this.backupObjectTypeLabel(objectType).toLowerCase()} '${objectName}'.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterBackupObjectRestore",
          e,
          "Failed to request object restore.",
        );
      } finally {
        this.clusterBackupsLoading.restore = false;
      }
    },

    async confirmClusterUpgrade() {
      const clusterName = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const version = String(this.modal.clusterUpgrade.version || "").trim();
      if (!clusterName || !version) return;

      this.clusterLoading.upgrade = true;
      this.clearModalError("clusterUpgrade");
      try {
        const result = await this.apiFetch(`/clusters/upgrade`, {
          method: "POST",
          body: {
            name: clusterName,
            version,
            auto_finalize: false,
          },
        });
        this.closeClusterUpgradeModal();
        this.showNotice(
          `Cluster '${clusterName}' upgrade requested to ${version}.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterUpgrade",
          e,
          "Failed to request cluster upgrade.",
        );
      } finally {
        this.clusterLoading.upgrade = false;
      }
    },

    async confirmClusterScale() {
      const clusterName = String(
        this.selectedCluster?.cluster_id || this.selectedClusterId || "",
      ).trim();
      const nodeCount = Number(this.modal.clusterScale.node_count);
      const nodeCpus = Number(this.modal.clusterScale.node_cpus);
      const diskSize = Number(this.modal.clusterScale.disk_size);
      const regions = this.normalizeRegionIds(
        this.clusterScaleSelectedRegions(),
        this.clusterScaleRegionOptions(),
      );
      if (!clusterName) return;

      if (!Number.isFinite(nodeCount) || nodeCount <= 0) {
        this.setModalError(
          "clusterScale",
          new Error("Node count is required."),
          "Node count is required.",
        );
        return;
      }
      if (!Number.isFinite(nodeCpus) || nodeCpus <= 0) {
        this.setModalError(
          "clusterScale",
          new Error("Node vCPUs is required."),
          "Node vCPUs is required.",
        );
        return;
      }
      if (!Number.isFinite(diskSize) || diskSize <= 0) {
        this.setModalError(
          "clusterScale",
          new Error("Disk size is required."),
          "Disk size is required.",
        );
        return;
      }
      if (regions.length === 0) {
        this.setModalError(
          "clusterScale",
          new Error("Select at least one region."),
          "Select at least one region.",
        );
        return;
      }
      if (regions.length * nodeCount < 3) {
        this.setModalError(
          "clusterScale",
          new Error(
            "Selected regions multiplied by node count must be at least 3.",
          ),
          "Selected regions multiplied by node count must be at least 3.",
        );
        return;
      }

      this.clusterLoading.scale = true;
      this.clearModalError("clusterScale");
      try {
        const result = await this.apiFetch(`/clusters/scale`, {
          method: "POST",
          body: {
            name: clusterName,
            node_count: nodeCount,
            node_cpus: nodeCpus,
            disk_size: diskSize,
            regions,
          },
        });
        this.closeClusterScaleModal();
        this.showNotice(
          `Cluster '${clusterName}' scale requested.`,
          { jobId: result?.job_id },
        );
      } catch (e) {
        this.setModalError(
          "clusterScale",
          e,
          "Failed to request cluster scale.",
        );
      } finally {
        this.clusterLoading.scale = false;
      }
    },



























    alertsRowText(alert) {
      return [
        alert?.starts_at,
        alert?.alert_type,
        alert?.cluster,
        alert?.nodes_text,
        alert?.summary,
        alert?.description,
        alert?.ends_at,
        alert?.fingerprint,
        this.relativeTimeFromNow(alert?.starts_at),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    alertsCellText(alert, colIndex) {
      switch (colIndex) {
        case 0:
          return alert?.starts_at || "";
        case 1:
          return alert?.alert_type || "";
        case 2:
          return alert?.cluster || "";
        case 3:
          return alert?.nodes_text || "";
        case 4:
          return alert?.summary || "";
        case 5:
          return alert?.ends_at || "";
        case 6:
          return alert?.starts_at || "";
        default:
          return "";
      }
    },

    alertsSortClass(index) {
      if (this.alertsSortIndex !== index) return "";
      return this.alertsSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleAlertsSort(index) {
      if (this.alertsSortIndex === index)
        this.alertsSortDir = this.alertsSortDir === "asc" ? "desc" : "asc";
      else {
        this.alertsSortIndex = index;
        this.alertsSortDir = index === 0 ? "desc" : "asc";
      }

      localStorage.setItem(
        "cp_alerts_sort_index",
        String(this.alertsSortIndex),
      );
      localStorage.setItem("cp_alerts_sort_dir", this.alertsSortDir);
      this.applyAlertsFilterSort();
    },

    applyAlertsFilterSort() {
      const q = (this.alertsFilterQuery || "").toLowerCase().trim();
      let rows = this.alerts.slice();
      if (q) rows = rows.filter((alert) => this.alertsRowText(alert).includes(q));

      if (this.alertsSortIndex !== null) {
        const type =
          this.alertsSortTypeByIndex[this.alertsSortIndex] || "string";
        const idx = this.alertsSortIndex;
        const dir = this.alertsSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.alertsCellText(a, idx));
          const bv = this.parseValue(type, this.alertsCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.alertsVisibleRows = rows;
    },

    async refreshAlerts({ limit = null } = {}) {
      this.alertsLoading.list = true;
      try {
        const path =
          limit === null
            ? "/alerts/"
            : this.visibilityPath("/alerts/", { limit });
        const data = await this.apiFetch(path, { method: "GET" });
        this.alerts = Array.isArray(data)
          ? data.map((alert) => this.normalizeAlertRow(alert))
          : [];
        this.alertsLastUpdatedUtc = this.utcNowString();
        this.applyAlertsFilterSort();
      } catch (e) {
        console.error(e);
        this.alertsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.alertsLoading.list = false;
      }
    },
















    maskedSecret(secret) {
      const value = String(secret || "");
      return value ? "•".repeat(Math.max(24, value.length)) : "";
    },




    versionsRowText(row) {
      return String(row?.version || "").toLowerCase();
    },

    applyVersionsFilter() {
      const q = (this.versionsFilterQuery || "").toLowerCase().trim();
      let rows = this.versions.slice();
      if (q) rows = rows.filter((row) => this.versionsRowText(row).includes(q));
      rows.sort((a, b) =>
        String(a.version || "").localeCompare(String(b.version || "")),
      );
      this.versionsVisibleRows = rows;
    },

    persistVersionsFilter() {
      localStorage.setItem(
        "cp_versions_filter",
        this.versionsFilterQuery || "",
      );
    },

    openVersionCreateModal() {
      this.modal.versionCreate.version = "";
      this.clearModalError("versionCreate");
      this.modal.versionCreate.open = true;
    },

    closeVersionCreateModal() {
      this.modal.versionCreate.open = false;
      this.modal.versionCreate.version = "";
      this.clearModalError("versionCreate");
    },

    async createVersion() {
      const version = String(this.modal.versionCreate.version || "").trim();
      if (!version) {
        this.setModalError(
          "versionCreate",
          new Error("Version is required."),
          "Version is required.",
        );
        return;
      }

      this.versionsLoading.create = true;
      this.clearModalError("versionCreate");
      try {
        await this.apiFetch("/admin/versions/", {
          method: "POST",
          body: { version },
        });
        this.closeVersionCreateModal();
        await this.refreshVersions();
        this.showNotice(`Version '${version}' created.`);
      } catch (e) {
        this.setModalError("versionCreate", e, "Failed to create version.");
      } finally {
        this.versionsLoading.create = false;
      }
    },

    openVersionDeleteConfirm(row) {
      this.modal.versionDeleteConfirm.version = row?.version || "";
      this.clearModalError("versionDeleteConfirm");
      this.modal.versionDeleteConfirm.open = true;
    },

    closeVersionDeleteConfirm() {
      this.modal.versionDeleteConfirm.open = false;
      this.modal.versionDeleteConfirm.version = "";
      this.clearModalError("versionDeleteConfirm");
    },

    async confirmVersionDelete() {
      const version = String(
        this.modal.versionDeleteConfirm.version || "",
      ).trim();
      if (!version) return;

      this.versionsLoading.delete = true;
      this.clearModalError("versionDeleteConfirm");
      try {
        await this.apiFetch(`/admin/versions/${encodeURIComponent(version)}`, {
          method: "DELETE",
        });
        this.closeVersionDeleteConfirm();
        await this.refreshVersions();
        this.showNotice(`Version '${version}' deleted.`);
      } catch (e) {
        this.setModalError(
          "versionDeleteConfirm",
          e,
          "Failed to delete version.",
        );
      } finally {
        this.versionsLoading.delete = false;
      }
    },

    async refreshVersions() {
      this.versionsLoading.list = true;
      try {
        const data = await this.apiFetch("/admin/versions/", { method: "GET" });
        this.versions = Array.isArray(data) ? data : [];
        this.versionsLastUpdatedUtc = this.utcNowString();
        this.applyVersionsFilter();
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView("versions", { fallback: false });
        }
        console.error(e);
        this.versionsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.versionsLoading.list = false;
      }
    },

    clusterOptionConfig(kind) {
      const configs = {
        node_counts: {
          listProp: "nodeCounts",
          visibleProp: "nodeCountsVisibleRows",
          filterProp: "nodeCountsFilterQuery",
          updatedProp: "nodeCountsLastUpdatedUtc",
          loadingProp: "nodeCountsLoading",
          endpoint: "/admin/node_counts/",
          key: "node_count",
          singularLabel: "Node count",
          pluralLabel: "Node counts",
          storageKey: "cp_node_counts_filter",
          createModal: "nodeCountCreate",
          deleteModal: "nodeCountDeleteConfirm",
          createErrorKey: "nodeCountCreate",
          deleteErrorKey: "nodeCountDeleteConfirm",
          forbiddenView: "node_counts",
        },
        cpu_counts: {
          listProp: "cpuCounts",
          visibleProp: "cpuCountsVisibleRows",
          filterProp: "cpuCountsFilterQuery",
          updatedProp: "cpuCountsLastUpdatedUtc",
          loadingProp: "cpuCountsLoading",
          endpoint: "/admin/cpu_counts/",
          key: "cpu_count",
          singularLabel: "CPU count",
          pluralLabel: "CPU counts",
          storageKey: "cp_cpu_counts_filter",
          createModal: "cpuCountCreate",
          deleteModal: "cpuCountDeleteConfirm",
          createErrorKey: "cpuCountCreate",
          deleteErrorKey: "cpuCountDeleteConfirm",
          forbiddenView: "cpu_counts",
        },
        disk_sizes: {
          listProp: "diskSizes",
          visibleProp: "diskSizesVisibleRows",
          filterProp: "diskSizesFilterQuery",
          updatedProp: "diskSizesLastUpdatedUtc",
          loadingProp: "diskSizesLoading",
          endpoint: "/admin/disk_sizes/",
          key: "size_gb",
          singularLabel: "Disk size",
          pluralLabel: "Disk sizes",
          storageKey: "cp_disk_sizes_filter",
          createModal: "diskSizeCreate",
          deleteModal: "diskSizeDeleteConfirm",
          createErrorKey: "diskSizeCreate",
          deleteErrorKey: "diskSizeDeleteConfirm",
          forbiddenView: "disk_sizes",
        },
      };
      return configs[kind];
    },

    clusterOptionRowValue(kind, row) {
      const config = this.clusterOptionConfig(kind);
      return Number(row?.[config?.key]);
    },

    applyClusterOptionFilter(kind) {
      const config = this.clusterOptionConfig(kind);
      const q = String(this[config.filterProp] || "").toLowerCase().trim();
      let rows = this[config.listProp].slice();
      if (q) {
        rows = rows.filter((row) =>
          String(this.clusterOptionRowValue(kind, row)).toLowerCase().includes(q),
        );
      }
      rows.sort(
        (a, b) =>
          this.clusterOptionRowValue(kind, a) -
          this.clusterOptionRowValue(kind, b),
      );
      this[config.visibleProp] = rows;
    },

    persistClusterOptionFilter(kind) {
      const config = this.clusterOptionConfig(kind);
      localStorage.setItem(config.storageKey, this[config.filterProp] || "");
    },

    openClusterOptionCreateModal(kind) {
      const config = this.clusterOptionConfig(kind);
      this.modal[config.createModal][config.key] = "";
      this.clearModalError(config.createErrorKey);
      this.modal[config.createModal].open = true;
    },

    closeClusterOptionCreateModal(kind) {
      const config = this.clusterOptionConfig(kind);
      this.modal[config.createModal].open = false;
      this.modal[config.createModal][config.key] = "";
      this.clearModalError(config.createErrorKey);
    },

    openClusterOptionDeleteConfirm(kind, row) {
      const config = this.clusterOptionConfig(kind);
      this.modal[config.deleteModal][config.key] = row?.[config.key] ?? "";
      this.clearModalError(config.deleteErrorKey);
      this.modal[config.deleteModal].open = true;
    },

    closeClusterOptionDeleteConfirm(kind) {
      const config = this.clusterOptionConfig(kind);
      this.modal[config.deleteModal].open = false;
      this.modal[config.deleteModal][config.key] = "";
      this.clearModalError(config.deleteErrorKey);
    },

    async createClusterOption(kind) {
      const config = this.clusterOptionConfig(kind);
      const rawValue = this.modal[config.createModal][config.key];
      const value = Number.parseInt(String(rawValue || "").trim(), 10);
      if (!Number.isFinite(value) || value <= 0) {
        this.setModalError(
          config.createErrorKey,
          new Error(`${config.singularLabel} must be a positive integer.`),
          `${config.singularLabel} must be a positive integer.`,
        );
        return;
      }

      this[config.loadingProp].create = true;
      this.clearModalError(config.createErrorKey);
      try {
        await this.apiFetch(config.endpoint, {
          method: "POST",
          body: { [config.key]: value },
        });
        this.closeClusterOptionCreateModal(kind);
        await this.refreshClusterOption(kind);
        this.showNotice(`${config.singularLabel} '${value}' created.`);
      } catch (e) {
        this.setModalError(
          config.createErrorKey,
          e,
          `Failed to create ${config.singularLabel.toLowerCase()}.`,
        );
      } finally {
        this[config.loadingProp].create = false;
      }
    },

    async confirmClusterOptionDelete(kind) {
      const config = this.clusterOptionConfig(kind);
      const value = Number.parseInt(
        String(this.modal[config.deleteModal][config.key] || "").trim(),
        10,
      );
      if (!Number.isFinite(value) || value <= 0) return;

      this[config.loadingProp].delete = true;
      this.clearModalError(config.deleteErrorKey);
      try {
        await this.apiFetch(`${config.endpoint}${encodeURIComponent(value)}`, {
          method: "DELETE",
        });
        this.closeClusterOptionDeleteConfirm(kind);
        await this.refreshClusterOption(kind);
        this.showNotice(`${config.singularLabel} '${value}' deleted.`);
      } catch (e) {
        this.setModalError(
          config.deleteErrorKey,
          e,
          `Failed to delete ${config.singularLabel.toLowerCase()}.`,
        );
      } finally {
        this[config.loadingProp].delete = false;
      }
    },

    async refreshClusterOption(kind) {
      const config = this.clusterOptionConfig(kind);
      this[config.loadingProp].list = true;
      try {
        const data = await this.apiFetch(config.endpoint, { method: "GET" });
        this[config.listProp] = Array.isArray(data) ? data : [];
        this[config.updatedProp] = this.utcNowString();
        this.applyClusterOptionFilter(kind);
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView(config.forbiddenView, { fallback: false });
        }
        console.error(e);
        this[config.updatedProp] = this.utcNowString();
      } finally {
        this[config.loadingProp].list = false;
      }
    },

    applyNodeCountsFilter() {
      this.applyClusterOptionFilter("node_counts");
    },

    persistNodeCountsFilter() {
      this.persistClusterOptionFilter("node_counts");
    },

    openNodeCountCreateModal() {
      this.openClusterOptionCreateModal("node_counts");
    },

    closeNodeCountCreateModal() {
      this.closeClusterOptionCreateModal("node_counts");
    },

    openNodeCountDeleteConfirm(row) {
      this.openClusterOptionDeleteConfirm("node_counts", row);
    },

    closeNodeCountDeleteConfirm() {
      this.closeClusterOptionDeleteConfirm("node_counts");
    },

    async createNodeCount() {
      await this.createClusterOption("node_counts");
    },

    async confirmNodeCountDelete() {
      await this.confirmClusterOptionDelete("node_counts");
    },

    async refreshNodeCounts() {
      await this.refreshClusterOption("node_counts");
    },

    applyCpuCountsFilter() {
      this.applyClusterOptionFilter("cpu_counts");
    },

    persistCpuCountsFilter() {
      this.persistClusterOptionFilter("cpu_counts");
    },

    openCpuCountCreateModal() {
      this.openClusterOptionCreateModal("cpu_counts");
    },

    closeCpuCountCreateModal() {
      this.closeClusterOptionCreateModal("cpu_counts");
    },

    openCpuCountDeleteConfirm(row) {
      this.openClusterOptionDeleteConfirm("cpu_counts", row);
    },

    closeCpuCountDeleteConfirm() {
      this.closeClusterOptionDeleteConfirm("cpu_counts");
    },

    async createCpuCount() {
      await this.createClusterOption("cpu_counts");
    },

    async confirmCpuCountDelete() {
      await this.confirmClusterOptionDelete("cpu_counts");
    },

    async refreshCpuCounts() {
      await this.refreshClusterOption("cpu_counts");
    },

    applyDiskSizesFilter() {
      this.applyClusterOptionFilter("disk_sizes");
    },

    persistDiskSizesFilter() {
      this.persistClusterOptionFilter("disk_sizes");
    },

    openDiskSizeCreateModal() {
      this.openClusterOptionCreateModal("disk_sizes");
    },

    closeDiskSizeCreateModal() {
      this.closeClusterOptionCreateModal("disk_sizes");
    },

    openDiskSizeDeleteConfirm(row) {
      this.openClusterOptionDeleteConfirm("disk_sizes", row);
    },

    closeDiskSizeDeleteConfirm() {
      this.closeClusterOptionDeleteConfirm("disk_sizes");
    },

    async createDiskSize() {
      await this.createClusterOption("disk_sizes");
    },

    async confirmDiskSizeDelete() {
      await this.confirmClusterOptionDelete("disk_sizes");
    },

    async refreshDiskSizes() {
      await this.refreshClusterOption("disk_sizes");
    },

    databaseRoleTemplatesRowText(row) {
      return [row?.database_role_template, row?.scope_type, row?.sql_statement]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    applyDatabaseRoleTemplatesFilter() {
      const q = String(this.databaseRoleTemplatesFilterQuery || "")
        .toLowerCase()
        .trim();
      let rows = Array.isArray(this.databaseRoleTemplates)
        ? this.databaseRoleTemplates.slice()
        : [];
      if (q) {
        rows = rows.filter((row) => this.databaseRoleTemplatesRowText(row).includes(q));
      }
      rows.sort((a, b) =>
        String(a?.database_role_template || "").localeCompare(
          String(b?.database_role_template || ""),
        ),
      );
      this.databaseRoleTemplatesVisibleRows = rows;
    },

    formatSqlStatement(sqlStatement) {
      return String(sqlStatement || "")
        .replace(/;\s*/g, ";\n")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
    },

    persistDatabaseRoleTemplatesFilter() {
      localStorage.setItem(
        "cp_database_role_templates_filter",
        this.databaseRoleTemplatesFilterQuery || "",
      );
    },

    openDatabaseRoleTemplateCreateModal() {
      this.modal.databaseRoleTemplateCreate.database_role_template = "";
      this.modal.databaseRoleTemplateCreate.scope_type = "schema";
      this.modal.databaseRoleTemplateCreate.sql_statement =
        "CREATE ROLE IF NOT EXISTS {database_role};";
      this.clearModalError("databaseRoleTemplateCreate");
      this.modal.databaseRoleTemplateCreate.open = true;
      this.$nextTick(() => {
        this.ensureDatabaseRoleTemplateAce();
        if (this._databaseRoleTemplateAceReady && this._databaseRoleTemplateAce) {
          if (typeof this.setAceValue === "function") {
            this.setAceValue(
              this._databaseRoleTemplateAce,
              this.modal.databaseRoleTemplateCreate.sql_statement,
            );
          }
          this._databaseRoleTemplateAce.resize();
          this._databaseRoleTemplateAce.focus();
        }
      });
    },

    closeDatabaseRoleTemplateCreateModal() {
      this.modal.databaseRoleTemplateCreate.open = false;
      this.modal.databaseRoleTemplateCreate.database_role_template = "";
      this.modal.databaseRoleTemplateCreate.scope_type = "schema";
      this.modal.databaseRoleTemplateCreate.sql_statement =
        "CREATE ROLE IF NOT EXISTS {database_role};";
      this.clearModalError("databaseRoleTemplateCreate");
    },

    openDatabaseRoleTemplateDeleteConfirm(row) {
      this.modal.databaseRoleTemplateDeleteConfirm.database_role_template = String(
        row?.database_role_template || "",
      );
      this.clearModalError("databaseRoleTemplateDeleteConfirm");
      this.modal.databaseRoleTemplateDeleteConfirm.open = true;
    },

    closeDatabaseRoleTemplateDeleteConfirm() {
      this.modal.databaseRoleTemplateDeleteConfirm.open = false;
      this.modal.databaseRoleTemplateDeleteConfirm.database_role_template = "";
      this.clearModalError("databaseRoleTemplateDeleteConfirm");
    },

    async createDatabaseRoleTemplate() {
      const databaseRoleTemplate = String(
        this.modal.databaseRoleTemplateCreate.database_role_template || "",
      ).trim();
      const sqlStatement = String(
        this._databaseRoleTemplateAceReady && this._databaseRoleTemplateAce
          ? this._databaseRoleTemplateAce.getValue()
          : this.modal.databaseRoleTemplateCreate.sql_statement || "",
      ).trim();
      const scopeType = String(
        this.modal.databaseRoleTemplateCreate.scope_type || "schema",
      ).trim();
      if (!databaseRoleTemplate) {
        this.setModalError(
          "databaseRoleTemplateCreate",
          new Error("Database role template is required."),
          "Database role template is required.",
        );
        return;
      }
      if (!sqlStatement) {
        this.setModalError(
          "databaseRoleTemplateCreate",
          new Error("SQL statement is required."),
          "SQL statement is required.",
        );
        return;
      }

      this.databaseRoleTemplatesLoading.create = true;
      this.clearModalError("databaseRoleTemplateCreate");
      try {
        await this.apiFetch("/admin/database_role_templates/", {
          method: "POST",
          body: {
            database_role_template: databaseRoleTemplate,
            scope_type: scopeType,
            sql_statement: this.formatSqlStatement(sqlStatement),
          },
        });
        this.closeDatabaseRoleTemplateCreateModal();
        await this.refreshDatabaseRoleTemplates();
        this.showNotice(`Database role template '${databaseRoleTemplate}' created.`);
      } catch (e) {
        this.setModalError(
          "databaseRoleTemplateCreate",
          e,
          "Failed to create database role template.",
        );
      } finally {
        this.databaseRoleTemplatesLoading.create = false;
      }
    },

    async confirmDatabaseRoleTemplateDelete() {
      const databaseRoleTemplate = String(
        this.modal.databaseRoleTemplateDeleteConfirm.database_role_template || "",
      ).trim();
      if (!databaseRoleTemplate) return;

      this.databaseRoleTemplatesLoading.delete = true;
      this.clearModalError("databaseRoleTemplateDeleteConfirm");
      try {
        await this.apiFetch(
          `/admin/database_role_templates/${encodeURIComponent(databaseRoleTemplate)}`,
          { method: "DELETE" },
        );
        this.closeDatabaseRoleTemplateDeleteConfirm();
        await this.refreshDatabaseRoleTemplates();
        this.showNotice(`Database role template '${databaseRoleTemplate}' deleted.`);
      } catch (e) {
        this.setModalError(
          "databaseRoleTemplateDeleteConfirm",
          e,
          "Failed to delete database role template.",
        );
      } finally {
        this.databaseRoleTemplatesLoading.delete = false;
      }
    },

    async refreshDatabaseRoleTemplates() {
      this.databaseRoleTemplatesLoading.list = true;
      try {
        const data = await this.apiFetch("/admin/database_role_templates/", {
          method: "GET",
        });
        this.databaseRoleTemplates = Array.isArray(data) ? data : [];
        this.databaseRoleTemplatesLastUpdatedUtc = this.utcNowString();
        this.applyDatabaseRoleTemplatesFilter();
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView("database_role_templates", { fallback: false });
        }
        console.error(e);
        this.databaseRoleTemplatesLastUpdatedUtc = this.utcNowString();
      } finally {
        this.databaseRoleTemplatesLoading.list = false;
      }
    },

    regionsRowText(row) {
      return [
        row?.cloud,
        row?.region,
        row?.zone,
        row?.vpc_id,
        Array.isArray(row?.security_groups)
          ? row.security_groups.join(" ")
          : "",
        row?.subnet,
        row?.image,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    applyRegionsFilter() {
      const q = (this.regionsFilterQuery || "").toLowerCase().trim();
      let rows = this.regions.slice();
      if (q) rows = rows.filter((row) => this.regionsRowText(row).includes(q));
      rows.sort((a, b) =>
        `${a.cloud || ""}/${a.region || ""}/${a.zone || ""}`.localeCompare(
          `${b.cloud || ""}/${b.region || ""}/${b.zone || ""}`,
        ),
      );
      this.regionsVisibleRows = rows;
    },

    persistRegionsFilter() {
      localStorage.setItem("cp_regions_filter", this.regionsFilterQuery || "");
    },

    openRegionCreateModal() {
      this.modal.regionCreate.cloud = "";
      this.modal.regionCreate.region = "";
      this.modal.regionCreate.zone = "";
      this.modal.regionCreate.vpc_id = "";
      this.modal.regionCreate.security_groups_text = "";
      this.modal.regionCreate.subnet = "";
      this.modal.regionCreate.image = "";
      this.modal.regionCreate.extras_text = "{}";
      this.clearModalError("regionCreate");
      this.modal.regionCreate.open = true;
    },

    closeRegionCreateModal() {
      this.modal.regionCreate.open = false;
      this.clearModalError("regionCreate");
    },

    async createRegion() {
      this.regionsLoading.create = true;
      this.clearModalError("regionCreate");
      try {
        const cloud = String(this.modal.regionCreate.cloud || "").trim();
        const region = String(this.modal.regionCreate.region || "").trim();
        const zone = String(this.modal.regionCreate.zone || "").trim();
        const vpc_id = String(this.modal.regionCreate.vpc_id || "").trim();
        const subnet = String(this.modal.regionCreate.subnet || "").trim();
        const image = String(this.modal.regionCreate.image || "").trim();

        if (!cloud || !region || !zone || !vpc_id || !subnet || !image) {
          throw new Error(
            "cloud, region, zone, vpc_id, subnet, and image are required.",
          );
        }

        const security_groups = String(
          this.modal.regionCreate.security_groups_text || "",
        )
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean);

        const extrasText =
          String(this.modal.regionCreate.extras_text || "{}").trim() || "{}";
        const extras = JSON.parse(extrasText);
        if (!extras || typeof extras !== "object" || Array.isArray(extras)) {
          throw new Error("extras must be a JSON object.");
        }

        await this.apiFetch("/admin/regions/", {
          method: "POST",
          body: {
            cloud,
            region,
            zone,
            vpc_id,
            security_groups,
            subnet,
            image,
            extras,
          },
        });
        this.closeRegionCreateModal();
        await this.refreshRegions();
        this.showNotice(`Region '${cloud}/${region}/${zone}' created.`);
      } catch (e) {
        this.setModalError("regionCreate", e, "Failed to create region.");
      } finally {
        this.regionsLoading.create = false;
      }
    },

    openRegionDeleteConfirm(row) {
      this.modal.regionDeleteConfirm.cloud = row?.cloud || "";
      this.modal.regionDeleteConfirm.region = row?.region || "";
      this.modal.regionDeleteConfirm.zone = row?.zone || "";
      this.clearModalError("regionDeleteConfirm");
      this.modal.regionDeleteConfirm.open = true;
    },

    closeRegionDeleteConfirm() {
      this.modal.regionDeleteConfirm.open = false;
      this.modal.regionDeleteConfirm.cloud = "";
      this.modal.regionDeleteConfirm.region = "";
      this.modal.regionDeleteConfirm.zone = "";
      this.clearModalError("regionDeleteConfirm");
    },

    async confirmRegionDelete() {
      const cloud = String(this.modal.regionDeleteConfirm.cloud || "").trim();
      const region = String(this.modal.regionDeleteConfirm.region || "").trim();
      const zone = String(this.modal.regionDeleteConfirm.zone || "").trim();
      if (!cloud || !region || !zone) return;

      this.regionsLoading.delete = true;
      this.clearModalError("regionDeleteConfirm");
      try {
        await this.apiFetch(
          `/admin/regions/${encodeURIComponent(cloud)}/${encodeURIComponent(region)}/${encodeURIComponent(zone)}`,
          { method: "DELETE" },
        );
        this.closeRegionDeleteConfirm();
        await this.refreshRegions();
        this.showNotice(`Region '${cloud}/${region}/${zone}' deleted.`);
      } catch (e) {
        this.setModalError(
          "regionDeleteConfirm",
          e,
          "Failed to delete region.",
        );
      } finally {
        this.regionsLoading.delete = false;
      }
    },

    async refreshRegions() {
      this.regionsLoading.list = true;
      try {
        const data = await this.apiFetch("/admin/regions/", { method: "GET" });
        this.regions = Array.isArray(data) ? data : [];
        this.regionsLastUpdatedUtc = this.utcNowString();
        this.applyRegionsFilter();
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView("regions", { fallback: false });
        }
        console.error(e);
        this.regionsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.regionsLoading.list = false;
      }
    },

    // ---------- Stored filters ----------
    persistServersFilter() {
      localStorage.setItem("cp_servers_filter", this.serversFilterQuery || "");
    },

    persistAlertsFilter() {
      localStorage.setItem("cp_alerts_filter", this.alertsFilterQuery || "");
    },

    // ---------- Shared table sorting ----------
    parseValue(type, value) {
      const v = (value ?? "").toString().trim();
      if (type === "number") {
        const n = parseFloat(v);
        return Number.isFinite(n) ? n : Number.NEGATIVE_INFINITY;
      }
      if (type === "date") {
        const d = new Date(v);
        return isNaN(d.getTime()) ? 0 : d.getTime();
      }
      if (type === "ip") {
        return v
          .split(".")
          .map((o) => o.padStart(3, "0"))
          .join(".");
      }
      return v.toLowerCase();
    },

    ensureDatabaseRoleTemplateAce() {
      if (this._databaseRoleTemplateAceReady) return;

      const editorNode =
        this.$refs.databaseRoleTemplateSqlEditor ||
        document.getElementById("databaseRoleTemplateSqlEditor");

      if (typeof this.createAceEditor !== "function") return;

      const editor = this.createAceEditor(editorNode, {
        mode: "sql",
        value: this.modal.databaseRoleTemplateCreate.sql_statement,
        minLines: 10,
        maxLines: 18,
        onChange: (value) => {
          this.modal.databaseRoleTemplateCreate.sql_statement = value;
        },
      });
      if (!editor) return;

      this._databaseRoleTemplateAce = editor;
      this._databaseRoleTemplateAceReady = true;
    },

    renderDatabaseRoleTemplateSqlEditors() {
      document.querySelectorAll(".sql-preview-editor").forEach((node) => {
        node.textContent = this.formatSqlStatement(
          node.dataset.databaseRoleTemplateSql || "-",
        );
      });
    },

  };
}

(function () {
  // ---------- cpkit extension registration ----------
  const CP_ADMIN_VIEWS = new Set([
    "versions",
    "node_counts",
    "cpu_counts",
    "disk_sizes",
    "database_role_templates",
    "regions",
  ]);

  const EXCLUDED_EXTENSION_METHODS = new Set(["init"]);
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
    "showNotice",
    "clearNotice",
    "canAccessView",
    "handleForbiddenView",
    "viewLabel",
    "safeJson",
    "formatJson",
    "rolesText",
    "openUserInfoModal",
    "closeUserInfoModal",
  ]);
  const CPKIT_MODAL_KEYS = new Set([
    "userInfo",
  ]);

  function loadCPExtensionParts() {
    return createCPExtensionParts();
  }

  function splitExtensionParts(extensionParts) {
    const state = {};
    const methods = {};
    for (const [key, value] of Object.entries(extensionParts)) {
      if (typeof value === "function") {
        if (!EXCLUDED_EXTENSION_METHODS.has(key) && !CPKIT_METHODS.has(key)) methods[key] = value;
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

  const extensionAssetPromises = {};

  function ensureStylesheet(href) {
    if (typeof document === "undefined") return Promise.resolve();
    if ([...document.styleSheets].some((sheet) => sheet.href === href)) {
      return Promise.resolve();
    }
    if ([...document.links].some((link) => link.href === href)) {
      return Promise.resolve();
    }
    if (extensionAssetPromises[href]) return extensionAssetPromises[href];

    extensionAssetPromises[href] = new Promise((resolve) => {
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.onload = () => resolve();
      link.onerror = () => resolve();
      document.head.appendChild(link);
    });
    return extensionAssetPromises[href];
  }

  function ensureScript(src) {
    if (typeof document === "undefined") return Promise.resolve();
    if ([...document.scripts].some((script) => script.src === src)) {
      return Promise.resolve();
    }
    if (extensionAssetPromises[src]) return extensionAssetPromises[src];

    extensionAssetPromises[src] = new Promise((resolve) => {
      const script = document.createElement("script");
      script.src = src;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => resolve();
      document.head.appendChild(script);
    });
    return extensionAssetPromises[src];
  }

  function ensureUPlotAssets() {
    return Promise.all([
      ensureStylesheet("https://cdn.jsdelivr.net/npm/uplot@1.6.32/dist/uPlot.min.css"),
      ensureScript("https://cdn.jsdelivr.net/npm/uplot@1.6.32/dist/uPlot.iife.min.js"),
    ]);
  }

  function preloadAppStaticAssets(assetPaths = []) {
    assetPaths.forEach((assetPath) => {
      const normalized = String(assetPath || "").trim().replace(/^\/+/, "");
      if (!normalized) return;
      const image = new Image();
      image.src = `/app/static/${normalized}`;
    });
  }

  const extensionParts = splitExtensionParts(loadCPExtensionParts());

  window.cpkitWebappExtension = {
    htmlPath: "/app/extension.html",
    dashboardEnsure: "ensureCPDashboard",
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
    state: extensionParts.state,
    methods: {
      ...extensionParts.methods,
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
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
        this.clearNotice();
        this.setClusterHash(this.selectedClusterId, "recovery");
        if (!this.clusterLoading.details) await this.refreshSelectedCluster();
        await this.refreshClusterRecoveryBackups();
      },
      isAdminSectionView(viewName = this.view) {
        return CP_ADMIN_VIEWS.has(viewName) || viewName === "admin";
      },
    },
    async init() {
      ensureUPlotAssets();
      preloadAppStaticAssets([
        ...((this.cloudLogoKeys || []).map((key) => `${key}.png`)),
        "favicon.png",
        "logo.png",
      ]);
    },
  };
})();
