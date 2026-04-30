INSERT INTO mq (msg_type, start_after)
VALUES ('FAIL_ZOMBIE_JOBS', now() + INTERVAL '300s' + (random()*10)::INTERVAL);

INSERT INTO mq (msg_type, start_after)
VALUES ('SYNC_BACKUP_CATALOG', now() + INTERVAL '120s' + (random()*10)::INTERVAL);

INSERT INTO public.settings (
    key,
    default_value,
    value_type,
    category,
    is_secret,
    description
) VALUES
    ('auth.api_key_signature_ttl_seconds', '300', 'integer', 'auth', false, 'Maximum allowed age for signed API key requests in seconds.'),
    ('logging.journald_identifier', 'cp', 'string', 'logging', false, 'Journald identifier used by the control plane logger.'),
    ('logging.level', 'INFO', 'string', 'logging', false, 'Application log verbosity level.'),
    ('storage.s3.url', '', 'url', 'storage', false, 'Base S3 endpoint used for tenant external connections.'),
    ('storage.s3.admin_access_key', '', 'string', 'storage', true, 'Administrative access key used by the control plane to provision buckets and tenant credentials.'),
    ('storage.s3.admin_secret_key', '', 'string', 'storage', true, 'Administrative secret key used by the control plane to provision buckets and tenant credentials.'),
    ('storage.s3.default_retention_days', '', 'integer', 'storage', false, 'Default lifecycle retention applied to tenant backup buckets in days.'),
    ('cluster.default_username', '', 'string', 'cluster', false, 'Default administrative username created in tenant clusters.'),
    ('cockroach.license_key', '', 'string', 'cockroach', true, 'CockroachDB enterprise license key used during provisioning.'),
    ('cockroach.license_org', '', 'string', 'cockroach', false, 'CockroachDB enterprise license organization used during provisioning.'),
    ('observability.prometheus_url', '', 'url', 'observability', false, 'Prometheus base URL used for dashboard and health queries.'),
    ('oidc.cache_ttl_seconds', '300', 'integer', 'oidc', false, 'OIDC metadata and JWKS cache TTL in seconds.'),
    ('oidc.enabled', 'false', 'boolean', 'oidc', false, 'Enable OIDC authentication for the control plane.'),
    ('oidc.issuer_url', '', 'url', 'oidc', false, 'OIDC issuer URL.'),
    ('oidc.client_id', '', 'string', 'oidc', false, 'OIDC client identifier.'),
    ('oidc.client_secret', '', 'string', 'oidc', true, 'OIDC client secret.'),
    ('oidc.scopes', 'openid profile email', 'string', 'oidc', false, 'Space-delimited OIDC scopes requested during login.'),
    ('oidc.audience', '', 'string', 'oidc', false, 'Expected OIDC audience when audience verification is enabled.'),
    ('oidc.extra_auth_params', '{}', 'json', 'oidc', false, 'JSON object of additional OIDC authorization request parameters.'),
    ('oidc.redirect_uri', '', 'url', 'oidc', false, 'OIDC redirect URI handled by the control plane.'),
    ('oidc.login_path', '/auth/login', 'path', 'oidc', false, 'Application path used to initiate OIDC login.'),
    ('oidc.session_max_age_seconds', '2592000', 'integer', 'oidc', false, 'Maximum lifetime of an OIDC-backed control-plane session in seconds.'),
    ('oidc.refresh_leeway_seconds', '60', 'integer', 'oidc', false, 'Time before token expiry when the server should refresh the OIDC session.'),
    ('oidc.cookie_secure', 'true', 'boolean', 'oidc', false, 'Whether OIDC cookies should be marked Secure.'),
    ('oidc.cookie_samesite', 'lax', 'string', 'oidc', false, 'SameSite policy applied to OIDC cookies.'),
    ('oidc.cookie_domain', '', 'string', 'oidc', false, 'Optional domain attribute applied to OIDC cookies.'),
    ('oidc.verify_audience', 'true', 'boolean', 'oidc', false, 'Whether to verify the audience claim in OIDC tokens.'),
    ('oidc.ui_username_claim', 'email', 'string', 'oidc', false, 'OIDC claim displayed as the UI username.'),
    ('oidc.authz_readonly_groups', '', 'csv', 'oidc', false, 'Comma-delimited OIDC groups that map to the read-only control-plane role.'),
    ('oidc.authz_user_groups', '', 'csv', 'oidc', false, 'Comma-delimited OIDC groups that map to the standard user control-plane role.'),
    ('oidc.authz_admin_groups', '', 'csv', 'oidc', false, 'Comma-delimited OIDC groups that map to the admin control-plane role.'),
    ('oidc.authz_groups_claim', 'groups', 'string', 'oidc', false, 'OIDC claim that contains the user''s group memberships.');
