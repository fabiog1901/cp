// CP webapp state and interaction layer.
//
// This file owns Alpine state, hash routing, API calls, filtering/sorting, and
// UI-specific data shaping. Backend authorization and business rules must remain
// enforced by the API/service layer.

window.app = function () {
  return {
    // Tabs
    view: "dashboard",
    apiBase: "/api",
    authChecked: false,
    isAuthenticated: false,
    authClaims: null,
    authLoginPath: "/api/auth/login",
    authDisplayNameClaim: "preferred_username",
    authSessionCookieName: "cp_session",
    authError: "",
    viewNotice: "",
    viewNoticeJobId: "",
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

    // ---------- Dashboard state ----------
    computeUnits: [],
    visibleRows: [],
    filterQuery: "",
    lastUpdatedUtc: null,

    inspector: null,
    inspectorFormat: "yaml",

    sortIndex: null,
    sortDir: "asc",
    sortTypeByIndex: {
      0: "string", // deployment_id
      1: "string", // compute_id
      2: "string", // region-zone
      3: "string", // hostname
      4: "ip",
      5: "number",
      6: "string",
      7: "string",
      8: "date",
      9: "string", // status
    },

    loading: {
      list: false,
      allocate: false,
      init: false,
      decommission: false,
      deallocateConfirm: false,
    },
    busyKey: null,
    autoRefreshEnabled: true,
    _autoTimer: null,

    modal: {
      allocate: {
        open: false,
        cpu_count: null,
        region: "",
        zone: "",
        compute_id: "",
        tagsText: "{}",
        ssh_public_key: "",
      },
      init: {
        open: false,
        ip: "",
        region: "",
        zone: "",
        hostname: "",
        cpuRangesText: '["0-3"]',
      },
      decommission: { open: false, hostname: "" },
      deallocateConfirm: { open: false, compute_id: "", hostname: "" },
      computeDetails: { open: false, row: null },
      userInfo: { open: false },
      serverActionConfirm: {
        open: false,
        hostname: "",
        action: "decommission",
      },
      serverDetails: { open: false, row: null },
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
      allocate: "",
      init: "",
      decommission: "",
      deallocateConfirm: "",
      serverActionConfirm: "",
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

    utcNowString() {
      return new Date()
        .toISOString()
        .replace("T", " ")
        .replace(/\.\d{3}Z$/, "");
    },

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

    toUtcStringMaybe(value) {
      if (!value) return "-";
      const d = new Date(value);
      if (isNaN(d.getTime())) return String(value);
      return d
        .toISOString()
        .replace("T", " ")
        .replace(/\.\d{3}Z$/, "");
    },

    relativeTimeFromNow(value) {
      if (!value) return "-";
      const ts = new Date(value);
      if (isNaN(ts.getTime())) return "-";

      const diffSecs = Math.max(0, Math.floor((Date.now() - ts.getTime()) / 1000));
      if (diffSecs < 60) return `${diffSecs}s ago`;
      if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
      if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
      return `${Math.floor(diffSecs / 86400)}d ago`;
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

    errorMessage(err, fallback = "Request failed.") {
      if (!err) return fallback;
      const msg =
        err?.message ||
        err?.detail ||
        err?.response?.data?.detail ||
        err?.response?.data?.message;
      return String(msg || fallback);
    },

    clearModalError(modalName) {
      if (!modalName) return;
      this.modalErrors[modalName] = "";
    },

    setModalError(modalName, err, fallback = "Request failed.") {
      this.modalErrors[modalName] = this.errorMessage(err, fallback);
    },

    // ---------- Auth ----------
    stopAutoRefreshTimers() {
      if (typeof window !== "undefined" && window.__cpAutoRefreshTimers) {
        Object.values(window.__cpAutoRefreshTimers).forEach((timerId) => {
          clearInterval(timerId);
        });
        window.__cpAutoRefreshTimers = {};
      }
      if (this._autoTimer) {
        clearInterval(this._autoTimer);
        this._autoTimer = null;
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

    setManagedInterval(name, prop, callback, intervalMs) {
      if (this[prop]) {
        clearInterval(this[prop]);
        this[prop] = null;
      }
      if (typeof window !== "undefined") {
        window.__cpAutoRefreshTimers = window.__cpAutoRefreshTimers || {};
        const existing = window.__cpAutoRefreshTimers[name];
        if (existing) {
          clearInterval(existing);
        }
        const timerId = setInterval(callback, intervalMs);
        window.__cpAutoRefreshTimers[name] = timerId;
        this[prop] = timerId;
        return;
      }
      this[prop] = setInterval(callback, intervalMs);
    },

    setAuthRequired(loginPath, errorMessage = "Not authenticated.") {
      this.isAuthenticated = false;
      this.authClaims = null;
      this.authDisplayNameClaim = "preferred_username";
      this.authSessionCookieName = "cp_session";
      this.authError = String(errorMessage || "Not authenticated.");
      this.stopAutoRefreshTimers();
      if (loginPath) this.authLoginPath = loginPath;
    },

    syncAuthMeta() {
      const meta =
        this.authClaims &&
        typeof this.authClaims === "object" &&
        this.authClaims._cp &&
        typeof this.authClaims._cp === "object"
          ? this.authClaims._cp
          : null;

      if (
        meta &&
        typeof meta.display_name_claim === "string" &&
        meta.display_name_claim.trim()
      ) {
        this.authDisplayNameClaim = meta.display_name_claim.trim();
      } else {
        this.authDisplayNameClaim = "preferred_username";
      }

      if (
        meta &&
        typeof meta.session_cookie_name === "string" &&
        meta.session_cookie_name.trim()
      ) {
        this.authSessionCookieName = meta.session_cookie_name.trim();
      } else {
        this.authSessionCookieName = "cp_session";
      }
    },

    authClaimsWithoutCookies() {
      const claims =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : null;
      if (!claims) return {};
      return Object.fromEntries(
        Object.entries(claims).filter(
          ([key]) => key !== "cookies" && !String(key).startsWith("_"),
        ),
      );
    },

    authSessionCookieValue() {
      const claims =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : null;
      if (!claims || typeof claims.cookies !== "object" || !claims.cookies) {
        return "(No cookie data captured yet)";
      }

      const cookieName = String(this.authSessionCookieName || "").trim();
      if (!cookieName) return "(No cookie data captured yet)";

      const value = claims.cookies[cookieName];
      return value ? String(value) : "(No cookie data captured yet)";
    },

    authIsUnauthenticatedMode() {
      return Boolean(this.authClaims && this.authClaims.auth_disabled);
    },

    authGroupsClaimName() {
      const claims =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : null;
      const rawName = claims?._groups_claim_name;
      return typeof rawName === "string" && rawName.trim()
        ? rawName.trim()
        : "groups";
    },

    authGroups() {
      const claims =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : null;
      if (!claims) return [];
      return this.normalizeClaimValues(claims[this.authGroupsClaimName()]);
    },

    authRoleGroups() {
      const roleGroups =
        this.authClaims &&
        typeof this.authClaims === "object" &&
        this.authClaims._role_groups &&
        typeof this.authClaims._role_groups === "object"
          ? this.authClaims._role_groups
          : {};
      return roleGroups;
    },

    normalizeClaimValues(input) {
      if (Array.isArray(input)) {
        return input.map((value) => String(value).trim()).filter(Boolean);
      }
      if (typeof input === "string") {
        return input
          .split(",")
          .map((value) => String(value).trim())
          .filter(Boolean);
      }
      return [];
    },

    authRoles() {
      const values = [];
      const roleGroups = this.authRoleGroups();
      const userGroups = new Set(this.authGroups());

      Object.entries(roleGroups).forEach(([roleName, groups]) => {
        const normalizedGroups = this.normalizeClaimValues(groups);
        if (
          normalizedGroups.some((group) => userGroups.has(String(group).trim()))
        ) {
          values.push(roleName);
        }
      });

      return [
        ...new Set(values.map((value) => String(value).trim()).filter(Boolean)),
      ];
    },

    clusterOwnerGroups() {
      const userGroups = new Set(this.authGroups());
      const eligibleGroups = new Set();

      Object.values(this.authRoleGroups()).forEach((groups) => {
        this.normalizeClaimValues(groups).forEach((group) => {
          if (userGroups.has(group)) {
            eligibleGroups.add(group);
          }
        });
      });

      return [...eligibleGroups].sort((a, b) => a.localeCompare(b));
    },

    authRoleAnalysis() {
      const claimName = this.authGroupsClaimName();
      const claims =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : null;
      return {
        groups_claim_name: claimName,
        groups_claim_value: claims ? (claims[claimName] ?? null) : null,
        normalized_groups: this.authGroups(),
        role_groups: this.authRoleGroups(),
        cp_roles: this.authRoles(),
      };
    },

    logRoleCheck({
      checkType = "role-check",
      requiredRole = "",
      viewName = this.view,
      result = false,
      detail = "",
    } = {}) {
      console.info("[cp role check]", {
        checkType,
        viewName: String(viewName || "").trim() || this.view,
        requiredRole: String(requiredRole || "").trim(),
        result: Boolean(result),
        detail: detail ? String(detail) : "",
        ...this.authRoleAnalysis(),
      });
    },

    hasRole(role, { viewName = this.view, checkType = "hasRole" } = {}) {
      if (this.authIsUnauthenticatedMode()) return true;
      const roleName = String(role || "").trim();
      if (!roleName) return false;

      const userRoles = this.authRoles();
      if (userRoles.includes(roleName)) {
        this.logRoleCheck({
          checkType,
          requiredRole: roleName,
          viewName,
          result: true,
          detail: "Matched direct or inferred effective role.",
        });
        return true;
      }

      const userGroups = this.authGroups();
      const roleGroups = this.normalizeClaimValues(
        this.authRoleGroups()[roleName],
      );
      if (roleGroups.length === 0) {
        this.logRoleCheck({
          checkType,
          requiredRole: roleName,
          viewName,
          result: false,
          detail: "No role-to-group mapping found for required role.",
        });
        return false;
      }

      const result = roleGroups.some((group) => userGroups.includes(group));
      this.logRoleCheck({
        checkType,
        requiredRole: roleName,
        viewName,
        result,
        detail: result
          ? "Matched required role through group membership."
          : "No matching user group found for required role.",
      });
      return result;
    },

    canManageCompute() {
      return (
        this.authIsUnauthenticatedMode() ||
        this.hasRole("CP_USER", {
          viewName: this.view,
          checkType: "canManageCompute",
        }) ||
        this.hasRole("CP_ADMIN", {
          viewName: this.view,
          checkType: "canManageCompute",
        })
      );
    },

    canViewAdmin(viewName = this.view) {
      return (
        this.authIsUnauthenticatedMode() ||
        this.hasRole("CP_ADMIN", {
          viewName,
          checkType: "canViewAdmin",
        })
      );
    },

    isAdminSectionView(viewName = this.view) {
      return [
        "admin",
        "versions",
        "node_counts",
        "cpu_counts",
        "disk_sizes",
        "regions",
      ].includes(viewName);
    },

    authGroupsClaimName() {
      return String(
        this.authClaims?._groups_claim_name ||
          this.authClaims?._cp?.groups_claim_name ||
          "groups",
      );
    },

    currentUserGroups() {
      const claimName = this.authGroupsClaimName();
      const claimValue = this.authClaims?.[claimName];
      if (Array.isArray(claimValue)) return claimValue.filter(Boolean);
      if (typeof claimValue === "string" && claimValue.trim()) {
        return claimValue
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean);
      }
      return [];
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

    async ensureCurrentView() {
      if (this.view === "clusters") await this.ensureServersView();
      else if (this.view === "cluster") await this.ensureClusterDetailView();
      else if (this.view === "cluster_dashboard")
        await this.ensureClusterDashboardView();
      else if (this.view === "cluster_users")
        await this.ensureClusterUsersView();
      else if (this.view === "cluster_databases")
        await this.ensureClusterDatabasesView();
      else if (this.view === "cluster_backups")
        await this.ensureClusterBackupsView();
      else if (this.view === "cluster_artifacts")
        await this.ensureClusterArtifactsView();
      else if (this.view === "cluster_recovery")
        await this.ensureClusterRecoveryView();
      else if (this.view === "alerts") await this.ensureAlertsView();
      else if (this.view === "versions") await this.ensureVersionsView();
      else if (this.view === "node_counts") await this.ensureNodeCountsView();
      else if (this.view === "cpu_counts") await this.ensureCpuCountsView();
      else if (this.view === "disk_sizes") await this.ensureDiskSizesView();
      else if (this.view === "database_role_templates")
        await this.ensureDatabaseRoleTemplatesView();
      else if (this.view === "regions") await this.ensureRegionsView();
      else await this.ensureDashboardView();
    },

    isViewAccessible(viewName) {
      if (
        [
          "admin",
          "versions",
          "node_counts",
          "cpu_counts",
          "disk_sizes",
          "database_role_templates",
          "regions",
        ].includes(viewName)
      ) {
        const result = this.canViewAdmin(viewName);
        this.logRoleCheck({
          checkType: "isViewAccessible",
          requiredRole: "CP_ADMIN",
          viewName,
          result,
          detail: "Checking admin access for restricted view.",
        });
        return result;
      }
      this.logRoleCheck({
        checkType: "isViewAccessible",
        requiredRole: "",
        viewName,
        result: true,
        detail: "View does not require an admin role.",
      });
      return true;
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

    viewSubtitle() {
      const subtitles = {
        dashboard: "Infrastructure landing page and operational navigation",
        clusters: "Cluster inventory and status",
        cluster: "Cluster details, access points, and actions",
        cluster_dashboard: "Cluster dashboard and live time-series metrics",
        cluster_users: "Cluster database users and role management",
        cluster_backups: "Cluster backups and backup object details",
        cluster_artifacts: "Cluster artifacts and diagnostic downloads",
        cluster_recovery: "Restore a cluster from cataloged full backups",
        alerts: "Operational alerts and incident signals",
        admin: "Administrative landing page and tooling",
        versions: "List database versions",
        node_counts: "List available node counts",
        cpu_counts: "List available CPU-per-node options",
        disk_sizes: "List available disk size options",
        database_role_templates: "Preconfigured database role templates",
        regions: "List configured deployment regions",
      };
      return subtitles[this.view] || "Control plane workspace";
    },



    handleForbiddenView(viewName, { fallback = true } = {}) {
      this.setActionNotice(this.unauthorizedViewMessage(viewName));
      if (!fallback) return;

      this.clearClusterDatabaseObjectsState();
      this.clearClusterUsersState();
      this.view = "dashboard";
      localStorage.setItem("cp_view", this.view);
      this.syncHashFromState(true);
    },

    clearViewNotice() {
      this.viewNotice = "";
      this.viewNoticeJobId = "";
    },

    setActionNotice(message, jobId = "") {
      this.viewNotice = String(message || "");
      this.viewNoticeJobId = String(jobId || "").trim();
    },

    userDisplayName() {
      const c =
        this.authClaims && typeof this.authClaims === "object"
          ? this.authClaims
          : {};
      const claim = String(this.authDisplayNameClaim || "preferred_username");
      const val =
        c[claim] || c.preferred_username || c.name || c.email || c.sub || "";
      if (this.authIsUnauthenticatedMode()) return "Unauthenticated";
      return String(val || "Unknown user");
    },

    userIconTitle() {
      return this.authIsUnauthenticatedMode()
        ? "Running in unauthenticated mode"
        : "Authenticated user";
    },

    async refreshAuthMeSnapshot() {
      try {
        const res = await fetch("/api/auth/me", { method: "GET" });
        const ct = res.headers.get("content-type") || "";
        const isJson = ct.includes("application/json");
        const data = isJson
          ? await res.json().catch(() => null)
          : await res.text().catch(() => null);
        if (res.ok && data && typeof data === "object") {
          this.authClaims = data;

          this.syncAuthMeta();
        }
      } catch (_e) {
        // keep last known authClaims in the modal when refresh fails
      }
    },

    async openUserInfoModal() {
      await this.refreshAuthMeSnapshot();
      this.modal.userInfo.open = true;
    },

    closeUserInfoModal() {
      this.modal.userInfo.open = false;
    },

    async checkAuthSession() {
      let res = null;
      let data = null;
      try {
        res = await fetch("/api/auth/me", { method: "GET" });
      } catch (e) {
        this.authError = this.errorMessage(e, "Unable to verify session.");
        this.authChecked = true;
        return false;
      }

      const ct = res.headers.get("content-type") || "";
      const isJson = ct.includes("application/json");
      data = isJson
        ? await res.json().catch(() => null)
        : await res.text().catch(() => null);

      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          const loginPath =
            res.headers.get("x-auth-login-url") ||
            (data &&
              ((data.detail && data.detail.auth_login_url) ||
                data.auth_login_url)) ||
            "/api/auth/login";
          this.setAuthRequired(loginPath);
          this.authChecked = true;
          return false;
        }

        this.authError =
          (data && (data.detail || data.message)) ||
          (typeof data === "string" && data) ||
          `Auth check failed (${res.status})`;
        this.authChecked = true;
        return false;
      }

      this.isAuthenticated = true;
      this.authClaims = data && typeof data === "object" ? data : null;
      this.syncAuthMeta();
      this.authError = "";
      this.authChecked = true;
      this.clearViewNotice();
      return true;
    },

    loginWithSSO() {
      if (typeof window === "undefined") return;
      const loginPath = this.authLoginPath || "/api/auth/login";
      const next = encodeURIComponent(
        `${window.location.pathname}${window.location.search}${window.location.hash}`,
      );
      const sep = String(loginPath).includes("?") ? "&" : "?";
      window.location.assign(`${loginPath}${sep}next=${next}`);
    },

    // ---------- Init ----------


    setView(next) {
      if (next === this.view) return;
      if (!this.isViewAccessible(next)) {
        this.handleForbiddenView(next, { fallback: false });
        return;
      }

      this.clearViewNotice();
      if (next !== "cluster" && next !== "cluster_databases") {
        this.clearClusterDatabaseObjectsState();
      }
      if (next !== "cluster_users") {
        this.clearClusterUsersState();
      }
      this.view = next;
      localStorage.setItem("cp_view", this.view);
      this.syncHashFromState();
      this.ensureCurrentView();
    },




    async logout() {
      try {
        await fetch("/api/auth/logout", { method: "POST" });
      } catch (e) {
        console.error(e);
      } finally {
        this.setAuthRequired(this.authLoginPath, "");
        this.authChecked = true;
        if (typeof window !== "undefined") window.location.assign("/");
      }
    },

    // ---------- Shared API fetch (also feeds inspector on dashboard) ----------
    async apiFetch(path, { method = "GET", body = null } = {}) {
      const url = this.apiBase + path;
      const startedAtUtc = this.utcNowString();

      const opts = { method, headers: {} };
      if (body !== null && body !== undefined) {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(body);
      }

      const res = await fetch(url, opts);
      const ct = res.headers.get("content-type") || "";
      const isJson = ct.includes("application/json");
      const data = isJson
        ? await res.json().catch(() => null)
        : await res.text().catch(() => null);

      if (this.view === "dashboard") {
        this.inspector = {
          startedAtUtc,
          url,
          method,
          status: res.status,
          ok: res.ok,
          response: data,
        };
      }

      if (!res.ok) {
        if (res.status === 401 && typeof window !== "undefined") {
          const loginPath =
            res.headers.get("x-auth-login-url") ||
            (data &&
              ((data.detail && data.detail.auth_login_url) ||
                data.auth_login_url)) ||
            "/api/auth/login";
          this.setAuthRequired(loginPath);
          throw new Error("Not authenticated.");
        }

        const msg =
          (data && (data.detail || data.message)) ||
          (typeof data === "string" && data) ||
          `Request failed (${res.status})`;
        const error = new Error(msg);
        error.status = res.status;
        error.forbidden = res.status === 403;
        throw error;
      }

      return data;
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

      if (this.serversSortIndex !== null) {
        const type =
          this.serversSortTypeByIndex[this.serversSortIndex] || "string";
        const idx = this.serversSortIndex;
        const dir = this.serversSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.serversCellText(a, idx));
          const bv = this.parseValue(type, this.serversCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.serversVisibleRows = rows;
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
        this.setActionNotice(
          `Cluster '${name}' creation requested.`,
          result?.job_id,
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
      this.clearViewNotice();
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
        this.viewNotice = this.errorMessage(
          e,
          "Failed to load cluster details.",
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
        this.setActionNotice(
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
        this.setActionNotice(
          `IdP group mapping updated for database role '${roleName}'.`,
        );
      } catch (e) {
        console.error(e);
        this.setActionNotice(
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
        this.setActionNotice(
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
        this.setActionNotice(`Database object '${databaseName}' deleted.`);
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
      this.setActionNotice(
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
      this.clearViewNotice();
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
      this.clearViewNotice();
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
      this.clearViewNotice();
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
      this.clearViewNotice();
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
      this.clearViewNotice();
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
      this.clearViewNotice();
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
        this.setActionNotice(
          `Cluster '${clusterId}' delete requested.`,
          result?.job_id,
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
        this.setActionNotice(
          `Cluster '${clusterId}' healthcheck requested.`,
          result?.job_id,
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
      this.setActionNotice(
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
        height: 320,
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
        typeof window.uPlot !== "function" ||
        !this.clusterDashboardHasData()
      ) {
        this.destroyClusterDashboardCharts();
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
        this.setActionNotice(
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
        this.setActionNotice(
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
        this.setActionNotice(`Database user '${username}' created.`);
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
        this.setActionNotice(`Database user '${username}' deleted.`);
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
        this.setActionNotice(`Password updated for '${username}'.`);
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
        this.setActionNotice(
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
        this.setActionNotice(`Database roles granted to '${username}'.`);
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
        this.setActionNotice(
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
        this.setActionNotice(
          `Cluster recovery requested for '${targetClusterId}' from '${sourceClusterId}'.`,
          result?.job_id,
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
        this.setActionNotice(
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
        this.setActionNotice(
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
        this.setActionNotice(
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
        this.setActionNotice(
          `Download started for '${response?.artifact_name || row?.artifact_name || artifactId}'.`,
        );
      } catch (e) {
        console.error(e);
        this.setActionNotice(
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
        this.setActionNotice(
          `Restore requested for ${this.backupObjectTypeLabel(objectType).toLowerCase()} '${objectName}'.`,
          result?.job_id,
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
        this.setActionNotice(
          `Cluster '${clusterName}' upgrade requested to ${version}.`,
          result?.job_id,
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
        this.setActionNotice(
          `Cluster '${clusterName}' scale requested.`,
          result?.job_id,
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

























    openServerActionConfirm(server, action) {
      this.modal.serverActionConfirm.hostname = server?.hostname || "";
      this.modal.serverActionConfirm.action = action || "decommission";
      this.clearModalError("serverActionConfirm");
      this.modal.serverActionConfirm.open = true;
    },

    closeServerActionConfirm() {
      this.modal.serverActionConfirm.open = false;
      this.clearModalError("serverActionConfirm");
    },

    async confirmServerAction() {
      const hostname = (this.modal.serverActionConfirm.hostname || "").trim();
      const action = this.modal.serverActionConfirm.action;
      if (!hostname) return;

      this.serversLoading.action = true;
      try {
        if (action === "delete") {
          await this.apiFetch(
            `/admin/servers/${encodeURIComponent(hostname)}`,
            {
              method: "DELETE",
            },
          );
        } else {
          await this.apiFetch(
            `/admin/servers/${encodeURIComponent(hostname)}`,
            {
              method: "PUT",
            },
          );
        }
        this.closeServerActionConfirm();
        await this.refreshServers();
      } catch (e) {
        this.setModalError(
          "serverActionConfirm",
          e,
          "Failed to run server action.",
        );
      } finally {
        this.serversLoading.action = false;
      }
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
        this.setActionNotice(`Version '${version}' created.`);
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
        this.setActionNotice(`Version '${version}' deleted.`);
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
        this.setActionNotice(`${config.singularLabel} '${value}' created.`);
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
        this.setActionNotice(`${config.singularLabel} '${value}' deleted.`);
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
        this.setActionNotice(`Database role template '${databaseRoleTemplate}' created.`);
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
        this.setActionNotice(`Database role template '${databaseRoleTemplate}' deleted.`);
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
        this.setActionNotice(`Region '${cloud}/${region}/${zone}' created.`);
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
        this.setActionNotice(`Region '${cloud}/${region}/${zone}' deleted.`);
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

    // ---------- Dashboard lifecycle ----------
    persistFilter() {
      localStorage.setItem("cp_filter", this.filterQuery || "");
    },

    persistServersFilter() {
      localStorage.setItem("cp_servers_filter", this.serversFilterQuery || "");
    },

    persistAlertsFilter() {
      localStorage.setItem("cp_alerts_filter", this.alertsFilterQuery || "");
    },
    persistInspectorFormat() {
      localStorage.setItem("cp_inspector_format", this.inspectorFormat);
    },

    async refreshDashboard() {
      this.loading.list = true;
      try {
        const data = await this.apiFetch("/compute_units/");
        this.computeUnits = Array.isArray(data) ? data : [];
        this.computeUnits = this.computeUnits.map((row) => ({
          ...row,
          compute_id: `${row.hostname}_${row.cpu_range}`,
        }));
        this.lastUpdatedUtc = this.utcNowString();
        this.applyFilterSort();
      } catch (e) {
        console.error(e);
        this.lastUpdatedUtc = this.utcNowString();
      } finally {
        this.loading.list = false;
      }
    },

    // ---------- Dashboard sorting/filtering ----------
    rowText(row) {
      const parts = [
        row.compute_id,
        row.hostname,
        row.ip,
        row.region,
        row.zone,
        row.status,
        this.tagValue(row, "deployment_id"),
      ];
      const tags =
        row.tags && typeof row.tags === "object"
          ? Object.entries(row.tags).map(
              ([k, v]) => `${k}:${Array.isArray(v) ? v.join(",") : v}`,
            )
          : [];
      return parts.concat(tags).filter(Boolean).join(" ").toLowerCase();
    },

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

    cellText(row, colIndex) {
      switch (colIndex) {
        case 0:
          return this.tagValue(row, "deployment_id") || "";
        case 1:
          return row.compute_id;
        case 2:
          return `${row.region || "-"}-${row.zone || "-"}`;
        case 3:
          return row.hostname || "";
        case 4:
          return row.ip || "";
        case 5:
          return row.cpu_count;
        case 6:
          return row.cpu_range || "";
        case 7:
          return row.ports_range || "";
        case 8:
          return row.started_at || "";
        case 9:
          return row.status || "";
        default:
          return "";
      }
    },

    applyFilterSort() {
      const q = (this.filterQuery || "").toLowerCase().trim();
      let rows = this.computeUnits.slice();
      if (q) rows = rows.filter((r) => this.rowText(r).includes(q));

      if (this.sortIndex !== null) {
        const type = this.sortTypeByIndex[this.sortIndex] || "string";
        const idx = this.sortIndex;
        const dir = this.sortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.cellText(a, idx));
          const bv = this.parseValue(type, this.cellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.visibleRows = rows;
    },

    toggleSort(index) {
      if (this.sortIndex === index)
        this.sortDir = this.sortDir === "asc" ? "desc" : "asc";
      else {
        this.sortIndex = index;
        this.sortDir = "asc";
      }

      localStorage.setItem("cp_sort_index", String(this.sortIndex));
      localStorage.setItem("cp_sort_dir", this.sortDir);
      this.applyFilterSort();
    },

    sortClass(index) {
      if (this.sortIndex !== index) return "";
      return this.sortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    tagValue(row, key) {
      const t = row.tags;
      if (!t || typeof t !== "object") return null;
      const v = t[key];
      if (v === undefined || v === null) return null;
      return Array.isArray(v) ? v.join(",") : String(v);
    },

    extraTags(row) {
      const t = row.tags;
      if (!t || typeof t !== "object") return [];
      return Object.entries(t).filter(
        ([k, _]) => !["deployment_id", "owner"].includes(k),
      );
    },

    formatTag(k, v) {
      if (Array.isArray(v)) return `${k}:[${v.join(",")}]`;
      return `${k}:${v}`;
    },

    statusClass(status) {
      const s = String(status || "").toLowerCase();
      if (s.includes("free")) return "status-online";
      if (s.includes("allocated")) return "status-warning";
      if (s.includes("decommissioned")) return "status-muted";
      if (s.includes("ing")) return "status-pending status-pulse";
      if (!s || s === "unknown") return "status-muted";
      return "status-offline";
    },

    // ---------- Inspector JSON -> YAML ----------
    inspectorText() {
      if (!this.inspector) return "No requests yet.";
      if (this.inspectorFormat === "json")
        return JSON.stringify(this.inspector, null, 2);
      return this.toYaml(this.inspector);
    },

    toYaml(value) {
      const isObj = (v) => v && typeof v === "object" && !Array.isArray(v);
      const needsQuotes = (s) =>
        s === "" ||
        /[:\-\?\[\]\{\},#&\*!|>'"%@`]/.test(s) ||
        /^\s|\s$/.test(s) ||
        /^(true|false|null|~|-?\d+(\.\d+)?)$/i.test(s);

      const quote = (s) =>
        `"${String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;

      const scalar = (v) => {
        if (v === null) return "null";
        if (v === true) return "true";
        if (v === false) return "false";
        if (typeof v === "number")
          return Number.isFinite(v) ? String(v) : quote(String(v));
        if (typeof v === "string") return needsQuotes(v) ? quote(v) : v;
        return quote(String(v));
      };

      const indent = (n) => "  ".repeat(n);

      const render = (v, depth) => {
        if (Array.isArray(v)) {
          if (v.length === 0) return "[]";
          return v
            .map((item) => {
              if (isObj(item) || Array.isArray(item)) {
                return `${indent(depth)}- ${render(
                  item,
                  depth + 1,
                ).trimStart()}`;
              }
              return `${indent(depth)}- ${scalar(item)}`;
            })
            .join("\n");
        }

        if (isObj(v)) {
          const keys = Object.keys(v);
          if (keys.length === 0) return "{}";
          return keys
            .map((k) => {
              const val = v[k];
              const keyStr = needsQuotes(k) ? quote(k) : k;
              if (isObj(val) || Array.isArray(val)) {
                return `${indent(depth)}${keyStr}:\n${render(val, depth + 1)}`;
              }
              return `${indent(depth)}${keyStr}: ${scalar(val)}`;
            })
            .join("\n");
        }

        return scalar(v);
      };

      return render(value, 0);
    },

    // ---------- Dashboard actions ----------
    openAllocateModal(computeId = "") {
      this.modal.allocate.compute_id = computeId ? String(computeId) : "";
      this.clearModalError("allocate");
      this.modal.allocate.open = true;
    },
    closeAllocateModal() {
      this.modal.allocate.open = false;
      this.clearModalError("allocate");
    },

    async allocate() {
      this.loading.allocate = true;
      this.clearModalError("allocate");
      try {
        const tags = JSON.parse(
          (this.modal.allocate.tagsText || "{}").trim() || "{}",
        );

        const payload = {
          cpu_count: this.modal.allocate.cpu_count ?? null,
          region: this.modal.allocate.region || null,
          zone: this.modal.allocate.zone || null,
          compute_id: (this.modal.allocate.compute_id || "").trim() || null,
          tags,
          ssh_public_key: (this.modal.allocate.ssh_public_key || "").trim(),
        };

        const deployment_id = (this.modal.allocate.deployment_id || "").trim();
        if (deployment_id)
          payload.tags = { ...(payload.tags || {}), deployment_id };

        if (!payload.ssh_public_key)
          throw new Error("ssh_public_key is required.");
        if (tags === null || typeof tags !== "object" || Array.isArray(tags))
          throw new Error("tags must be a JSON object.");
        await this.apiFetch("/compute_units/allocate", {
          method: "POST",
          body: payload,
        });
        this.closeAllocateModal();
        await this.refreshDashboard();
        if (typeof this.refreshServers === "function")
          await this.refreshServers();
      } catch (err) {
        this.setModalError("allocate", err, "Allocation failed.");
      } finally {
        this.loading.allocate = false;
      }
    },

    openInitModal() {
      // Keep any existing values, but ensure step has a sane default.
      if (this.modal.init.cpuStep == null || this.modal.init.cpuStep <= 0)
        this.modal.init.cpuStep = null;

      this.clearModalError("init");
      this.modal.init.open = true;
      this.recomputeInitCpuRanges();
    },
    closeInitModal() {
      this.modal.init.open = false;
      this.clearModalError("init");
      this.modal.init.ip = "";
      this.modal.init.hostname = "";
      this.modal.init.user_id = "ubuntu";
      this.modal.init.region = "";
      this.modal.init.zone = "";
      this.modal.init.deployment_id = "";
      this.modal.init.cpuStart = 0;
      this.modal.init.cpuEnd = 0;
      this.modal.init.cpuStep = 0;
      this.modal.init.cpuRangesText = "";
      this.modal.init.cpuRangesPreview = "";
      this.modal.init.cpuSetPreview = "";
      this.modal.init.cpuRangesError = "";
    },

    recomputeInitCpuRanges(fromTextarea = false) {
      // If fromTextarea=true, parse cpuRangesText and just update previews.
      // Otherwise compute ranges from start/end/step and update cpuRangesText + previews.
      try {
        this.modal.init.cpuRangesError = "";

        let cpu_ranges = [];
        let cpu_set = [];

        if (fromTextarea) {
          const parsed = JSON.parse(
            (this.modal.init.cpuRangesText || "[]").trim() || "[]",
          );
          if (
            !Array.isArray(parsed) ||
            parsed.some((x) => typeof x !== "string")
          )
            throw new Error("cpu_ranges must be a JSON array of strings.");
          cpu_ranges = parsed;
        } else {
          const start = 0;
          const end = Number(this.modal.init.cpuEnd) - 1;
          const step = Number(this.modal.init.cpuStep);

          if (!Number.isInteger(end) || end < 0)
            throw new Error("end must be a non-negative integer.");
          if (!Number.isInteger(step) || step <= 0)
            throw new Error("step must be a positive integer.");
          if (end < start) throw new Error("end must be >= start.");

          // Build chunks: [start..min(start+step-1,end)], then advance by step.
          for (let cur = start; cur <= end; cur += step) {
            const chunkEnd = Math.min(cur + step - 1, end);
            cpu_ranges.push(`${cur}-${chunkEnd}`);
          }

          // Keep JSON textarea in sync for transparency / copy-paste.
          this.modal.init.cpuRangesText = JSON.stringify(cpu_ranges);
        }

        // Expand to a CPU set preview (best-effort)
        for (const r of cpu_ranges) {
          const m = String(r).match(/^\s*(\d+)\s*-\s*(\d+)\s*$/);
          if (!m) continue;
          const a = Number(m[1]);
          const b = Number(m[2]);
          if (!Number.isInteger(a) || !Number.isInteger(b) || b < a) continue;
          for (let i = a; i <= b; i++) cpu_set.push(i);
        }

        // De-dup + sort
        cpu_set = Array.from(new Set(cpu_set)).sort((a, b) => a - b);

        this.modal.init.cpuRangesPreview = JSON.stringify(cpu_ranges, null, 2);
        this.modal.init.cpuSetPreview = cpu_set.length
          ? `${cpu_set.join(", ")}\n(count: ${cpu_set.length})`
          : "-";
      } catch (e) {
        this.modal.init.cpuRangesPreview = "";
        this.modal.init.cpuSetPreview = "";
        this.modal.init.cpuRangesError = e.message || String(e);
      }
    },

    async initServer() {
      this.loading.init = true;
      this.clearModalError("init");
      try {
        const cpu_ranges = JSON.parse(
          (this.modal.init.cpuRangesText || "[]").trim() || "[]",
        );
        if (
          !Array.isArray(cpu_ranges) ||
          cpu_ranges.some((x) => typeof x !== "string")
        )
          throw new Error("cpu_ranges must be a JSON array of strings.");

        const payload = {
          ip: (this.modal.init.ip || "").trim(),
          region: (this.modal.init.region || "").trim(),
          zone: (this.modal.init.zone || "").trim(),
          hostname: (this.modal.init.hostname || "").trim(),
          user_id: (this.modal.init.user_id || "ubuntu").trim(),
          cpu_ranges,
        };
        for (const [k, v] of Object.entries(payload)) {
          if ((typeof v === "string" && !v) || v == null)
            throw new Error(`${k} is required.`);
        }

        await this.apiFetch("/admin/servers/", {
          method: "POST",
          body: payload,
        });
        this.closeInitModal();
        await this.refreshDashboard();
        if (typeof this.refreshServers === "function")
          await this.refreshServers();
      } catch (e) {
        this.setModalError("init", e, "Server init failed.");
      } finally {
        this.loading.init = false;
      }
    },

    openDecommissionModal() {
      this.clearModalError("decommission");
      this.modal.decommission.open = true;
    },
    closeDecommissionModal() {
      this.modal.decommission.open = false;
      this.clearModalError("decommission");
    },

    async decommissionByHostname() {
      this.loading.decommission = true;
      this.clearModalError("decommission");
      try {
        const payload = {
          hostname: (this.modal.decommission.hostname || "").trim(),
        };

        await this.apiFetch("/admin/servers/", {
          method: "PUT",
          body: payload,
        });

        this.closeDecommissionModal();
        await this.refreshDashboard();
        if (typeof this.refreshServers === "function")
          await this.refreshServers();
      } catch (e) {
        this.setModalError("decommission", e, "Server decommission failed.");
      } finally {
        this.loading.decommission = false;
      }
    },

    openDeallocateConfirm(row) {
      this.modal.deallocateConfirm.compute_id = row.compute_id;
      this.modal.deallocateConfirm.hostname = row.hostname || "";
      this.clearModalError("deallocateConfirm");
      this.modal.deallocateConfirm.open = true;
    },
    closeDeallocateConfirm() {
      this.modal.deallocateConfirm.open = false;
      this.clearModalError("deallocateConfirm");
    },

    openComputeDetails(row) {
      this.modal.computeDetails.row = row || null;
      this.modal.computeDetails.open = true;
    },
    closeComputeDetails() {
      this.modal.computeDetails.open = false;
      this.modal.computeDetails.row = null;
    },

    openServerDetails(row) {
      this.modal.serverDetails.row = row || null;
      this.modal.serverDetails.open = true;
    },

    closeServerDetails() {
      this.modal.serverDetails.open = false;
      this.modal.serverDetails.row = null;
    },

    async confirmDeallocate() {
      const computeId = this.modal.deallocateConfirm.compute_id;
      this.loading.deallocateConfirm = true;
      this.busyKey = computeId;
      this.clearModalError("deallocateConfirm");
      try {
        await this.apiFetch(
          `/compute_units/deallocate/${encodeURIComponent(computeId)}`,
          { method: "DELETE" },
        );
        this.closeDeallocateConfirm();
        await this.refreshDashboard();
        if (typeof this.refreshServers === "function")
          await this.refreshServers();
      } catch (e) {
        this.setModalError("deallocateConfirm", e, "Deallocate failed.");
      } finally {
        this.loading.deallocateConfirm = false;
        this.busyKey = null;
      }
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
};

const CP_LEGACY_APP_FACTORY = window.app;

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
    "safeJson",
    "formatJson",
    "rolesText",
    "openUserInfoModal",
    "closeUserInfoModal",
  ]);
  const CPKIT_MODAL_KEYS = new Set([
    "userInfo",
  ]);

  function loadLegacyApp() {
    if (typeof CP_LEGACY_APP_FACTORY !== "function") return {};
    return CP_LEGACY_APP_FACTORY();
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

  function preloadAppStaticAssets(assetPaths = []) {
    assetPaths.forEach((assetPath) => {
      const normalized = String(assetPath || "").trim().replace(/^\/+/, "");
      if (!normalized) return;
      const image = new Image();
      image.src = `/app/static/${normalized}`;
    });
  }

  const legacy = splitLegacyApp(loadLegacyApp());

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
        return CP_ADMIN_VIEWS.has(viewName) || viewName === "admin";
      },
    },
    async init() {
      ensureScript("https://cdn.jsdelivr.net/npm/uplot@1.6.32/dist/uPlot.iife.min.js");
      preloadAppStaticAssets([
        ...((this.cloudLogoKeys || []).map((key) => `${key}.png`)),
        "favicon.png",
        "logo.png",
      ]);
    },
  };
})();
