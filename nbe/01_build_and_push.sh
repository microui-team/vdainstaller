#!/bin/bash
set -e

# macOS often creates these hidden metadata files that break docker build's xattr reading.
find . -name "._*" -delete 2>/dev/null || true

# Default registry if none provided
REGISTRY=${1:-"asia-south1-docker.pkg.dev/izac-349007/reports"}

echo "=== 1. Building Base Image ==="
docker build -t offline-base -f Dockerfile.base .

echo "=== 2. Building RPM Bundle Image ==="
docker build -t ${REGISTRY}/offline-rpms:latest -f Dockerfile.rpm_bundle .

echo "=== 3. Building Wheelhouse and Jars Image ==="
docker build -t ${REGISTRY}/offline-venv:latest -f Dockerfile.venv .

echo "=== 4. Pushing Images to Registry ==="
docker push ${REGISTRY}/offline-rpms:latest
docker push ${REGISTRY}/offline-venv:latest

echo "=========================================================="
echo "SUCCESS! Images pushed to ${REGISTRY}"
echo "You can now run '02_extract_artifacts.sh ${REGISTRY}' on the client's Docker node."
echo "=========================================================="
