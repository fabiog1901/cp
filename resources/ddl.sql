CREATE SEQUENCE public.mq_seq MINVALUE 1 MAXVALUE 9223372036854775807 INCREMENT 1 START 1 PER NODE CACHE 100;
CREATE TABLE public.mq (
    msg_id INT8 NOT NULL DEFAULT nextval('public.mq_seq'::REGCLASS),
    start_after TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    msg_type STRING NOT NULL,
    msg_data JSONB NOT NULL DEFAULT '{}':::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL DEFAULT 'system':::STRING,
    CONSTRAINT pk PRIMARY KEY (msg_id ASC)
);
CREATE TABLE public.clusters (
    cluster_id STRING NOT NULL,
    cluster_inventory JSONB NOT NULL DEFAULT '[]':::JSONB,
    lbs_inventory JSONB NOT NULL DEFAULT '[]':::JSONB,
    version STRING NULL,
    node_count INT2 NULL,
    node_cpus INT2 NULL,
    disk_size INT2 NULL,
    status STRING NOT NULL,
    grp STRING NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    password BYTES NOT NULL DEFAULT '\x':::BYTES,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC)
);
CREATE TABLE public.jobs (
    job_id INT8 NOT NULL,
    job_type STRING NULL,
    status STRING NULL,
    description JSONB NULL,
    created_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    CONSTRAINT pk PRIMARY KEY (job_id ASC)
);
CREATE TABLE public.map_clusters_jobs (
    cluster_id STRING NOT NULL,
    job_id INT8 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC, job_id ASC),
    INDEX map_jobs_clusters (job_id ASC)
);
CREATE TABLE public.tasks (
    job_id INT8 NOT NULL,
    task_id INT2 NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    task_name STRING NULL,
    task_desc STRING NULL,
    CONSTRAINT pk PRIMARY KEY (job_id ASC, task_id ASC)
);
CREATE TABLE public.regions (
    cloud STRING NOT NULL,
    region STRING NOT NULL,
    zone STRING NOT NULL,
    vpc_id STRING NULL,
    security_groups STRING[] NULL,
    subnet STRING NULL,
    image STRING NULL,
    extras JSONB NULL,
    CONSTRAINT pk PRIMARY KEY (cloud ASC, region ASC, zone ASC)
);
CREATE TABLE public.versions (
    version STRING NOT NULL,
    CONSTRAINT pk PRIMARY KEY (version ASC)
);
CREATE TABLE public.cpus_per_node (
    cpu_count INT2 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (cpu_count ASC)
);
CREATE TABLE public.nodes_per_region (
    node_count INT2 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (node_count ASC)
);
CREATE TABLE public.disk_sizes (
    size_gb INT2 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (size_gb ASC)
);
CREATE TABLE public.role_to_groups_mappings (
    "role" STRING NOT NULL,
    groups STRING[] NULL,
    CONSTRAINT pk PRIMARY KEY ("role" ASC)
);
CREATE TABLE public.event_log (
    ts TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    user_id STRING NOT NULL,
    action STRING NOT NULL,
    details JSONB NULL,
    request_id UUID NULL,
    CONSTRAINT pk PRIMARY KEY (ts ASC, user_id ASC)
) WITH (ttl = 'on', ttl_expiration_expression = e'(ts::TIMESTAMPTZ + \'90 days\')', ttl_job_cron = '@daily');
CREATE TABLE public.live_alerts (
    fingerprint STRING NOT NULL,
    receiver STRING NOT NULL,
    payload_status STRING NOT NULL,
    alert_name STRING NULL,
    severity STRING NULL,
    status STRING NOT NULL,
    labels JSONB NOT NULL DEFAULT '{}':::JSONB,
    annotations JSONB NOT NULL DEFAULT '{}':::JSONB,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    group_labels JSONB NOT NULL DEFAULT '{}':::JSONB,
    common_labels JSONB NOT NULL DEFAULT '{}':::JSONB,
    common_annotations JSONB NOT NULL DEFAULT '{}':::JSONB,
    external_url STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    CONSTRAINT pk_live_alerts PRIMARY KEY (fingerprint ASC)
);
CREATE TABLE public.playbooks (
    name STRING NOT NULL,
    version TIMESTAMPTZ(0) NOT NULL DEFAULT now():::TIMESTAMPTZ,
    content BYTES NULL,
    created_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NULL,
    default_version TIMESTAMPTZ NULL,
    updated_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (name ASC, version ASC)
);
CREATE TABLE public.settings (
    key STRING NOT NULL,
    value STRING NULL,
    default_value STRING NULL,
    value_type STRING NULL,
    category STRING NULL,
    is_secret BOOL NULL DEFAULT false,
    description STRING NULL DEFAULT '':::STRING,
    updated_at TIMESTAMPTZ NULL,
    updated_by STRING NULL,
    CONSTRAINT pk_settings PRIMARY KEY (key ASC)
);
CREATE TABLE public.api_keys (
    access_key STRING NOT NULL,
    encrypted_secret_access_key BYTES NOT NULL,
    owner STRING NOT NULL,
    valid_until TIMESTAMPTZ NOT NULL,
    roles STRING[] NULL,
    CONSTRAINT pk_api_keys PRIMARY KEY (access_key ASC)
);
CREATE TABLE public.oidc_sessions (
    session_id STRING NOT NULL,
    encrypted_id_token BYTES NOT NULL,
    encrypted_refresh_token BYTES NULL,
    token_expires_at TIMESTAMPTZ NOT NULL,
    session_expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    CONSTRAINT pk_oidc_sessions PRIMARY KEY (session_id ASC)
) WITH (ttl = 'on', ttl_expiration_expression = e'(session_expires_at)', ttl_job_cron = '@hourly');
ALTER TABLE public.map_clusters_jobs ADD CONSTRAINT cluster_id_in_clusters FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;
ALTER TABLE public.map_clusters_jobs ADD CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE;
ALTER TABLE public.tasks ADD CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE;
ALTER TABLE public.map_clusters_jobs VALIDATE CONSTRAINT cluster_id_in_clusters;
ALTER TABLE public.map_clusters_jobs VALIDATE CONSTRAINT job_id_in_jobs;
ALTER TABLE public.tasks VALIDATE CONSTRAINT job_id_in_jobs;
