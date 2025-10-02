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
    msg_data JSONB NOT NULL default '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL default 'system',
    CONSTRAINT pk PRIMARY KEY (msg_id ASC)
);

-- plant the seeds
INSERT INTO mq (msg_type) VALUES ('FAIL_ZOMBIE_JOBS');
INSERT INTO mq (msg_type) VALUES ('HEALTHCHECK_CLUSTERS');
INSERT INTO mq (msg_type) VALUES ('GATHER_BACKUPS');


ALTER TABLE mq CONFIGURE ZONE USING
    gc.ttlseconds = 120;

-- OBJECTS

CREATE TABLE clusters (
    cluster_id STRING NOT NULL,
    cluster_inventory JSONB NOT NULL default '[]',
    lbs_inventory JSONB NOT NULL default '[]',
    version STRING NULL,
    node_count INT2 NULL,
    node_cpus INT2 NULL,
    disk_size INT2 NULL,
    status STRING NOT NULL,
    grp STRING,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ,
    created_by STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now():::TIMESTAMPTZ ON UPDATE now():::TIMESTAMPTZ,
    updated_by STRING NOT NULL,
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
create table settings (
    id string not null,
    value string,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() ON UPDATE now(),
    updated_by string,
    default_value string,
    description string,
    constraint pk primary key (id)
);


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
  event_details JSONB,
  CONSTRAINT pk PRIMARY KEY (created_at, created_by)
) WITH (ttl_expiration_expression = $$(created_at::TIMESTAMPTZ + '90 days')$$, ttl_job_cron = '@daily')
;

create table role_to_groups_mappings (
    role string NOT NULL,
    groups string[] NULL,
    constraint pk primary key (role)
);
-- currently there are only 3 roles. The table shouldn't have therefore no more than 3 rows
insert into role_to_groups_mappings (role) values ('ro'), ('rw'), ('admin'); 


/*
    FAKE DATA
*/
insert into versions values ('v25.1.0'), ('v25.2.0'), ('v25.2.5');
insert into cpus_per_node values (2), (4), (8), (16);
insert into nodes_per_region values (1), (2), (3), (4);
insert into disk_sizes values (500), (1000), (2000);

insert into regions values ('gcp', 'us-east4', 'a', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-east4', 'b', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-east4', 'c', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-central1', 'a', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-central1', 'b', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-central1', 'c', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-east1', 'd', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-east1', 'b', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );
insert into regions values ('gcp', 'us-east1', 'c', 'default', array['cockroachdb'], 'default', 'projects/ubuntu-os-cloud/global/images/family/ubuntu-2404-lts-amd64', '{}' );

insert into regions values ('aws', 'us-east-1', 'a', 'vpc-039dd158f86366108', array['sg-067d280fe7a21bc60'], 'subnet-0d933a012de53be58', '/canonical/ubuntu/server/24.04', '{}' );
insert into regions values ('aws', 'us-east-1', 'b', 'vpc-039dd158f86366108', array['sg-067d280fe7a21bc60'], 'subnet-0a10df84fd63e9e29', '/canonical/ubuntu/server/24.04', '{}' );
insert into regions values ('aws', 'us-east-1', 'c', 'vpc-039dd158f86366108', array['sg-067d280fe7a21bc60'], 'subnet-0838bb993e9d878eb', '/canonical/ubuntu/server/24.04', '{}' );

insert into regions values ('aws', 'ca-central-1', 'a', 'vpc-0289741dc46c80da8', array['sg-0e3631bbd91d95940'], 'subnet-02ed0abd3c499dca9', '/canonical/ubuntu/server/24.04', '{}' );
insert into regions values ('aws', 'ca-central-1', 'b', 'vpc-0289741dc46c80da8', array['sg-0e3631bbd91d95940'], 'subnet-057e35614fa949783', '/canonical/ubuntu/server/24.04', '{}' );
insert into regions values ('aws', 'ca-central-1', 'c', 'vpc-0289741dc46c80da8', array['sg-0e3631bbd91d95940'], 'subnet-05cd5b8d26347f3a3', '/canonical/ubuntu/server/24.04', '{}' );




