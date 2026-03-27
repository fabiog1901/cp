// cp SPA (tabs, no routing) using Alpine + Fetch + Ace for Playbooks editor (no YAML linter yet).

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

    // Shared UTC timestamps

    // ---------- Servers state ----------
    servers: [],
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
      create: false,
      upgrade: false,
      scale: false,
    },
    clusterUsers: [],
    clusterUsersVisibleRows: [],
    clusterUsersFilterQuery: "",
    clusterUsersLastUpdatedUtc: null,
    clusterUsersAutoRefreshEnabled: true,
    _clusterUsersAutoTimer: null,
    clusterUsersLoading: {
      snapshot: false,
      create: false,
      delete: false,
      password: false,
      revokeRole: false,
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
    },
    clusterConnectCopiedFor: "",
    clusterCreateOptions: {
      versions: [],
      node_counts: [],
      cpus_per_node: [],
      disk_sizes: [],
      regions: [],
    },

    // ---------- Jobs state ----------
    jobs: [],
    jobsVisibleRows: [],
    jobsFilterQuery: "",
    jobsLastUpdatedUtc: null,
    jobsSortIndex: 0,
    jobsSortDir: "desc",
    jobsSortTypeByIndex: {
      0: "number", // job_id
      1: "string", // job_type
      2: "string", // status
      3: "string", // created_by
      4: "date", // created_at
      5: "date", // updated_at
    },
    jobsLoading: { list: false },
    jobsAutoRefreshEnabled: true,
    _jobsAutoTimer: null,
    jobDetailsAutoRefreshEnabled: true,
    _jobDetailsAutoTimer: null,
    jobsContextClusterId: "",
    selectedJobId: "",
    selectedJobDetails: null,
    jobLoading: { details: false, reschedule: false },

    // ---------- Events state ----------
    events: [],
    eventsVisibleRows: [],
    eventsFilterQuery: "",
    eventsLastUpdatedUtc: null,
    eventsSortIndex: 0,
    eventsSortDir: "desc",
    eventsSortTypeByIndex: {
      0: "date", // ts
      1: "string", // user_id
      2: "string", // action
      3: "string", // details
      4: "string", // request_id
    },
    eventsLoading: { list: false },
    eventsAutoRefreshEnabled: true,
    _eventsAutoTimer: null,

    // ---------- API keys state ----------
    apiKeys: [],
    apiKeysVisibleRows: [],
    apiKeysFilterQuery: "",
    apiKeysLastUpdatedUtc: null,
    apiKeysSortIndex: 2,
    apiKeysSortDir: "desc",
    apiKeysSortTypeByIndex: {
      0: "string", // access_key
      1: "string", // owner
      2: "date", // valid_until
      3: "string", // roles
    },
    apiKeysLoading: { list: false, create: false, delete: false },
    apiKeysAutoRefreshEnabled: true,
    _apiKeysAutoTimer: null,
    availableCPRoles: ["CP_READONLY", "CP_USER", "CP_ADMIN"],

    // ---------- Settings state ----------
    settings: [],
    settingsVisibleRows: [],
    settingsFilterQuery: "",
    settingsLastUpdatedUtc: null,
    settingsSortIndex: 1,
    settingsSortDir: "asc",
    settingsSortTypeByIndex: {
      0: "string", // key
      1: "string", // category
      2: "string", // value_type
      3: "string", // effective_value
      4: "string", // default_value
      5: "date", // updated_at
    },
    settingsLoading: { list: false, update: false, reset: false },
    settingsAutoRefreshEnabled: true,
    _settingsAutoTimer: null,
    settingsDrafts: {},
    settingsError: "",

    // ---------- Versions state ----------
    versions: [],
    versionsVisibleRows: [],
    versionsFilterQuery: "",
    versionsLastUpdatedUtc: null,
    versionsLoading: { list: false, create: false, delete: false },
    versionsAutoRefreshEnabled: true,
    _versionsAutoTimer: null,

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
      apiKeyCreate: {
        open: false,
        valid_until: "",
        roles: ["CP_ADMIN"],
      },
      apiKeyDeleteConfirm: {
        open: false,
        access_key: "",
        owner: "",
      },
      versionCreate: {
        open: false,
        version: "",
      },
      versionDeleteConfirm: {
        open: false,
        version: "",
      },
      playbookVersionDeleteConfirm: {
        open: false,
        version: "",
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
      clusterUserCreate: {
        open: false,
        username: "",
        password: "",
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
        roles: [],
        grantRole: "",
      },
      apiKeySecret: {
        open: false,
        access_key: "",
        owner: "",
        valid_until: "",
        roles: [],
        secret_access_key: "",
        reveal: false,
        copied: false,
      },
      settingResetConfirm: {
        open: false,
        key: "",
        category: "",
        value_type: "",
        default_value: "",
        is_secret: false,
      },
    },
    modalErrors: {
      allocate: "",
      init: "",
      decommission: "",
      deallocateConfirm: "",
      serverActionConfirm: "",
      apiKeyCreate: "",
      apiKeyDeleteConfirm: "",
      versionCreate: "",
      versionDeleteConfirm: "",
      playbookVersionDeleteConfirm: "",
      regionCreate: "",
      regionDeleteConfirm: "",
      clusterDeleteConfirm: "",
      clusterCreate: "",
      clusterUpgrade: "",
      clusterScale: "",
      clusterUserCreate: "",
      clusterUserDeleteConfirm: "",
      clusterUserPassword: "",
      clusterUserRoles: "",
      settingResetConfirm: "",
    },

    // ---------- Playbooks state ----------
    playbooks: [
      "CREATE_CLUSTER",
      "DELETE_CLUSTER",
      "SCALE_CLUSTER_IN",
      "SCALE_CLUSTER_OUT",
      "SCALE_DISK_SIZE",
      "SCALE_NODE_CPUS",
      "UPGRADE_CLUSTER",
      "HEALTHCHECK_CLUSTER",
      "RESTORE_CLUSTER",
    ],
    selectedPlaybook: "",
    pbEditorReady: false,
    pbLoading: {
      list: false,
      save: false,
      load: false,
      setDefault: false,
      delete: false,
    },
    pbToast: { message: "", ok: true },
    pbLastUpdatedUtc: null,
    pbDefaultVersion: "",
    pbSelectedVersion: "",
    pbVersions: [],

    // Ace
    _ace: null,
    _aceReady: false,

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
      const normalized = String(value || "")
        .trim()
        .toLowerCase();
      if (normalized === "azure") return "azr";
      if (normalized.startsWith("aws")) return "aws";
      if (normalized.startsWith("azr")) return "azr";
      if (normalized.startsWith("gcp")) return "gcp";
      return normalized.slice(0, 3);
    },

    cloudLogoForCloud(cloud) {
      const cloudKey = this.cloudKey(cloud);
      if (["aws", "azr", "gcp"].includes(cloudKey)) {
        return `/static/${cloudKey}.png`;
      }
      return "";
    },

    cloudLogoForRegion(regionId) {
      return this.cloudLogoForCloud(this.cloudKeyFromRegion(regionId));
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
      if (this._clusterBackupsAutoTimer) {
        clearInterval(this._clusterBackupsAutoTimer);
        this._clusterBackupsAutoTimer = null;
      }
      if (this._eventsAutoTimer) {
        clearInterval(this._eventsAutoTimer);
        this._eventsAutoTimer = null;
      }
      if (this._jobsAutoTimer) {
        clearInterval(this._jobsAutoTimer);
        this._jobsAutoTimer = null;
      }
      if (this._jobDetailsAutoTimer) {
        clearInterval(this._jobDetailsAutoTimer);
        this._jobDetailsAutoTimer = null;
      }
      if (this._versionsAutoTimer) {
        clearInterval(this._versionsAutoTimer);
        this._versionsAutoTimer = null;
      }
      if (this._regionsAutoTimer) {
        clearInterval(this._regionsAutoTimer);
        this._regionsAutoTimer = null;
      }
      if (this._apiKeysAutoTimer) {
        clearInterval(this._apiKeysAutoTimer);
        this._apiKeysAutoTimer = null;
      }
      if (this._settingsAutoTimer) {
        clearInterval(this._settingsAutoTimer);
        this._settingsAutoTimer = null;
      }
      this.destroyClusterDashboardCharts();
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
        "settings",
        "api_keys",
        "versions",
        "regions",
        "playbooks",
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
      return this.buildPath(path, {
        groups: this.currentUserGroups(),
        is_admin: this.canViewAdmin(),
        ...extra,
      });
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
        case "cluster_backups":
          return this.selectedClusterId
            ? this.routeHash(
                `/clusters/${encodeURIComponent(this.selectedClusterId)}/backups`,
                { path: this.selectedClusterBackupPath },
              )
            : this.routeHash("/clusters");
        case "jobs":
          return this.routeHash("/jobs", {
            cluster: this.jobsContextClusterId,
          });
        case "job":
          return this.selectedJobId
            ? this.routeHash(`/jobs/${encodeURIComponent(this.selectedJobId)}`)
            : this.routeHash("/jobs");
        case "events":
          return this.routeHash("/events");
        case "admin":
          return this.routeHash("/admin");
        case "api_keys":
          return this.routeHash("/admin/api-keys");
        case "settings":
          return this.routeHash("/admin/settings");
        case "versions":
          return this.routeHash("/admin/versions");
        case "regions":
          return this.routeHash("/admin/regions");
        case "playbooks":
          return this.routeHash("/admin/playbooks");
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
      if (this.view === "playbooks") await this.ensurePlaybooksView();
      else if (this.view === "clusters") await this.ensureServersView();
      else if (this.view === "cluster") await this.ensureClusterDetailView();
      else if (this.view === "cluster_dashboard")
        await this.ensureClusterDashboardView();
      else if (this.view === "cluster_users") await this.ensureClusterUsersView();
      else if (this.view === "cluster_backups")
        await this.ensureClusterBackupsView();
      else if (this.view === "jobs") await this.ensureJobsView();
      else if (this.view === "job") await this.ensureJobDetailView();
      else if (this.view === "events") await this.ensureEventsView();
      else if (this.view === "api_keys") await this.ensureApiKeysView();
      else if (this.view === "settings") await this.ensureSettingsView();
      else if (this.view === "versions") await this.ensureVersionsView();
      else if (this.view === "regions") await this.ensureRegionsView();
      else if (this.view === "admin") await this.ensureAdminView();
      else await this.ensureDashboardView();
    },

    async applyHashRoute() {
      const route = this.parseCurrentHashRoute();
      if (!route.hasHash) return false;

      const parts = route.parts;
      const query = route.query || {};
      const previousJobsContext = String(this.jobsContextClusterId || "").trim();

      let nextView = "dashboard";
      let nextClusterId = "";
      let nextJobId = "";

      if (parts.length === 0 || parts[0] === "dashboard") {
        nextView = "dashboard";
      } else if (parts[0] === "clusters") {
        if (parts.length === 1) {
          nextView = "clusters";
        } else if (parts.length >= 2) {
          nextClusterId = String(parts[1] || "").trim();
          if (parts[2] === "dashboard") nextView = "cluster_dashboard";
          else if (parts[2] === "users") nextView = "cluster_users";
          else if (parts[2] === "backups") nextView = "cluster_backups";
          else nextView = "cluster";
        }
      } else if (parts[0] === "jobs") {
        if (parts.length >= 2) {
          nextView = "job";
          nextJobId = String(parts[1] || "").trim();
        } else {
          nextView = "jobs";
          this.jobsContextClusterId = String(query.cluster || "").trim();
          localStorage.setItem(
            "cp_jobs_context_cluster_id",
            this.jobsContextClusterId,
          );
          if (this.jobsContextClusterId) {
            this.jobsFilterQuery = this.jobsContextClusterId;
            this.persistJobsFilter();
          } else if (
            previousJobsContext &&
            String(this.jobsFilterQuery || "").trim() === previousJobsContext
          ) {
            this.jobsFilterQuery = "";
            this.persistJobsFilter();
          }
        }
      } else if (parts[0] === "events") {
        nextView = "events";
      } else if (parts[0] === "admin") {
        if (parts[1] === "api-keys") nextView = "api_keys";
        else if (parts[1] === "settings") nextView = "settings";
        else if (parts[1] === "versions") nextView = "versions";
        else if (parts[1] === "regions") nextView = "regions";
        else if (parts[1] === "playbooks") nextView = "playbooks";
        else nextView = "admin";
      } else {
        nextView = "dashboard";
      }

      if (nextClusterId) {
        const clusterChanged =
          String(this.selectedClusterId || "").trim() !== nextClusterId;
        this.selectedClusterId = nextClusterId;
        localStorage.setItem("cp_selected_cluster_id", nextClusterId);
        this.clusterConnectCopiedFor = "";
        if (clusterChanged) {
          this.selectedCluster = null;
          this.clusterUsers = [];
          this.clusterUsersVisibleRows = [];
          this.clusterBackups = [];
          this.clusterBackupDetails = [];
          this.clusterDashboardSnapshot = null;
          this.clusterDashboardChartData = [];
          this.clusterDashboardCurrentNodes = [];
        }
      }

      if (nextJobId) {
        const changedJob = String(this.selectedJobId || "").trim() !== nextJobId;
        this.selectedJobId = nextJobId;
        localStorage.setItem("cp_selected_job_id", nextJobId);
        if (changedJob) this.selectedJobDetails = null;
      }

      if (nextView === "cluster_backups") {
        this.selectedClusterBackupPath = String(query.path || "").trim();
      } else {
        this.selectedClusterBackupPath = "";
      }

      if (nextView === "cluster_dashboard") {
        const period = Number.parseInt(query.period, 10);
        const step = Number.parseInt(query.step, 10);
        if (Number.isFinite(period) && period > 0) {
          this.clusterDashboardPeriodMins = period;
        }
        if (Number.isFinite(step) && step > 0) {
          this.clusterDashboardIntervalSecs = step;
        }
      }

      this.view = nextView;
      localStorage.setItem("cp_view", this.view);

      if (!this.isViewAccessible(this.view)) {
        this.handleForbiddenView(this.view);
        this.syncHashFromState(true);
        return true;
      }

      this.clearViewNotice();
      await this.ensureCurrentView();
      return true;
    },

    async handleHashChange() {
      if (this._suppressNextHashChange) {
        this._suppressNextHashChange = false;
        return;
      }
      await this.applyHashRoute();
    },

    isViewAccessible(viewName) {
      if (
        [
          "admin",
          "playbooks",
          "api_keys",
          "settings",
          "versions",
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
        jobs: "Jobs",
        events: "Events",
        admin: "Admin",
        playbooks: "Playbooks",
        api_keys: "API Keys",
        settings: "Settings",
        versions: "Versions",
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
        jobs: "Queued and completed orchestration work",
        job: "Job details and task execution history",
        events: "Cluster and platform activity stream",
        admin: "Administrative landing page and tooling",
        api_keys: "Manage API keys and one-time secret issuance",
        settings: "Manage dynamic configuration settings",
        versions: "List database versions",
        regions: "List configured deployment regions",
        playbooks: "Playbooks editor",
      };
      return subtitles[this.view] || "Control plane workspace";
    },

    jobsTitle() {
      return this.jobsContextClusterId
        ? `Jobs for ${this.jobsContextClusterId}`
        : "Jobs";
    },

    jobsSubtitle() {
      return this.jobsContextClusterId
        ? "Cluster-scoped jobs loaded from the cluster jobs endpoint."
        : "List of visible jobs from the jobs API.";
    },

    handleForbiddenView(viewName, { fallback = true } = {}) {
      this.setActionNotice(this.unauthorizedViewMessage(viewName));
      if (!fallback) return;

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
    async init() {
      const sIdx = localStorage.getItem("cp_sort_index");
      const sDir = localStorage.getItem("cp_sort_dir");
      const sFilter = localStorage.getItem("cp_filter");
      const sFmt = localStorage.getItem("cp_inspector_format");
      const sViewRaw = localStorage.getItem("cp_view");
      const sView = sViewRaw === "servers" ? "clusters" : sViewRaw;
      const selectedClusterId = localStorage.getItem("cp_selected_cluster_id");
      const ssIdx = localStorage.getItem("cp_servers_sort_index");
      const ssDir = localStorage.getItem("cp_servers_sort_dir");
      const ssFilter = localStorage.getItem("cp_servers_filter");
      const seIdx = localStorage.getItem("cp_events_sort_index");
      const seDir = localStorage.getItem("cp_events_sort_dir");
      const seFilter = localStorage.getItem("cp_events_filter");
      const sakIdx = localStorage.getItem("cp_api_keys_sort_index");
      const sakDir = localStorage.getItem("cp_api_keys_sort_dir");
      const sakFilter = localStorage.getItem("cp_api_keys_filter");
      const setIdx = localStorage.getItem("cp_settings_sort_index");
      const setDir = localStorage.getItem("cp_settings_sort_dir");
      const setFilter = localStorage.getItem("cp_settings_filter");
      const jobsFilter = localStorage.getItem("cp_jobs_filter");
      const jobsIdx = localStorage.getItem("cp_jobs_sort_index");
      const jobsDir = localStorage.getItem("cp_jobs_sort_dir");
      const jobsContextClusterId = localStorage.getItem(
        "cp_jobs_context_cluster_id",
      );
      const selectedJobId = localStorage.getItem("cp_selected_job_id");
      const versionsFilter = localStorage.getItem("cp_versions_filter");
      const regionsFilter = localStorage.getItem("cp_regions_filter");
      const clusterUsersFilter = localStorage.getItem("cp_cluster_users_filter");

      if (sIdx !== null && !Number.isNaN(+sIdx)) this.sortIndex = +sIdx;
      if (sDir === "desc") this.sortDir = "desc";
      if (sFilter !== null) this.filterQuery = sFilter;
      if (ssFilter !== null) this.serversFilterQuery = ssFilter;
      if (jobsFilter !== null) this.jobsFilterQuery = jobsFilter;
      if (jobsContextClusterId !== null)
        this.jobsContextClusterId = jobsContextClusterId;
      if (selectedJobId !== null) this.selectedJobId = selectedJobId;
      if (seFilter !== null) this.eventsFilterQuery = seFilter;
      if (sakFilter !== null) this.apiKeysFilterQuery = sakFilter;
      if (setFilter !== null) this.settingsFilterQuery = setFilter;
      if (versionsFilter !== null) this.versionsFilterQuery = versionsFilter;
      if (regionsFilter !== null) this.regionsFilterQuery = regionsFilter;
      if (clusterUsersFilter !== null)
        this.clusterUsersFilterQuery = clusterUsersFilter;
      if (selectedClusterId !== null)
        this.selectedClusterId = selectedClusterId;
      if (ssIdx !== null && !Number.isNaN(+ssIdx))
        this.serversSortIndex = +ssIdx;
      if (jobsIdx !== null && !Number.isNaN(+jobsIdx))
        this.jobsSortIndex = +jobsIdx;
      if (seIdx !== null && !Number.isNaN(+seIdx))
        this.eventsSortIndex = +seIdx;
      if (sakIdx !== null && !Number.isNaN(+sakIdx))
        this.apiKeysSortIndex = +sakIdx;
      if (setIdx !== null && !Number.isNaN(+setIdx))
        this.settingsSortIndex = +setIdx;
      if (ssDir === "desc") this.serversSortDir = "desc";
      if (jobsDir === "asc" || jobsDir === "desc") this.jobsSortDir = jobsDir;
      if (seDir === "asc" || seDir === "desc") this.eventsSortDir = seDir;
      if (sakDir === "asc" || sakDir === "desc") this.apiKeysSortDir = sakDir;
      if (setDir === "asc" || setDir === "desc") this.settingsSortDir = setDir;
      if (sFmt === "json" || sFmt === "yaml") this.inspectorFormat = sFmt;
      if (
        sView === "dashboard" ||
        sView === "clusters" ||
        sView === "cluster" ||
        sView === "cluster_dashboard" ||
        sView === "cluster_users" ||
        sView === "cluster_backups" ||
        sView === "jobs" ||
        sView === "job" ||
        sView === "admin" ||
        sView === "playbooks" ||
        sView === "events" ||
        sView === "api_keys" ||
        sView === "settings" ||
        sView === "versions" ||
        sView === "regions"
      )
        this.view = sView;

      this.renderedAtUtc = this.utcNowString();

      const hasSession = await this.checkAuthSession();
      if (!hasSession) return;

      if (typeof window !== "undefined" && !this._hashChangeHandlerRegistered) {
        window.addEventListener("hashchange", () => {
          this.handleHashChange();
        });
        this._hashChangeHandlerRegistered = true;
      }

      const hasHashRoute = this.parseCurrentHashRoute().hasHash;
      let routeHandled = false;
      if (hasHashRoute) {
        routeHandled = await this.applyHashRoute();
      } else if (!this.isViewAccessible(this.view)) {
        this.handleForbiddenView(this.view);
      } else {
        this.syncHashFromState(true);
      }

      if (!this.isViewAccessible(this.view)) {
        this.handleForbiddenView(this.view);
      }

      // Start dashboard timer (only refresh if dashboard tab is active)
      this._autoTimer = setInterval(() => {
        if (
          this.autoRefreshEnabled &&
          this.view === "dashboard" &&
          this.computeUnits.length > 0
        )
          this.refreshDashboard();
      }, 10_000);

      // Start clusters timer (legacy internal state name is servers)
      this._serversAutoTimer = setInterval(() => {
        if (this.serversAutoRefreshEnabled && this.view === "clusters")
          this.refreshServers();
      }, 15_000);

      this._clusterDetailsAutoTimer = setInterval(() => {
        if (
          this.clusterDetailsAutoRefreshEnabled &&
          this.view === "cluster" &&
          this.selectedClusterId
        )
          this.refreshSelectedCluster();
      }, 5_000);

      this._clusterDashboardAutoTimer = setInterval(() => {
        if (
          this.clusterDashboardAutoRefreshEnabled &&
          this.view === "cluster_dashboard" &&
          this.selectedClusterId
        )
          this.refreshClusterDashboard();
      }, 10_000);

      this._clusterUsersAutoTimer = setInterval(() => {
        if (
          this.clusterUsersAutoRefreshEnabled &&
          this.view === "cluster_users" &&
          this.selectedClusterId
        )
          this.refreshClusterUsers();
      }, 10_000);

      this._clusterBackupsAutoTimer = setInterval(() => {
        if (
          this.clusterBackupsAutoRefreshEnabled &&
          this.view === "cluster_backups" &&
          this.selectedClusterId
        )
          this.refreshClusterBackups();
      }, 20_000);

      this._jobsAutoTimer = setInterval(() => {
        if (this.jobsAutoRefreshEnabled && this.view === "jobs")
          this.refreshJobs();
      }, 15_000);

      this._jobDetailsAutoTimer = setInterval(() => {
        if (
          this.jobDetailsAutoRefreshEnabled &&
          this.view === "job" &&
          this.selectedJobId
        )
          this.refreshSelectedJobDetails();
      }, 15_000);

      this._eventsAutoTimer = setInterval(() => {
        if (this.eventsAutoRefreshEnabled && this.view === "events")
          this.refreshEvents();
      }, 15_000);

      this._apiKeysAutoTimer = setInterval(() => {
        if (this.apiKeysAutoRefreshEnabled && this.view === "api_keys")
          this.refreshApiKeys();
      }, 20_000);

      this._versionsAutoTimer = setInterval(() => {
        if (this.versionsAutoRefreshEnabled && this.view === "versions")
          this.refreshVersions();
      }, 20_000);

      this._regionsAutoTimer = setInterval(() => {
        if (this.regionsAutoRefreshEnabled && this.view === "regions")
          this.refreshRegions();
      }, 20_000);

      this._settingsAutoTimer = setInterval(() => {
        if (this.settingsAutoRefreshEnabled && this.view === "settings")
          this.refreshSettings();
      }, 20_000);

      if (!routeHandled) {
        await this.ensureCurrentView();
      }
    },

    setView(next) {
      if (next === this.view) return;
      if (!this.isViewAccessible(next)) {
        this.handleForbiddenView(next, { fallback: false });
        return;
      }

      this.clearViewNotice();
      this.view = next;
      localStorage.setItem("cp_view", this.view);
      this.syncHashFromState();
      this.ensureCurrentView();
    },

    openJobsView(clusterId = "") {
      const nextClusterId = String(clusterId || "").trim();
      const contextChanged = this.jobsContextClusterId !== nextClusterId;
      const previousClusterId = this.jobsContextClusterId;
      this.jobsContextClusterId = nextClusterId;
      localStorage.setItem("cp_jobs_context_cluster_id", nextClusterId);
      if (nextClusterId) {
        this.jobsFilterQuery = nextClusterId;
        this.persistJobsFilter();
      } else if (
        previousClusterId &&
        String(this.jobsFilterQuery || "").trim() === previousClusterId
      ) {
        this.jobsFilterQuery = "";
        this.persistJobsFilter();
      }
      if (contextChanged) {
        this.jobs = [];
      }
      if (this.view === "jobs") {
        this.syncHashFromState();
        this.ensureJobsView();
        return;
      }
      this.setView("jobs");
    },

    openJob(jobId) {
      const nextId = String(jobId || "").trim();
      if (!nextId) return;
      if (this.selectedJobId !== nextId) {
        this.selectedJobDetails = null;
      }
      this.selectedJobId = nextId;
      localStorage.setItem("cp_selected_job_id", nextId);
      this.view = "job";
      localStorage.setItem("cp_view", this.view);
      this.clearViewNotice();
      this.syncHashFromState();
      this.ensureJobDetailView();
    },

    backToJobs() {
      this.openJobsView(this.jobsContextClusterId);
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
      if (this.servers.length === 0 && !this.serversLoading.list)
        await this.refreshServers();
      else this.applyServersFilterSort();
    },

    async ensureClusterDetailView() {
      if (!this.selectedClusterId) {
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (
        !this.selectedCluster ||
        this.selectedCluster.cluster_id !== this.selectedClusterId
      ) {
        await this.refreshSelectedCluster();
      }
    },

    async ensureClusterDashboardView() {
      if (!this.selectedClusterId) {
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (
        !this.clusterDashboardSnapshot ||
        this.clusterDashboardSnapshot?.cluster?.cluster_id !== this.selectedClusterId
      ) {
        await this.refreshClusterDashboard();
        return;
      }
      this.renderClusterDashboardCharts();
    },

    async ensureClusterUsersView() {
      if (!this.selectedClusterId) {
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (
        !this.selectedCluster ||
        this.selectedCluster.cluster_id !== this.selectedClusterId
      ) {
        await this.refreshSelectedCluster();
      }
      if (this.clusterUsers.length === 0 && !this.clusterUsersLoading.snapshot) {
        await this.refreshClusterUsers();
      } else {
        this.applyClusterUsersFilter();
      }
    },

    async ensureClusterBackupsView() {
      if (!this.selectedClusterId) {
        this.view = "clusters";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (
        !this.selectedCluster ||
        this.selectedCluster.cluster_id !== this.selectedClusterId
      ) {
        await this.refreshSelectedCluster();
      }
      if (this.clusterBackups.length === 0 && !this.clusterBackupsLoading.snapshot) {
        await this.refreshClusterBackups();
      } else if (
        this.selectedClusterBackupPath &&
        this.clusterBackupDetails.length === 0 &&
        !this.clusterBackupsLoading.details
      ) {
        await this.refreshSelectedBackupDetails();
      }
    },

    async ensureJobsView() {
      if (this.jobs.length === 0 && !this.jobsLoading.list)
        await this.refreshJobs();
      else this.applyJobsFilterSort();
    },

    async ensureJobDetailView() {
      if (!this.selectedJobId) {
        this.view = "jobs";
        localStorage.setItem("cp_view", this.view);
        this.syncHashFromState(true);
        return;
      }
      if (
        !this.selectedJobDetails ||
        this.selectedJobDetails?.job?.job_id !== Number(this.selectedJobId)
      ) {
        await this.refreshSelectedJobDetails();
      }
    },

    async ensureEventsView() {
      if (this.events.length === 0 && !this.eventsLoading.list)
        await this.refreshEvents();
      else this.applyEventsFilterSort();
    },

    async ensureApiKeysView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("api_keys", { fallback: false });
        return;
      }
      if (this.apiKeys.length === 0 && !this.apiKeysLoading.list)
        await this.refreshApiKeys();
      else this.applyApiKeysFilterSort();
    },

    async ensureSettingsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("settings", { fallback: false });
        return;
      }
      if (this.settings.length === 0 && !this.settingsLoading.list)
        await this.refreshSettings();
      else this.applySettingsFilterSort();
    },

    async ensureVersionsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("versions", { fallback: false });
        return;
      }
      if (this.versions.length === 0 && !this.versionsLoading.list)
        await this.refreshVersions();
      else this.applyVersionsFilter();
    },

    async ensureRegionsView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("regions", { fallback: false });
        return;
      }
      if (this.regions.length === 0 && !this.regionsLoading.list)
        await this.refreshRegions();
      else this.applyRegionsFilter();
    },

    async ensureAdminView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("admin", { fallback: false });
        return;
      }
      if (this.settings.length === 0 && !this.settingsLoading.list) {
        await this.refreshSettings();
      } else {
        this.applySettingsFilterSort();
      }
      if (this.versions.length === 0 && !this.versionsLoading.list) {
        await this.refreshVersions();
      } else {
        this.applyVersionsFilter();
      }
      if (this.regions.length === 0 && !this.regionsLoading.list) {
        await this.refreshRegions();
      } else {
        this.applyRegionsFilter();
      }
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
      if (s === "ready") return "status-online";
      if (s === "running") return "status-online";
      if (s === "creating" || s === "scaling" || s === "upgrading")
        return "status-pending status-pulse";
      if (s === "decommissioned") return "status-muted";
      if (s.includes("ing")) return "status-pending status-pulse";
      if (!s || s === "unknown") return "status-muted";
      return "status-offline";
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
      return `${size} GB (${this.getHumanSize(size)})`;
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
      } catch (e) {
        console.error(e);
        this.viewNotice = this.errorMessage(
          e,
          "Failed to load cluster details.",
        );
        this.selectedCluster = null;
      } finally {
        this.clusterLoading.details = false;
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

    clusterConnectCommand(lbOrCluster = this.selectedCluster) {
      const dns = lbOrCluster?.dns_address
        ? String(lbOrCluster.dns_address || "").trim()
        : this.clusterPrimaryDns(lbOrCluster);
      return dns ? `cockroach sql --host=${dns} --port=26257` : "";
    },

    async copyClusterConnectCommand(lbOrCluster = this.selectedCluster) {
      const command = this.clusterConnectCommand(lbOrCluster);
      const dns = lbOrCluster?.dns_address
        ? String(lbOrCluster.dns_address || "").trim()
        : this.clusterPrimaryDns(lbOrCluster);
      if (!command) return;
      if (
        typeof navigator !== "undefined" &&
        navigator.clipboard &&
        typeof navigator.clipboard.writeText === "function"
      ) {
        await navigator.clipboard.writeText(command);
      } else if (typeof document !== "undefined") {
        const el = document.createElement("textarea");
        el.value = command;
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
          ? `Cluster connect command copied for '${dns}'.`
          : "Cluster connect command copied to clipboard.",
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
      this.openJobsView(clusterId);
    },

    openClusterDashboard() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.view = "cluster_dashboard";
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
      this.view = "cluster_users";
      localStorage.setItem("cp_view", this.view);
      this.clearViewNotice();
      this.syncHashFromState();
      this.ensureClusterUsersView();
    },

    openClusterBackups() {
      const clusterId =
        this.selectedCluster?.cluster_id || this.selectedClusterId;
      if (!clusterId) return;
      this.selectedClusterId = String(clusterId).trim();
      localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
      this.view = "cluster_backups";
      localStorage.setItem("cp_view", this.view);
      this.clearViewNotice();
      this.syncHashFromState();
      this.ensureClusterBackupsView();
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
      if (typeof document === "undefined") return 960;
      const el = document.getElementById(containerId);
      const width = Number(el?.clientWidth || el?.offsetWidth || 0);
      return Math.max(width || 960, 320);
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

    clusterDashboardChartOptions({ title, yLabel, containerId, series }) {
      return {
        title,
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
            size: 74,
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
            title: config.title,
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
          localStorage.setItem("cp_selected_cluster_id", this.selectedClusterId);
        }

        if (typeof window !== "undefined") {
          window.requestAnimationFrame(() => this.renderClusterDashboardCharts());
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

    applyClusterUsersFilter() {
      const q = String(this.clusterUsersFilterQuery || "").trim().toLowerCase();
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
      this.clusterUsersLoading.snapshot = true;
      try {
        const snapshot = await this.apiFetch(
          this.visibilityPath(`/clusters/${encodeURIComponent(clusterId)}/users`),
          { method: "GET" },
        );
        this.clusterUsers = Array.isArray(snapshot?.database_users)
          ? snapshot.database_users
          : [];
        if (snapshot?.cluster) {
          this.selectedCluster = snapshot.cluster;
        }
        this.clusterUsersLastUpdatedUtc = this.utcNowString();
        this.applyClusterUsersFilter();
      } catch (e) {
        console.error(e);
        this.clusterUsersLastUpdatedUtc = this.utcNowString();
        this.setActionNotice(
          this.errorMessage(e, "Failed to load cluster users."),
        );
      } finally {
        this.clusterUsersLoading.snapshot = false;
      }
    },

    openClusterUserCreateModal() {
      this.modal.clusterUserCreate.open = true;
      this.modal.clusterUserCreate.username = "";
      this.modal.clusterUserCreate.password = "";
      this.clearModalError("clusterUserCreate");
    },

    closeClusterUserCreateModal() {
      this.modal.clusterUserCreate.open = false;
      this.modal.clusterUserCreate.username = "";
      this.modal.clusterUserCreate.password = "";
      this.clearModalError("clusterUserCreate");
    },

    async createClusterUser() {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(this.modal.clusterUserCreate.username || "").trim();
      const password = String(this.modal.clusterUserCreate.password || "").trim();
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
        await this.apiFetch(`/clusters/${encodeURIComponent(clusterId)}/users`, {
          method: "POST",
          body: { username, password },
        });
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
      const username = String(this.modal.clusterUserPassword.username || "").trim();
      const password = String(this.modal.clusterUserPassword.password || "").trim();
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
      this.modal.clusterUserRoles.roles = Array.isArray(row?.member_of)
        ? row.member_of.filter(Boolean)
        : [];
      this.modal.clusterUserRoles.grantRole = "";
      this.clearModalError("clusterUserRoles");
    },

    closeClusterUserRolesModal() {
      this.modal.clusterUserRoles.open = false;
      this.modal.clusterUserRoles.username = "";
      this.modal.clusterUserRoles.roles = [];
      this.modal.clusterUserRoles.grantRole = "";
      this.clearModalError("clusterUserRoles");
    },

    async revokeClusterUserRole(role) {
      const clusterId = String(this.selectedClusterId || "").trim();
      const username = String(this.modal.clusterUserRoles.username || "").trim();
      const normalizedRole = String(role || "").trim();
      if (!clusterId || !username || !normalizedRole) return;
      this.clusterUsersLoading.revokeRole = true;
      this.clearModalError("clusterUserRoles");
      try {
        await this.apiFetch(
          `/clusters/${encodeURIComponent(clusterId)}/users/${encodeURIComponent(username)}/revoke-role`,
          {
            method: "POST",
            body: { role: normalizedRole },
          },
        );
        this.modal.clusterUserRoles.roles = this.modal.clusterUserRoles.roles.filter(
          (entry) => entry !== normalizedRole,
        );
        await this.refreshClusterUsers();
        this.setActionNotice(
          `Role '${normalizedRole}' revoked from '${username}'.`,
        );
      } catch (e) {
        this.setModalError(
          "clusterUserRoles",
          e,
          "Failed to revoke role.",
        );
      } finally {
        this.clusterUsersLoading.revokeRole = false;
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
          this.visibilityPath(`/clusters/${encodeURIComponent(clusterId)}/backups`),
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
          (entry) => String(entry?.path || "").trim() === this.selectedClusterBackupPath,
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

    jobsDescriptionText(job) {
      return this.toYaml(job?.description ?? null);
    },

    jobTaskDescriptionText(task) {
      if (typeof task?.task_desc === "string") return task.task_desc;
      return this.toYaml(task?.task_desc ?? null);
    },

    selectedJobPrimaryClusterId() {
      const linkedClusters = Array.isArray(
        this.selectedJobDetails?.linked_clusters,
      )
        ? this.selectedJobDetails.linked_clusters
        : [];
      return String(linkedClusters[0]?.cluster_id || "").trim();
    },

    selectedJobDescriptionClusterName() {
      const description = this.selectedJobDetails?.job?.description;
      if (!description || typeof description !== "object") return "";

      const directName = String(
        description.cluster_name ||
          description.name ||
          description.cluster_id ||
          "",
      ).trim();
      if (directName) return directName;

      const deployment = Array.isArray(description.deployment)
        ? description.deployment
        : [];
      return String(deployment[0]?.cluster_name || "").trim();
    },

    selectedJobPrimaryClusterLabel() {
      return (
        this.selectedJobDescriptionClusterName() ||
        this.selectedJobPrimaryClusterId() ||
        "-"
      );
    },

    selectedJobLinkedClusterMeta() {
      const linkedClusters = Array.isArray(
        this.selectedJobDetails?.linked_clusters,
      )
        ? this.selectedJobDetails.linked_clusters
        : [];
      if (linkedClusters.length === 0) {
        return this.selectedJobDescriptionClusterName()
          ? "Cluster name found in the job payload. The linked cluster record is not available yet."
          : "No linked cluster has been recorded for this job yet.";
      }
      if (linkedClusters.length <= 1) {
        return "Open the linked cluster details page.";
      }
      return `${linkedClusters.length} linked clusters returned. Opening the first linked cluster.`;
    },

    async rescheduleSelectedJob() {
      const jobId = String(this.selectedJobId || "").trim();
      if (!jobId) return;
      this.jobLoading.reschedule = true;
      try {
        const result = await this.apiFetch(
          `/jobs/${encodeURIComponent(jobId)}/reschedule`,
          { method: "POST" },
        );
        this.setActionNotice(`Job '${jobId}' rescheduled.`, result?.job_id);
        if (this.jobs.length > 0) {
          await this.refreshJobs();
        }
      } catch (e) {
        console.error(e);
        this.setActionNotice(this.errorMessage(e, "Failed to reschedule job."));
      } finally {
        this.jobLoading.reschedule = false;
      }
    },

    async refreshSelectedJobDetails() {
      const jobId = String(this.selectedJobId || "").trim();
      if (!jobId) return;
      this.jobLoading.details = true;
      try {
        this.selectedJobDetails = await this.apiFetch(
          `/jobs/${encodeURIComponent(jobId)}/details`,
          { method: "GET" },
        );
      } catch (e) {
        console.error(e);
        this.setActionNotice(
          this.errorMessage(e, "Failed to load job details."),
        );
        this.selectedJobDetails = null;
      } finally {
        this.jobLoading.details = false;
      }
    },

    jobsRowText(job) {
      return [
        job?.job_id,
        job?.job_type,
        job?.status,
        job?.created_by,
        job?.created_at,
        job?.updated_at,
        this.jobsDescriptionText(job),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    jobsCellText(job, colIndex) {
      switch (colIndex) {
        case 0:
          return job?.job_id ?? "";
        case 1:
          return job?.job_type || "";
        case 2:
          return job?.status || "";
        case 3:
          return job?.created_by || "";
        case 4:
          return job?.created_at || "";
        case 5:
          return job?.updated_at || "";
        default:
          return "";
      }
    },

    jobsSortClass(index) {
      if (this.jobsSortIndex !== index) return "";
      return this.jobsSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleJobsSort(index) {
      if (this.jobsSortIndex === index)
        this.jobsSortDir = this.jobsSortDir === "asc" ? "desc" : "asc";
      else {
        this.jobsSortIndex = index;
        this.jobsSortDir = index === 0 || index >= 4 ? "desc" : "asc";
      }

      localStorage.setItem("cp_jobs_sort_index", String(this.jobsSortIndex));
      localStorage.setItem("cp_jobs_sort_dir", this.jobsSortDir);
      this.applyJobsFilterSort();
    },

    applyJobsFilterSort() {
      const q = (this.jobsFilterQuery || "").toLowerCase().trim();
      let rows = this.jobs.slice();
      if (q) rows = rows.filter((job) => this.jobsRowText(job).includes(q));

      if (this.jobsSortIndex !== null) {
        const type = this.jobsSortTypeByIndex[this.jobsSortIndex] || "string";
        const idx = this.jobsSortIndex;
        const dir = this.jobsSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.jobsCellText(a, idx));
          const bv = this.parseValue(type, this.jobsCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.jobsVisibleRows = rows;
    },

    persistJobsFilter() {
      localStorage.setItem("cp_jobs_filter", this.jobsFilterQuery || "");
    },

    async onJobsFilterInput() {
      this.persistJobsFilter();
      const query = String(this.jobsFilterQuery || "").trim();
      if (!query && this.jobsContextClusterId) {
        this.jobsContextClusterId = "";
        localStorage.setItem("cp_jobs_context_cluster_id", "");
        this.syncHashFromState();
        this.jobs = [];
        await this.refreshJobs();
        return;
      }
      this.applyJobsFilterSort();
    },

    async refreshJobs() {
      this.jobsLoading.list = true;
      try {
        if (this.jobsContextClusterId) {
          const data = await this.apiFetch(
            this.visibilityPath(
              `/clusters/${encodeURIComponent(this.jobsContextClusterId)}/jobs`,
            ),
            { method: "GET" },
          );
          this.jobs = Array.isArray(data?.jobs) ? data.jobs : [];
          if (!this.jobsFilterQuery) {
            this.jobsFilterQuery = this.jobsContextClusterId;
            this.persistJobsFilter();
          }
        } else {
          const data = await this.apiFetch(this.visibilityPath("/jobs/"), {
            method: "GET",
          });
          this.jobs = Array.isArray(data) ? data : [];
        }
        this.jobsLastUpdatedUtc = this.utcNowString();
        this.applyJobsFilterSort();
      } catch (e) {
        console.error(e);
        this.jobsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.jobsLoading.list = false;
      }
    },

    eventsDetailsText(event) {
      return this.toYaml(event?.details ?? null);
    },

    eventsRowText(event) {
      return [
        event.ts,
        event.user_id,
        event.action,
        event.request_id,
        this.eventsDetailsText(event),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    eventsCellText(event, colIndex) {
      switch (colIndex) {
        case 0:
          return event.ts || "";
        case 1:
          return event.user_id || "";
        case 2:
          return event.action || "";
        case 3:
          return this.eventsDetailsText(event);
        case 4:
          return event.request_id || "";
        default:
          return "";
      }
    },

    eventsSortClass(index) {
      if (this.eventsSortIndex !== index) return "";
      return this.eventsSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleEventsSort(index) {
      if (this.eventsSortIndex === index)
        this.eventsSortDir = this.eventsSortDir === "asc" ? "desc" : "asc";
      else {
        this.eventsSortIndex = index;
        this.eventsSortDir = index === 0 ? "desc" : "asc";
      }

      localStorage.setItem(
        "cp_events_sort_index",
        String(this.eventsSortIndex),
      );
      localStorage.setItem("cp_events_sort_dir", this.eventsSortDir);
      this.applyEventsFilterSort();
    },

    applyEventsFilterSort() {
      const q = (this.eventsFilterQuery || "").toLowerCase().trim();
      let rows = this.events.slice();
      if (q)
        rows = rows.filter((event) => this.eventsRowText(event).includes(q));

      if (this.eventsSortIndex !== null) {
        const type =
          this.eventsSortTypeByIndex[this.eventsSortIndex] || "string";
        const idx = this.eventsSortIndex;
        const dir = this.eventsSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.eventsCellText(a, idx));
          const bv = this.parseValue(type, this.eventsCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.eventsVisibleRows = rows;
    },

    async refreshEvents() {
      this.eventsLoading.list = true;
      try {
        const data = await this.apiFetch(
          this.visibilityPath("/events/", { limit: 200, offset: 0 }),
          { method: "GET" },
        );
        this.events = Array.isArray(data) ? data : [];
        this.eventsLastUpdatedUtc = this.utcNowString();
        this.applyEventsFilterSort();
      } catch (e) {
        console.error(e);
        this.eventsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.eventsLoading.list = false;
      }
    },

    apiKeysRolesText(row) {
      return Array.isArray(row?.roles) && row.roles.length
        ? row.roles.join(", ")
        : "-";
    },

    apiKeysRowText(row) {
      return [
        row?.access_key,
        row?.owner,
        row?.valid_until,
        this.apiKeysRolesText(row),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    apiKeysCellText(row, colIndex) {
      switch (colIndex) {
        case 0:
          return row?.access_key || "";
        case 1:
          return row?.owner || "";
        case 2:
          return row?.valid_until || "";
        case 3:
          return this.apiKeysRolesText(row);
        default:
          return "";
      }
    },

    apiKeysSortClass(index) {
      if (this.apiKeysSortIndex !== index) return "";
      return this.apiKeysSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleApiKeysSort(index) {
      if (this.apiKeysSortIndex === index)
        this.apiKeysSortDir = this.apiKeysSortDir === "asc" ? "desc" : "asc";
      else {
        this.apiKeysSortIndex = index;
        this.apiKeysSortDir = index === 2 ? "desc" : "asc";
      }

      localStorage.setItem(
        "cp_api_keys_sort_index",
        String(this.apiKeysSortIndex),
      );
      localStorage.setItem("cp_api_keys_sort_dir", this.apiKeysSortDir);
      this.applyApiKeysFilterSort();
    },

    applyApiKeysFilterSort() {
      const q = (this.apiKeysFilterQuery || "").toLowerCase().trim();
      let rows = this.apiKeys.slice();
      if (q) rows = rows.filter((row) => this.apiKeysRowText(row).includes(q));

      if (this.apiKeysSortIndex !== null) {
        const type =
          this.apiKeysSortTypeByIndex[this.apiKeysSortIndex] || "string";
        const idx = this.apiKeysSortIndex;
        const dir = this.apiKeysSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.apiKeysCellText(a, idx));
          const bv = this.parseValue(type, this.apiKeysCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.apiKeysVisibleRows = rows;
    },

    persistApiKeysFilter() {
      localStorage.setItem("cp_api_keys_filter", this.apiKeysFilterQuery || "");
    },

    async refreshApiKeys() {
      this.apiKeysLoading.list = true;
      try {
        const data = await this.apiFetch("/admin/api_keys/", { method: "GET" });
        this.apiKeys = Array.isArray(data) ? data : [];
        this.apiKeysLastUpdatedUtc = this.utcNowString();
        this.applyApiKeysFilterSort();
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView("api_keys", { fallback: false });
        }
        console.error(e);
        this.apiKeysLastUpdatedUtc = this.utcNowString();
      } finally {
        this.apiKeysLoading.list = false;
      }
    },

    defaultApiKeyValidUntilUtc() {
      return new Date(Date.now() + 24 * 60 * 60 * 1000)
        .toISOString()
        .replace(/\.\d{3}Z$/, "Z");
    },

    openApiKeyCreateModal() {
      this.clearModalError("apiKeyCreate");
      this.modal.apiKeyCreate.valid_until = this.defaultApiKeyValidUntilUtc();
      this.modal.apiKeyCreate.roles = ["CP_ADMIN"];
      this.modal.apiKeyCreate.open = true;
    },

    closeApiKeyCreateModal() {
      this.modal.apiKeyCreate.open = false;
      this.clearModalError("apiKeyCreate");
    },

    openApiKeyDeleteConfirm(row) {
      this.modal.apiKeyDeleteConfirm.access_key = row?.access_key || "";
      this.modal.apiKeyDeleteConfirm.owner = row?.owner || "";
      this.clearModalError("apiKeyDeleteConfirm");
      this.modal.apiKeyDeleteConfirm.open = true;
    },

    closeApiKeyDeleteConfirm() {
      this.modal.apiKeyDeleteConfirm.open = false;
      this.clearModalError("apiKeyDeleteConfirm");
    },

    closeApiKeySecretModal() {
      this.modal.apiKeySecret.open = false;
      this.modal.apiKeySecret.access_key = "";
      this.modal.apiKeySecret.owner = "";
      this.modal.apiKeySecret.valid_until = "";
      this.modal.apiKeySecret.roles = [];
      this.modal.apiKeySecret.secret_access_key = "";
      this.modal.apiKeySecret.reveal = false;
      this.modal.apiKeySecret.copied = false;
    },

    toggleApiKeySecretVisibility() {
      this.modal.apiKeySecret.reveal = !this.modal.apiKeySecret.reveal;
      this.modal.apiKeySecret.copied = false;
    },

    maskedSecret(secret) {
      const value = String(secret || "");
      return value ? "•".repeat(Math.max(24, value.length)) : "";
    },

    async copyApiKeySecret() {
      if (!this.modal.apiKeySecret.reveal) return;
      const secret = String(this.modal.apiKeySecret.secret_access_key || "");
      if (!secret) return;

      if (
        typeof navigator !== "undefined" &&
        navigator.clipboard &&
        typeof navigator.clipboard.writeText === "function"
      ) {
        await navigator.clipboard.writeText(secret);
      } else if (typeof document !== "undefined") {
        const el = document.createElement("textarea");
        el.value = secret;
        el.setAttribute("readonly", "");
        el.style.position = "absolute";
        el.style.left = "-9999px";
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
      }

      this.modal.apiKeySecret.copied = true;
    },

    async createApiKey() {
      this.apiKeysLoading.create = true;
      this.clearModalError("apiKeyCreate");
      try {
        const validUntil = String(
          this.modal.apiKeyCreate.valid_until || "",
        ).trim();
        if (!validUntil) throw new Error("valid_until is required.");
        if (!validUntil.endsWith("Z")) {
          throw new Error("valid_until must be a UTC timestamp ending in Z.");
        }
        const parsedValidUntil = new Date(validUntil);
        if (Number.isNaN(parsedValidUntil.getTime())) {
          throw new Error("valid_until must be a valid UTC timestamp.");
        }

        const roles = Array.isArray(this.modal.apiKeyCreate.roles)
          ? this.modal.apiKeyCreate.roles.filter(Boolean)
          : [];
        if (roles.length === 0) throw new Error("Select at least one role.");

        const payload = {
          valid_until: parsedValidUntil.toISOString(),
          roles,
        };

        const created = await this.apiFetch("/admin/api_keys/", {
          method: "POST",
          body: payload,
        });

        this.closeApiKeyCreateModal();
        this.modal.apiKeySecret.access_key = created?.access_key || "";
        this.modal.apiKeySecret.owner = created?.owner || "";
        this.modal.apiKeySecret.valid_until = created?.valid_until || "";
        this.modal.apiKeySecret.roles = Array.isArray(created?.roles)
          ? created.roles
          : [];
        this.modal.apiKeySecret.secret_access_key =
          created?.secret_access_key || "";
        this.modal.apiKeySecret.reveal = false;
        this.modal.apiKeySecret.copied = false;
        this.modal.apiKeySecret.open = true;
        await this.refreshApiKeys();
      } catch (e) {
        this.setModalError("apiKeyCreate", e, "Failed to create API key.");
      } finally {
        this.apiKeysLoading.create = false;
      }
    },

    async confirmApiKeyDelete() {
      const accessKey = String(
        this.modal.apiKeyDeleteConfirm.access_key || "",
      ).trim();
      if (!accessKey) return;

      this.apiKeysLoading.delete = true;
      this.clearModalError("apiKeyDeleteConfirm");
      try {
        await this.apiFetch(
          `/admin/api_keys/${encodeURIComponent(accessKey)}`,
          {
            method: "DELETE",
          },
        );
        this.closeApiKeyDeleteConfirm();
        await this.refreshApiKeys();
      } catch (e) {
        this.setModalError(
          "apiKeyDeleteConfirm",
          e,
          "Failed to delete API key.",
        );
      } finally {
        this.apiKeysLoading.delete = false;
      }
    },

    settingsRowText(row) {
      return [
        row?.key,
        row?.category,
        row?.value_type,
        row?.value,
        row?.default_value,
        row?.updated_by,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },

    settingsCellText(row, colIndex) {
      switch (colIndex) {
        case 0:
          return row?.key || "";
        case 1:
          return row?.category || "";
        case 2:
          return row?.value_type || "";
        case 3:
          return row?.value || "";
        case 4:
          return row?.default_value || "";
        case 5:
          return row?.updated_at || "";
        default:
          return "";
      }
    },

    settingsSortClass(index) {
      if (this.settingsSortIndex !== index) return "";
      return this.settingsSortDir === "asc" ? "sort-asc" : "sort-desc";
    },

    toggleSettingsSort(index) {
      if (this.settingsSortIndex === index)
        this.settingsSortDir = this.settingsSortDir === "asc" ? "desc" : "asc";
      else {
        this.settingsSortIndex = index;
        this.settingsSortDir = index === 5 ? "desc" : "asc";
      }

      localStorage.setItem(
        "cp_settings_sort_index",
        String(this.settingsSortIndex),
      );
      localStorage.setItem("cp_settings_sort_dir", this.settingsSortDir);
      this.applySettingsFilterSort();
    },

    applySettingsFilterSort() {
      const q = (this.settingsFilterQuery || "").toLowerCase().trim();
      let rows = this.settings.slice();
      if (q) rows = rows.filter((row) => this.settingsRowText(row).includes(q));

      if (this.settingsSortIndex !== null) {
        const type =
          this.settingsSortTypeByIndex[this.settingsSortIndex] || "string";
        const idx = this.settingsSortIndex;
        const dir = this.settingsSortDir;

        rows.sort((a, b) => {
          const av = this.parseValue(type, this.settingsCellText(a, idx));
          const bv = this.parseValue(type, this.settingsCellText(b, idx));
          if (av < bv) return dir === "asc" ? -1 : 1;
          if (av > bv) return dir === "asc" ? 1 : -1;
          return 0;
        });
      }

      this.settingsVisibleRows = rows;
    },

    persistSettingsFilter() {
      localStorage.setItem(
        "cp_settings_filter",
        this.settingsFilterQuery || "",
      );
    },

    settingDraftValue(row) {
      const key = row?.key;
      if (!key) return "";
      if (Object.prototype.hasOwnProperty.call(this.settingsDrafts, key)) {
        return this.settingsDrafts[key];
      }
      return row?.value || "";
    },

    setSettingDraft(key, value) {
      if (!key) return;
      this.settingsDrafts = {
        ...this.settingsDrafts,
        [key]: String(value ?? ""),
      };
    },

    isSettingDirty(row) {
      return this.settingDraftValue(row) !== String(row?.value || "");
    },

    settingValuePreview(row, value) {
      if (row?.is_secret) return "(hidden)";
      return String(value ?? "") || "-";
    },

    settingSourceLabel(row) {
      return row?.value === null || row?.value === undefined
        ? "Default"
        : "Override";
    },

    async refreshSettings() {
      this.settingsLoading.list = true;
      this.settingsError = "";
      try {
        const existingRowsByKey = Object.fromEntries(
          this.settings.map((row) => [row.key, row]),
        );
        const data = await this.apiFetch("/admin/settings", { method: "GET" });
        const rows = Array.isArray(data)
          ? data
          : Array.isArray(data?.items)
            ? data.items
            : Array.isArray(data?.settings)
              ? data.settings
              : [];
        this.settings = rows;
        this.settingsDrafts = Object.fromEntries(
          this.settings.map((row) => {
            const existing = existingRowsByKey[row.key];
            const existingDraft = this.settingsDrafts[row.key];
            const existingEffective = String(existing?.value || "");
            const nextEffective = String(row.value || "");
            if (
              existingDraft !== undefined &&
              existingDraft !== existingEffective
            ) {
              return [row.key, existingDraft];
            }
            return [row.key, nextEffective];
          }),
        );
        this.settingsLastUpdatedUtc = this.utcNowString();
        this.applySettingsFilterSort();
      } catch (e) {
        if (e?.forbidden) {
          this.handleForbiddenView("settings", { fallback: false });
        }
        this.settingsError = this.errorMessage(e, "Failed to load settings.");
        console.error(e);
        this.settingsLastUpdatedUtc = this.utcNowString();
      } finally {
        this.settingsLoading.list = false;
      }
    },

    async saveSetting(row) {
      const key = row?.key;
      if (!key) return;

      this.settingsLoading.update = true;
      try {
        const updated = await this.apiFetch(
          `/admin/settings/${encodeURIComponent(key)}`,
          {
            method: "PATCH",
            body: { value: this.settingDraftValue(row) },
          },
        );
        this.settings = this.settings.map((entry) =>
          entry.key === updated.key ? updated : entry,
        );
        this.setSettingDraft(updated.key, updated.value || "");
        this.settingsLastUpdatedUtc = this.utcNowString();
        this.applySettingsFilterSort();
      } catch (e) {
        console.error(e);
      } finally {
        this.settingsLoading.update = false;
      }
    },

    openSettingResetConfirm(row) {
      this.modal.settingResetConfirm.key = row?.key || "";
      this.modal.settingResetConfirm.category = row?.category || "";
      this.modal.settingResetConfirm.value_type = row?.value_type || "";
      this.modal.settingResetConfirm.default_value = row?.default_value || "";
      this.modal.settingResetConfirm.is_secret = Boolean(row?.is_secret);
      this.clearModalError("settingResetConfirm");
      this.modal.settingResetConfirm.open = true;
    },

    closeSettingResetConfirm() {
      this.modal.settingResetConfirm.open = false;
      this.clearModalError("settingResetConfirm");
    },

    async confirmSettingReset() {
      const key = String(this.modal.settingResetConfirm.key || "").trim();
      if (!key) return;

      this.settingsLoading.reset = true;
      try {
        const updated = await this.apiFetch(
          `/admin/settings/${encodeURIComponent(key)}`,
          { method: "PUT" },
        );
        this.settings = this.settings.map((entry) =>
          entry.key === updated.key ? updated : entry,
        );
        this.setSettingDraft(updated.key, updated.value || "");
        this.closeSettingResetConfirm();
        this.settingsLastUpdatedUtc = this.utcNowString();
        this.applySettingsFilterSort();
      } catch (e) {
        this.setModalError(
          "settingResetConfirm",
          e,
          "Failed to reset setting.",
        );
      } finally {
        this.settingsLoading.reset = false;
      }
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
    async ensureDashboardView() {
      if (
        this.canViewAdmin() &&
        this.settings.length === 0 &&
        !this.settingsLoading.list
      ) {
        await this.refreshSettings();
      }
      this.applyFilterSort();
    },

    persistFilter() {
      localStorage.setItem("cp_filter", this.filterQuery || "");
    },

    persistServersFilter() {
      localStorage.setItem("cp_servers_filter", this.serversFilterQuery || "");
    },
    persistEventsFilter() {
      localStorage.setItem("cp_events_filter", this.eventsFilterQuery || "");
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

    // ---------- Playbooks lifecycle ----------
    async ensurePlaybooksView() {
      if (!this.canViewAdmin()) {
        this.handleForbiddenView("playbooks", { fallback: false });
        return;
      }
      this.ensureAce();
      if (
        !this.pbLoading.list &&
        (this.playbooks.length === 0 ||
          !this.selectedPlaybook ||
          !this.pbVersions.length)
      )
        await this.reloadPlaybooks();
    },

    ensureAce() {
      if (this._aceReady) return;

      if (!window.ace || !this.$refs.aceContainer) {
        this.pbToast = {
          ok: false,
          message: "Ace not loaded or container missing.",
        };
        return;
      }

      const editor = window.ace.edit(this.$refs.aceContainer);
      editor.setTheme("ace/theme/cobalt");
      editor.session.setMode("ace/mode/yaml");
      editor.setOptions({
        showPrintMargin: false,
        useSoftTabs: true,
        tabSize: 2,
        wrap: true,
      });

      // keep reference
      this._ace = editor;
      this._aceReady = true;
      this.pbEditorReady = true;
      this.pbToast = {
        ok: true,
        message: `${this.utcNowString()} - Editor ready.`,
      };
    },

    async reloadPlaybooks() {
      this.pbLoading.list = true;
      try {
        // Select first by default
        if (this.playbooks.length && !this.selectedPlaybook) {
          this.selectedPlaybook = this.playbooks[0];
        }
        if (this.selectedPlaybook) await this.onSelectPlaybook();

        this.pbToast = {
          ok: true,
          message: `${this.utcNowString()} - Loaded playbooks list (${
            this.playbooks.length
          }).`,
        };
      } catch (e) {
        this.pbToast = { ok: false, message: `List failed: ${e.message}` };
      } finally {
        this.pbLoading.list = false;
      }
    },

    async onSelectPlaybook() {
      if (!this.selectedPlaybook) return;
      if (!this._aceReady || !this._ace) {
        this.pbToast = { ok: false, message: "Editor not ready yet." };
        return;
      }
      await this.loadPlaybookSelection(this.selectedPlaybook);
    },

    extractPlaybookText(payload) {
      if (typeof payload === "string") {
        try {
          return this.b64decode(payload);
        } catch {
          return payload;
        }
      }

      if (payload && typeof payload === "object") {
        const content =
          payload.modified_content ?? payload.original_content ?? "";
        return typeof content === "string" ? content : String(content ?? "");
      }

      return String(payload ?? "");
    },

    applyPlaybookPayload(name, payload, options = {}) {
      const text = this.extractPlaybookText(payload);
      const versions = Array.isArray(payload?.available_versions)
        ? payload.available_versions.map((item) => String(item))
        : this.pbVersions;
      const defaultVersion =
        payload?.default_version != null
          ? String(payload.default_version)
          : this.pbDefaultVersion;
      const selectedVersion = String(
        payload?.playbook_version ||
          options.selectedVersion ||
          defaultVersion ||
          versions[versions.length - 1] ||
          "",
      );

      this.pbVersions = versions;
      this.pbDefaultVersion = defaultVersion;
      this.pbSelectedVersion = selectedVersion;
      this._ace.setValue(text, -1);
      this.pbLastUpdatedUtc = this.utcNowString();
      this.pbToast = {
        ok: true,
        message: `${this.utcNowString()} - Loaded "${name}"${
          selectedVersion ? ` (${selectedVersion})` : ""
        }.`,
      };
    },

    async loadPlaybookSelection(name) {
      this.pbLoading.load = true;
      try {
        const payload = await this.apiFetch(
          `/admin/playbooks/${encodeURIComponent(name)}`,
          { method: "GET" },
        );
        this.applyPlaybookPayload(name, payload);
      } catch (e) {
        this.pbToast = { ok: false, message: `Load failed: ${e.message}` };
      } finally {
        this.pbLoading.load = false;
      }
    },

    async onSelectPlaybookVersion() {
      const name = String(this.selectedPlaybook || "").trim();
      const version = String(this.pbSelectedVersion || "").trim();
      if (!name || !version) return;
      if (!this._aceReady || !this._ace) {
        this.pbToast = { ok: false, message: "Editor not ready yet." };
        return;
      }

      this.pbLoading.load = true;
      try {
        const payload = await this.apiFetch(
          `/admin/playbooks/${encodeURIComponent(name)}/${encodeURIComponent(version)}`,
          { method: "GET" },
        );
        this.applyPlaybookPayload(name, payload, { selectedVersion: version });
      } catch (e) {
        this.pbToast = {
          ok: false,
          message: `Version load failed: ${e.message}`,
        };
      } finally {
        this.pbLoading.load = false;
      }
    },

    // Encode (String → Base64)
    b64encode(str) {
      return btoa(String.fromCodePoint(...new TextEncoder().encode(str)));
    },

    // Decode (Base64 → String)
    b64decode(b64) {
      return new TextDecoder().decode(
        Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)),
      );
    },

    async savePlaybook() {
      if (!this.selectedPlaybook) {
        this.pbToast = { ok: false, message: "Select a playbook first." };
        return;
      }
      if (!this._aceReady || !this._ace) {
        this.pbToast = { ok: false, message: "Editor not ready yet." };
        return;
      }

      this.pbLoading.save = true;

      try {
        const payload = await this.apiFetch(
          `/admin/playbooks/${encodeURIComponent(this.selectedPlaybook)}`,
          {
            method: "POST",
            body: { content: this._ace.getValue() },
          },
        );
        this.applyPlaybookPayload(this.selectedPlaybook, payload);

        this.pbToast = {
          ok: true,
          message: `${this.utcNowString()} - Saved "${this.selectedPlaybook}".`,
        };
      } catch (e) {
        this.pbToast = { ok: false, message: `Save failed: ${e.message}` };
      } finally {
        this.pbLoading.save = false;
      }
    },

    async setDefaultPlaybookVersion() {
      const name = String(this.selectedPlaybook || "").trim();
      const version = String(this.pbSelectedVersion || "").trim();
      if (!name || !version) {
        this.pbToast = {
          ok: false,
          message: "Select a playbook and version first.",
        };
        return;
      }

      this.pbLoading.setDefault = true;
      try {
        await this.apiFetch(
          `/admin/playbooks/${encodeURIComponent(name)}/${encodeURIComponent(version)}`,
          {
            method: "PUT",
          },
        );
        this.pbDefaultVersion = version;
        this.pbToast = {
          ok: true,
          message: `${this.utcNowString()} - Set default for "${name}" to ${version}.`,
        };
      } catch (e) {
        this.pbToast = {
          ok: false,
          message: `Set default failed: ${e.message}`,
        };
      } finally {
        this.pbLoading.setDefault = false;
      }
    },

    openPlaybookVersionDeleteConfirm() {
      if (
        this.pbSelectedVersion &&
        this.pbDefaultVersion &&
        this.pbSelectedVersion === this.pbDefaultVersion
      ) {
        this.pbToast = {
          ok: false,
          message:
            "Promote another version before deleting the current default.",
        };
        return;
      }
      this.modal.playbookVersionDeleteConfirm.version = String(
        this.pbSelectedVersion || "",
      );
      this.clearModalError("playbookVersionDeleteConfirm");
      this.modal.playbookVersionDeleteConfirm.open = true;
    },

    closePlaybookVersionDeleteConfirm() {
      this.modal.playbookVersionDeleteConfirm.open = false;
      this.modal.playbookVersionDeleteConfirm.version = "";
      this.clearModalError("playbookVersionDeleteConfirm");
    },

    async confirmPlaybookVersionDelete() {
      const name = String(this.selectedPlaybook || "").trim();
      const version = String(
        this.modal.playbookVersionDeleteConfirm.version || "",
      ).trim();
      if (!name || !version) return;

      this.pbLoading.delete = true;
      this.clearModalError("playbookVersionDeleteConfirm");
      try {
        const payload = await this.apiFetch(
          `/admin/playbooks/${encodeURIComponent(name)}/${encodeURIComponent(version)}`,
          { method: "DELETE" },
        );
        this.closePlaybookVersionDeleteConfirm();
        this.applyPlaybookPayload(name, payload);
        this.pbToast = {
          ok: true,
          message: `${this.utcNowString()} - Deleted "${name}" version ${version}.`,
        };
      } catch (e) {
        this.setModalError(
          "playbookVersionDeleteConfirm",
          e,
          "Failed to delete playbook version.",
        );
      } finally {
        this.pbLoading.delete = false;
      }
    },
  };
};
