#!/usr/bin/env bash
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-cargo_db}"

DB_NAME="${DB_NAME:-cargo_transportation}"
DB_OWNER="${DB_OWNER:-cargo_user}"
DB_PASSWORD="${DB_PASSWORD:-cargo_pass}"

# In this Docker setup, POSTGRES_USER is the cluster superuser.
DB_ADMIN_USER="${DB_ADMIN_USER:-cargo_user}"

echo "[init_db] container=$DB_CONTAINER db=$DB_NAME owner=$DB_OWNER admin=$DB_ADMIN_USER"

# Create role if doesn't exist, set or refresh password
docker exec -i "$DB_CONTAINER" psql -U "$DB_ADMIN_USER" -d postgres <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${DB_OWNER}') THEN
        CREATE ROLE ${DB_OWNER} LOGIN PASSWORD '${DB_PASSWORD}';
    ELSE
        ALTER ROLE ${DB_OWNER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;
SQL

# Create database if doesn't exist and set owner
docker exec -i "$DB_CONTAINER" psql -U "$DB_ADMIN_USER" -d postgres <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}') THEN
        CREATE DATABASE ${DB_NAME} OWNER ${DB_OWNER};
    END IF;
END
\$\$;

ALTER DATABASE ${DB_NAME} OWNER TO ${DB_OWNER};
SQL

echo "[init_db] done"

