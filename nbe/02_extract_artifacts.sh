#!/bin/bash
set -e

# Default registry if none provided
REGISTRY=${1:-"asia-south1-docker.pkg.dev/izac-349007/reports"}
OUTPUT_DIR="/docker/nbe_offline_package"

echo "=== 1. Pulling Images from Registry ==="
docker pull ${REGISTRY}/offline-rpms:latest
docker pull ${REGISTRY}/offline-venv:latest

echo "=== 2. Creating Local Output Directory ==="
mkdir -p ${OUTPUT_DIR}/rpms

echo "=== 3. Extracting System RPMs ==="
docker run --rm -v $(pwd)/${OUTPUT_DIR}/rpms:/export ${REGISTRY}/offline-rpms:latest bash -c "cp -r /rpms/* /export/"

echo "=== 4. Extracting Python Wheels, Jars, and Scripts ==="
docker run --rm -v $(pwd)/${OUTPUT_DIR}:/export ${REGISTRY}/offline-venv:latest bash -c "cp /artifacts/wheelhouse.tar.gz /export/ && cp /artifacts/jars.tar.gz /export/ && cp /build/requirements.txt /export/ && cp /artifacts/03_install_on_mapr.sh /export/ && cp /artifacts/poc_metrics.py /export/ && cp /artifacts/*.txt /export/ || true"

chmod +x ${OUTPUT_DIR}/03_install_on_mapr.sh || true

echo "=========================================================="
echo "SUCCESS! The directory '${OUTPUT_DIR}' is fully prepared."
echo "You can now compress it or SCP it directly to the MapR nodes."
echo "Example: scp -r ${OUTPUT_DIR} user@mapr-node:/tmp/"
echo "Once transferred, run '03_install_on_mapr.sh' on the MapR node."
echo "=========================================================="
