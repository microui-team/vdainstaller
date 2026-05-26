#!/bin/bash

# Exit on error
set -e

# Target directory
PACKAGE_DIR="/docker/nbe_offline_package"

# Create the target directory if it doesn't exist
mkdir -p "$PACKAGE_DIR"

# Static list of resolved images extracted from vda-deploy.yaml
IMAGES=(
  "microuidigital/superset-app:latest"
  "asia-south1-docker.pkg.dev/izac-349007/reports/docker.getcollate.io/openmetadata/postgresql:1.12.1"
  "redis:7"
  "asia-south1-docker.pkg.dev/izac-349007/reports/docker.elastic.co/elasticsearch/elasticsearch:9.3.0"
  "asia-south1-docker.pkg.dev/izac-349007/ssm-tool/keycloak:21.1.1-local"
  "microuidigital/nginx:latest"
  "asia-south1-docker.pkg.dev/izac-349007/ssm-tool/vda-client:c400a958215603fb0c5e05341bfe12755998aca2"
  "asia-south1-docker.pkg.dev/izac-349007/ssm-tool/vda-server:c400a958215603fb0c5e05341bfe12755998aca2"
  "prohankumar/metadata:2"
  "microuidigital/vda-gitcontrolapp:latest"
  "asia-south1-docker.pkg.dev/izac-349007/reports/docker.getcollate.io/openmetadata/server:1.12.1"
  "asia-south1-docker.pkg.dev/izac-349007/reports/docker.getcollate.io/openmetadata/ingestion:1.12.1"
  "surrealdb/surrealdb:v3.0.5"
  "marquezproject/marquez:latest"
  "marquezproject/marquez-web:latest"
  "qdrant/qdrant:latest"
  "temporalio/auto-setup"
  "temporalio/admin-tools"
  "temporalio/ui"
  "confluentinc/cp-schema-registry:7.6.0"
  "apache/kafka:latest"
  "redis:7.4.0"
  "asia-south1-docker.pkg.dev/izac-349007/reports/dia-server"
  "asia-south1-docker.pkg.dev/izac-349007/reports/di-server"
  "asia-south1-docker.pkg.dev/izac-349007/reports/kc"
  "asia-south1-docker.pkg.dev/izac-349007/reports/local-model:latest"
  "asia-south1-docker.pkg.dev/izac-349007/reports/pyspark-notebook"
  "asia-south1-docker.pkg.dev/izac-349007/reports/lakekeeper"
  "curlimages/curl"
  "postgres:17"
  "minio/minio:RELEASE.2025-07-23T15-54-02Z"
  "trinodb/trino:476"
  "starrocks/allin1-ubuntu:4.0.1"
  "risingwavelabs/risingwave:v2.7.1"
  "asia-south1-docker.pkg.dev/izac-349007/reports/offline-rpms"
  "asia-south1-docker.pkg.dev/izac-349007/reports/offline-venv"
)

echo "Preparing to process ${#IMAGES[@]} docker images..."
echo "Output package directory: $PACKAGE_DIR"

# Pull and save images
for img in "${IMAGES[@]}"; do
  echo -e "\n--- Processing: $img ---"
  
  echo "Running: docker pull $img"
  if ! docker pull "$img"; then
    echo "Warning: Failed to pull $img. Skipping..."
    continue
  fi
  
  # Create a safe filename for the tar by substituting '/' and ':' with '_'
  safe_name=$(echo "$img" | sed 's/[\/:]/_/g').tar
  tar_path="$PACKAGE_DIR/$safe_name"
  
  echo "Running: docker save -o $tar_path $img"
  if docker save -o "$tar_path" "$img"; then
    echo "Successfully saved $img to $tar_path"
  else
    echo "Error: Failed to save $img"
  fi
done

echo -e "\nFinished processing all images!"
