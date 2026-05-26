#!/bin/bash
# =========================================================
# Master script to execute all POC Benchmarking Workloads
# =========================================================

set -e

echo "========================================================="
echo "   NBE Big Data POC - Automated Benchmarking Suite       "
echo "========================================================="
echo ""

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Ensure reports directory exists
mkdir -p poc_reports

echo "[1/4] Running Batch Processing Workload (Oracle -> Parquet -> DuckDB)"
python poc_benchmarks/workloads/01_batch_processing.py

echo "[2/4] Running CDC Processing Workload (Delta Lake MERGE)"
python poc_benchmarks/workloads/02_cdc_processing.py

echo "[3/4] Running Real-Time Processing Workload (PySpark Structured Streaming)"
python poc_benchmarks/workloads/03_realtime_processing.py

echo "[4/6] Running XML Processing Workload"
python poc_benchmarks/workloads/04_xml_processing.py

echo "[5/6] Running Unstructured Data Workload (PDF, OCR, Arabic)"
python poc_benchmarks/workloads/05_unstructured_data_processing.py

echo "[6/6] Running HTML Scraping Workload"
python poc_benchmarks/workloads/06_html_scraping.py

echo ""
echo "[7/7] Generating HTML Dashboard..."
python poc_benchmarks/generate_html_report.py

echo ""
echo "========================================================="
echo "   POC Suite Completed Successfully!                     "
echo "   View JSON reports in ./poc_reports/                   "
echo "   Open poc_metrics_dashboard.html in a browser!         "
echo "========================================================="
