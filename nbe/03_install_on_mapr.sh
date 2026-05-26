#!/bin/bash
set -e

echo "=== 1. Installing System RPMs ==="
rm -f ./rpms/*.i686.rpm
rm -f ./rpms/tesseract-langpack-eng*.rpm

sudo yum localinstall -y --allowerasing ./rpms/*.rpm

echo "=== 2. Extracting Python Wheels and Jars ==="
tar xzf wheelhouse.tar.gz
tar xzf jars.tar.gz

echo "=== 3. Setting up Python 3.8 Virtual Environment ==="
python3.8 -m venv /opt/nbe_venv
source /opt/nbe_venv/bin/activate

echo "=== 4. Installing Python Dependencies ==="
pip install --upgrade pip
pip install --no-index --find-links ./wheelhouse -r requirements.txt
