#!/bin/bash
set -e

echo "=== 1. Installing System RPMs ==="
sudo yum localinstall -y ./rpms/*.rpm

echo "=== 2. Extracting Python Wheels and Jars ==="
tar xzf wheelhouse.tar.gz
tar xzf jars.tar.gz

echo "=== 3. Setting up Python 3.8 Virtual Environment ==="
# MapR nodes have python3.8 after the RPM install
python3.8 -m venv /opt/nbe_venv
source /opt/nbe_venv/bin/activate

echo "=== 4. Installing Python Dependencies ==="
pip install --upgrade pip
pip install --no-index --find-links ./wheelhouse -r requirements.txt

echo "=========================================================="
echo "Setup Complete! Virtual environment is ready at /opt/nbe_venv"
echo "To run your Spark metrics script, execute:"
echo "source /opt/nbe_venv/bin/activate"
echo "python poc_metrics.py"
echo "=========================================================="