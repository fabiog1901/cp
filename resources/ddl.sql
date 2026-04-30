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
) WITH (
    ttl = 'on',
    ttl_expiration_expression = e'(CASE WHEN status = \'DELETED\' THEN updated_at::TIMESTAMPTZ + \'90 days\'::INTERVAL ELSE NULL END)',
    ttl_job_cron = '@daily'
);
CREATE TABLE public.external_connections (
    cluster_id STRING NOT NULL,
    name STRING NOT NULL,
    connection_type STRING NOT NULL,
    provider STRING NOT NULL,
    endpoint STRING NOT NULL,
    bucket_name STRING NULL,
    access_key_id STRING NULL,
    encrypted_secret_access_key BYTES NULL,
    metadata JSONB NOT NULL DEFAULT '{}':::JSONB,
    status STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    CONSTRAINT pk_external_connections PRIMARY KEY (cluster_id ASC, name ASC)
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
) WITH (
    ttl = 'on',
    ttl_expiration_expression = e'(updated_at::TIMESTAMPTZ + \'90 days\'::INTERVAL)',
    ttl_job_cron = '@daily'
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
CREATE TABLE public.database_role_templates (
    database_role_template STRING NOT NULL,
    scope_type STRING NOT NULL DEFAULT 'schema':::STRING,
    sql_statement STRING NOT NULL,
    CONSTRAINT pk_database_role_templates PRIMARY KEY (database_role_template ASC)
);
CREATE TABLE public.cluster_database_objects (
    cluster_id STRING NOT NULL,
    database_name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    CONSTRAINT pk_cluster_database_objects PRIMARY KEY (cluster_id ASC, database_name ASC),
    CONSTRAINT fk_cluster_database_objects_cluster_id_ref_clusters FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE
);
CREATE TABLE public.cluster_database_roles (
    cluster_id STRING NOT NULL,
    database_name STRING NOT NULL,
    schema_name STRING NULL,
    database_role STRING NOT NULL,
    database_role_template STRING NOT NULL,
    scope_type STRING NOT NULL,
    sql_statement STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    CONSTRAINT pk_cluster_database_roles PRIMARY KEY (cluster_id ASC, database_role ASC),
    CONSTRAINT fk_cluster_database_roles_cluster_id_ref_clusters FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE,
    CONSTRAINT fk_cluster_database_roles_database_object_ref_cluster_database_objects FOREIGN KEY (cluster_id, database_name) REFERENCES public.cluster_database_objects(cluster_id, database_name) ON DELETE CASCADE,
    CONSTRAINT fk_cluster_database_roles_template_ref_database_role_templates FOREIGN KEY (database_role_template) REFERENCES public.database_role_templates(database_role_template)
);
CREATE TABLE public.cluster_backup_catalog (
    cluster_id STRING NOT NULL,
    backup_path STRING NOT NULL,
    grp STRING NULL,
    backup_type STRING NULL,
    start_time TIMESTAMPTZ NULL,
    end_time TIMESTAMPTZ NULL,
    is_full_cluster BOOL NOT NULL DEFAULT false,
    status STRING NOT NULL,
    object_count INT8 NOT NULL DEFAULT 0,
    last_seen_at TIMESTAMPTZ NULL,
    sync_error STRING NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    CONSTRAINT pk_cluster_backup_catalog PRIMARY KEY (cluster_id ASC, backup_path ASC),
    INDEX idx_cluster_backup_catalog_group_full (grp ASC, is_full_cluster ASC, end_time DESC),
    CONSTRAINT fk_cluster_backup_catalog_cluster_id_ref_clusters FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE
);
CREATE TABLE public.cluster_backup_catalog_objects (
    cluster_id STRING NOT NULL,
    backup_path STRING NOT NULL,
    ordinal INT8 NOT NULL,
    database_name STRING NULL,
    parent_schema_name STRING NULL,
    object_name STRING NULL,
    object_type STRING NULL,
    backup_type STRING NULL,
    start_time TIMESTAMPTZ NULL,
    end_time TIMESTAMPTZ NULL,
    size_bytes INT8 NULL,
    row_count INT8 NULL,
    is_full_cluster BOOL NULL,
    regions STRING NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT pk_cluster_backup_catalog_objects PRIMARY KEY (cluster_id ASC, backup_path ASC, ordinal ASC),
    CONSTRAINT fk_cluster_backup_catalog_objects_backup_ref_catalog FOREIGN KEY (cluster_id, backup_path) REFERENCES public.cluster_backup_catalog(cluster_id, backup_path) ON DELETE CASCADE
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
    alert_type STRING NOT NULL,
    cluster STRING NULL,
    nodes STRING[] NULL,
    summary STRING NULL,
    description STRING NULL,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    CONSTRAINT pk_live_alerts PRIMARY KEY (fingerprint ASC)
) WITH (ttl = 'on', ttl_expiration_expression = e'(updated_at::TIMESTAMPTZ + \'90 days\')', ttl_job_cron = '@daily');
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
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
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
ALTER TABLE public.external_connections ADD CONSTRAINT cluster_id_in_external_connections FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;
ALTER TABLE public.tasks ADD CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES public.jobs(job_id) ON DELETE CASCADE;
