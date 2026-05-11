#!/bin/bash
set -e

# This function creates a user and a database, then grants privileges.
# Usage: create_db_and_user <database_name> <user_name> <password>
create_db_and_user() {
    local db=$1
    local user=$2
    local pass=$3

    echo "  Creating user '$user' and database '$db'..."
    
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
        -- Create the user if it doesn't exist
        DO
        \$do\$
        BEGIN
           IF NOT EXISTS (
              SELECT FROM pg_catalog.pg_roles
              WHERE  rolname = '$user') THEN
              CREATE ROLE $user LOGIN PASSWORD '$pass';
           END IF;
        END
        \$do\$;

        -- Create the database if it doesn't exist
        SELECT 'CREATE DATABASE $db OWNER $user'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\gexec
EOSQL
    
    echo "  Granting privileges..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" <<-EOSQL
        GRANT ALL PRIVILEGES ON DATABASE $db TO $user;
        GRANT ALL ON SCHEMA public TO $user;
EOSQL
}

# --- DEFINITIONS FOR YOUR SERVICES ---

# 1. OpenMetadata
create_db_and_user "openmetadata_db" "openmetadata_user" "openmetadata_password"

# 2. Airflow (Ingestion)
create_db_and_user "airflow_db" "airflow_user" "airflow_pass"

# 3. Superset
create_db_and_user "superset" "superset" "superset_password"

# 4. Keycloak
create_db_and_user "keycloak" "keycloak" "keycloak_password"

# 5. Temporal
create_db_and_user "temporal" "temporal" "temporal_password"

create_db_and_user "vda" "vda" "vda_password"

echo "✅ All requested databases and users have been created."
