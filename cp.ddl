-- as user root
USE defaultdb;

DROP DATABASE IF EXISTS cp CASCADE;

CREATE DATABASE cp;
USE cp;

CREATE user if not exists cp WITH PASSWORD 'cp';

-- revoke silly default grants from public role
REVOKE connect ON DATABASE cp FROM public;
REVOKE USAGE, CREATE ON schema cp.public FROM public;

GRANT connect ON DATABASE cp TO cp;
GRANT USAGE ON schema cp.public TO cp;


ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT ALL ON TABLES TO cp WITH GRANT OPTION;
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT ALL ON SEQUENCES TO cp WITH GRANT OPTION;


-- MQ
CREATE SEQUENCE mq_seq PER NODE CACHE 100;

CREATE TABLE mq (
    msg_id INT8 NOT NULL DEFAULT nextval('mq_seq'),
    start_after TIMESTAMPTZ NOT NULL default now(),
    msg_type STRING NOT NULL,
    msg_data JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL default 'system',
    CONSTRAINT pk PRIMARY KEY (msg_id ASC)
);

-- plant the seeds
INSERT INTO mq (msg_type) VALUES ('FAIL_ZOMBIE_JOBS');
INSERT INTO mq (msg_type) VALUES ('HEALTHCHECK_CLUSTERS');


ALTER TABLE mq CONFIGURE ZONE USING
    gc.ttlseconds = 120;

-- OBJECTS

CREATE TABLE clusters (
    cluster_id STRING NOT NULL,
    description JSONB NULL,
    status STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    grp STRING,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC)
);

CREATE TABLE jobs (
    job_id INT8 NOT NULL,
    job_type STRING NULL,
    status STRING NULL,
    description JSONB NULL,
    created_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NULL,
    updated_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ on update now(),
    CONSTRAINT pk PRIMARY KEY (job_id ASC)
);

CREATE TABLE map_clusters_jobs (
    cluster_id STRING NOT NULL,
    job_id INT8 NOT NULL,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC, job_id ASC),
    CONSTRAINT cluster_id_in_clusters FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id) ON DELETE CASCADE,
    CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE,
    INDEX map_jobs_clusters (job_id ASC)
);

CREATE TABLE tasks (
  job_id INT8 NOT NULL,
  task_id INT2 NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  task_name STRING NULL,
  task_desc STRING NULL,
  CONSTRAINT pk PRIMARY KEY (job_id ASC, task_id ASC),
  CONSTRAINT job_id_in_jobs FOREIGN KEY (job_id) REFERENCES jobs (job_id) ON DELETE CASCADE
);



CREATE TABLE secrets (
    id STRING NOT NULL,
    data STRING NULL,
    CONSTRAINT pk PRIMARY KEY (id ASC)
);

/* 
    SETTINGS
*/


CREATE TABLE regions (
    cloud STRING NOT NULL,
    region STRING NOT NULL,
    zone STRING NOT NULL,
    vpc_id STRING,
    security_groups STRING[],
    subnet STRING,
    image STRING,
    extras JSONB NULL,
    CONSTRAINT pk PRIMARY KEY (cloud ASC, region ASC, zone ASC)
);

create table versions (
    version STRING not null,
    constraint pk primary key (version)
);

create table cpus_per_node (
    cpus int2 not null,
    constraint pk primary key (cpus)
);

create table nodes_per_region (
    nodes int2 not null,
    constraint pk primary key (nodes)
);

create table disk_sizes (
    size_gb INT2,
    constraint pk primary key (size_gb)
);

CREATE TABLE event_log (
  created_at TIMESTAMPTZ NOT NULL default now(),
  created_by STRING NOT NULL,
  event_type string not null,
  event_details STRING,
  CONSTRAINT pk PRIMARY KEY (created_at, created_by)
) WITH (ttl_expiration_expression = $$(created_at::TIMESTAMPTZ + '90 days')$$, ttl_job_cron = '@daily')
;

-- USERS
CREATE TABLE users (
  username STRING,
  password_hash BYTES, 
  salt BYTES,
  hash_algo STRING,
  iterations INT,
  attempts int2 not null default 0,
  groups string[],
  CONSTRAINT pk primary key (username)
);

create table role_to_groups_mappings (
    role string,
    groups string[],
    constraint pk primary key (role)
);
