#!/bin/bash
set -e

# Default registry if none provided
REGISTRY=${1:-"asia-south1-docker.pkg.dev/izac-349007/reports"}
OUTPUT_DIR="/docker/nbe_offline_package"

docker pull ${REGISTRY}/offline-rpms:latest
docker pull ${REGISTRY}/offline-venv:latest

rm -rf ${OUTPUT_DIR}
mkdir -p ${OUTPUT_DIR}/rpms

docker run --rm -v $(pwd)/${OUTPUT_DIR}/rpms:/export ${REGISTRY}/offline-rpms:latest bash -c "cp -r /rpms/* /export/ && chown -R $(id -u):$(id -g) /export"

docker run --rm -v $(pwd)/${OUTPUT_DIR}:/export ${REGISTRY}/offline-venv:latest bash -c "cp /artifacts/wheelhouse.tar.gz /export/ && if [ -f /artifacts/jars.tar.gz ]; then cp /artifacts/jars.tar.gz /export/; fi && cp /build/requirements.txt /export/ && cp -r /artifacts/poc_benchmarks /export/ && cp /artifacts/*.txt /export/ && chown -R $(id -u):$(id -g) /export"

cp 03_install_on_mapr.sh ${OUTPUT_DIR}/03_install_on_mapr.sh
chmod +x ${OUTPUT_DIR}/03_install_on_mapr.sh