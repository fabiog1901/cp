# cp

## SSO integration with Keycloak

Install and setup Keycloak as per [blog post](https://dev.to/cockroachlabs/cockroachdb-sso-integration-using-keycloak-4b17).

## Develop

1. Start CockroachDB cluster

    The cluster should have database `cp` created.

2. Start Keycloak

    ```bash
    /opt/keycloak-26.2.5/bin/kc.sh start-dev --http-port 8081 \
      --db-url-host=localhost --db-password=postgres \
      --db-username=fabio --db postgres
    ```

3. Start Prometheus server

    ```bash
    ./prometheus --config.file=prometheus.yaml \
      --enable-feature=auto-reload-config \
      --config.auto-reload-interval=30s
    ```

4. Start Reflex

    ```bash
    poetry shell
    REFLEX_HOT_RELOAD_EXCLUDE_PATHS="/Users/fabio/projects/cp/playbooks" reflex run
    ```
