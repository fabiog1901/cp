-- CP tables are in the public schema
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
CREATE TABLE public.map_clusters_jobs (
    cluster_id STRING NOT NULL,
    job_id INT8 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC, job_id ASC),
    INDEX map_jobs_clusters (job_id ASC),
    CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES cpkit.jobs(job_id) ON DELETE CASCADE
);
CREATE TABLE public.cluster_artifact_catalog (
    artifact_id STRING NOT NULL,
    job_id INT8 NOT NULL,
    cluster_id STRING NOT NULL,
    kind STRING NOT NULL,
    status STRING NOT NULL DEFAULT 'RUNNING':::STRING,
    artifact_name STRING NOT NULL,
    bucket STRING NULL,
    object_key STRING NOT NULL,
    size_bytes INT8 NULL,
    sha256 STRING NULL,
    redacted BOOL NOT NULL DEFAULT true,
    metadata JSONB NOT NULL DEFAULT '{}':::JSONB,
    expires_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NULL,
    CONSTRAINT pk_cluster_artifact_catalog PRIMARY KEY (artifact_id ASC),
    INDEX cluster_artifact_catalog_job_idx (job_id ASC),
    INDEX cluster_artifact_catalog_cluster_idx (cluster_id ASC)
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
CREATE TABLE public.cluster_database_role_group_mappings (
    cluster_id STRING NOT NULL,
    database_role STRING NOT NULL,
    group_name STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    CONSTRAINT pk_cluster_database_role_group_mappings PRIMARY KEY (cluster_id ASC, database_role ASC, group_name ASC),
    CONSTRAINT fk_cluster_database_role_group_mappings_role_ref_cluster_database_roles FOREIGN KEY (cluster_id, database_role) REFERENCES public.cluster_database_roles(cluster_id, database_role) ON DELETE CASCADE
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

ALTER TABLE public.map_clusters_jobs ADD CONSTRAINT cluster_id_in_clusters FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;
ALTER TABLE public.external_connections ADD CONSTRAINT cluster_id_in_external_connections FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;
ALTER TABLE public.cluster_artifact_catalog ADD CONSTRAINT job_id_in_cluster_artifact_catalog FOREIGN KEY (job_id) REFERENCES cpkit.jobs(job_id) ON DELETE CASCADE;
ALTER TABLE public.cluster_artifact_catalog ADD CONSTRAINT cluster_id_in_cluster_artifact_catalog FOREIGN KEY (cluster_id) REFERENCES public.clusters(cluster_id) ON DELETE CASCADE;


-- seed recurring job
INSERT INTO cpkit.mq (msg_type, start_after)
VALUES ('SYNC_BACKUP_CATALOG', now() + INTERVAL '120s' + (random()*10)::INTERVAL);

-- cp specific settings
INSERT INTO cpkit.settings (
    key,
    default_value,
    value_type,
    category,
    is_secret,
    description
) VALUES
    ('storage.s3.url',                    '', 'url',     'storage',       false, 'Base S3 endpoint used for tenant external connections.'),
    ('storage.s3.admin_access_key',       '', 'string',  'storage',       true,  'Administrative access key used by the control plane to provision buckets and tenant credentials.'),
    ('storage.s3.admin_secret_key',       '', 'string',  'storage',       true,  'Administrative secret key used by the control plane to provision buckets and tenant credentials.'),
    ('storage.s3.default_retention_days', '', 'integer', 'storage',       false, 'Default lifecycle retention applied to tenant backup buckets in days.'),
    ('cluster.default_username',          '', 'string',  'cluster',       false, 'Default administrative username created in tenant clusters.'),
    ('cockroach.license_key',             '', 'string',  'cockroach',     true,  'CockroachDB enterprise license key used during provisioning.'),
    ('cockroach.license_org',             '', 'string',  'cockroach',     false, 'CockroachDB enterprise license organization used during provisioning.'),
    ('observability.prometheus_url',      '', 'url',     'observability', false, 'Prometheus base URL used for dashboard and health queries.')
ON CONFLICT (key) DO NOTHING;

-- cp specific playbooks. the yaml content is done via the webapp.
INSERT INTO cpkit.playbooks (name, content, created_by, default_version, updated_by)
VALUES
    ('CREATE_CLUSTER',      NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('DELETE_CLUSTER',      NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('SCALE_CLUSTER_IN',    NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('SCALE_CLUSTER_OUT',   NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('SCALE_DISK_SIZE',     NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('SCALE_NODE_CPUS',     NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('UPGRADE_CLUSTER',     NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('HEALTHCHECK_CLUSTER', NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('DEBUG_ZIP_CLUSTER',   NULL, 'system', now():::TIMESTAMPTZ, 'system'),
    ('POLL_DEBUG_ZIP',      NULL, 'system', now():::TIMESTAMPTZ, 'system')
;
