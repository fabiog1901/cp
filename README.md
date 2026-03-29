# cp

🌍 `cp` is a control plane for CockroachDB clusters and a DBaaS-style platform for operating them safely and consistently.

It is designed to let teams create, manage, and monitor CockroachDB clusters across public clouds and, when integrated, private cloud environments too. The platform is secured through SSO login via an identity provider using OIDC, and auditable user actions are preserved internally in an event log so operational changes remain traceable over time.

At a solution level, this repository contains the application itself, but the full platform also depends on a CockroachDB cluster to store metadata and back the internal message queue, plus a Prometheus server to power dashboard queries and cluster health visibility. Integration with Alertmanager is a natural next step and is planned as a potential path for active alerting. 📈

It combines:

- 🖥️ a web UI built with Reflex
- 🧠 a service layer that contains business logic
- 🗄️ a repository layer for Postgres/CockroachDB access
- ⚙️ background workers that run cluster jobs through Ansible
- 🔐 SSO integration for authentication and authorization
- 📈 Prometheus-backed dashboards for cluster metrics

## 🌱 Application Architecture Overview

`cp` is built as a stateless application tier made up of a webapp frontend and a FastAPI backend. Application instances do not keep durable runtime state locally, which means multiple identical copies can be provisioned behind a load balancer to support high availability and horizontal scaling.

The stateful parts of the platform live outside the app tier. CockroachDB stores platform metadata and also backs the internal message queue used for asynchronous cluster operations. Prometheus provides the metrics source for dashboards and health visibility, while the workers execute longer-running operational workflows such as provisioning, scaling, upgrades, restores, and health checks.

At a high level, the architecture separates cleanly into:

- a stateless webapp and API layer that serves the UI and handles requests
- a shared CockroachDB/Postgres-compatible data layer for metadata and queued work
- background workers that pull queued jobs and run infrastructure automation
- a Prometheus integration for observability and cluster health views

This setup keeps the application tier easy to replicate, while the database, queue, and monitoring systems provide the shared state and coordination needed by the platform.

## ✨ Features

- Cluster lifecycle management including create, scale, upgrade, restore, and delete workflows.
- Cluster inventory and detail views for browsing managed CockroachDB deployments.
- Job tracking and rescheduling for asynchronous operational tasks.
- Backup management including backup discovery, backup detail inspection, and restore operations.
- Database user management including create, delete, password rotation, and role revocation.
- Observability features backed by Prometheus for dashboards and cluster health visibility.
- Request logging and runtime diagnostics to support operational visibility and troubleshooting.
- Auditing of user actions through an internal event log for traceability and accountability.
- Administrative management for settings, regions, versions, playbooks, and API keys.
