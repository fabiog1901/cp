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

CREATE SEQUENCE mq_seq PER NODE CACHE 100;

CREATE TABLE mq (
    msg_id INT8 NOT NULL DEFAULT nextval('mq_seq'),
    msg_type STRING NOT NULL,
    msg_data JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    CONSTRAINT pk PRIMARY KEY (msg_id ASC)
);

ALTER TABLE mq CONFIGURE ZONE USING
    gc.ttlseconds = 120;

CREATE TABLE clusters (
    cluster_id STRING NOT NULL,
    topology JSONB NULL,
    status STRING NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC)
);

CREATE TABLE jobs (
    cluster_id STRING NOT NULL,
    job_id UUID NOT NULL,
    job_type STRING NULL,
    status STRING NULL,
    created_at TIMESTAMPTZ NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NULL,
    CONSTRAINT pk PRIMARY KEY (cluster_id ASC, job_id ASC),
    CONSTRAINT cluster_id_in_clusters FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id) ON DELETE CASCADE
);

CREATE TABLE tasks (
  cluster_id STRING NOT NULL,
  job_id UUID NOT NULL,
  task_id INT2 NOT NULL,
  progress INT2 NULL,
  created_at TIMESTAMPTZ NOT NULL,
  event STRING NULL,
  event_data JSONB NULL,
  CONSTRAINT pk PRIMARY KEY (job_id ASC, task_id ASC),
  CONSTRAINT cluster_id_job_id_in_jobs FOREIGN KEY (cluster_id, job_id) REFERENCES jobs (cluster_id, job_id) ON DELETE CASCADE
);



-- TODO
CREATE TABLE event_log (
  created_at TIMESTAMPTZ NOT NULL default now(),
  created_by STRING NOT NULL,
  event_type string not null,
  event_details STRING,
  CONSTRAINT pk PRIMARY KEY (created_at, created_by)
) WITH (ttl_expiration_expression = $$(created_at::TIMESTAMPTZ + '90 days')$$, ttl_job_cron = '@daily')
;
