import psutil
import time
import threading
import json
import os
from datetime import datetime

class MetricsCollector:
    def __init__(self, interval_sec=1.0):
        self.interval_sec = interval_sec
        self.is_running = False
        self.thread = None
        self.metrics_log = []
        self.start_time = None
        self.end_time = None
        
        # To calculate IO accurately, we get baseline counters
        self.baseline_disk = psutil.disk_io_counters()
        self.baseline_net = psutil.net_io_counters()

    def _collect(self):
        process = psutil.Process(os.getpid())
        while self.is_running:
            try:
                mem_info = process.memory_info()
                sample = {
                    "timestamp": datetime.now().isoformat(),
                    "process_cpu_percent": process.cpu_percent(interval=None),
                    "process_memory_rss_mb": mem_info.rss / (1024 * 1024),
                    "process_memory_vms_mb": mem_info.vms / (1024 * 1024),
                    "system_cpu_percent": psutil.cpu_percent(interval=None),
                    "system_memory_percent": psutil.virtual_memory().percent
                }
                self.metrics_log.append(sample)
                time.sleep(self.interval_sec)
            except Exception as e:
                # If process ends or errors occur, stop logging
                break

    def start(self):
        self.start_time = time.time()
        self.is_running = True
        
        # Reset counters
        self.baseline_disk = psutil.disk_io_counters()
        self.baseline_net = psutil.net_io_counters()
        self.metrics_log = []
        
        # Init cpu_percent so next calls are non-blocking and accurate
        psutil.cpu_percent(interval=None)
        psutil.Process(os.getpid()).cpu_percent(interval=None)
        
        self.thread = threading.Thread(target=self._collect)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.end_time = time.time()
        if self.thread:
            self.thread.join()

    def generate_report(self, workload_name, rows_processed=None):
        duration = self.end_time - self.start_time if self.end_time else 0
        
        final_disk = psutil.disk_io_counters()
        final_net = psutil.net_io_counters()
        
        disk_read_mb = (final_disk.read_bytes - self.baseline_disk.read_bytes) / (1024*1024) if final_disk and self.baseline_disk else 0
        disk_write_mb = (final_disk.write_bytes - self.baseline_disk.write_bytes) / (1024*1024) if final_disk and self.baseline_disk else 0
        
        net_recv_mb = (final_net.bytes_recv - self.baseline_net.bytes_recv) / (1024*1024) if final_net and self.baseline_net else 0
        net_sent_mb = (final_net.bytes_sent - self.baseline_net.bytes_sent) / (1024*1024) if final_net and self.baseline_net else 0

        # Aggregations
        if self.metrics_log:
            avg_sys_cpu = sum(m["system_cpu_percent"] for m in self.metrics_log) / len(self.metrics_log)
            max_sys_cpu = max(m["system_cpu_percent"] for m in self.metrics_log)
            avg_proc_cpu = sum(m["process_cpu_percent"] for m in self.metrics_log) / len(self.metrics_log)
            max_proc_rss = max(m["process_memory_rss_mb"] for m in self.metrics_log)
        else:
            avg_sys_cpu = max_sys_cpu = avg_proc_cpu = max_proc_rss = 0.0

        throughput = (rows_processed / duration) if (rows_processed and duration > 0) else 0

        report = {
            "workload_name": workload_name,
            "duration_seconds": round(duration, 2),
            "rows_processed": rows_processed,
            "throughput_rows_per_sec": round(throughput, 2),
            "avg_system_cpu_percent": round(avg_sys_cpu, 2),
            "max_system_cpu_percent": round(max_sys_cpu, 2),
            "avg_process_cpu_percent": round(avg_proc_cpu, 2),
            "max_process_memory_rss_mb": round(max_proc_rss, 2),
            "total_disk_read_mb": round(disk_read_mb, 2),
            "total_disk_write_mb": round(disk_write_mb, 2),
            "total_network_recv_mb": round(net_recv_mb, 2),
            "total_network_sent_mb": round(net_sent_mb, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        return report

    def save_report(self, workload_name, report_dir="poc_reports", rows_processed=None):
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        report = self.generate_report(workload_name, rows_processed)
        filename = f"{report_dir}/{workload_name}_{int(time.time())}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
            
        print(f"\n{'='*60}")
        print(f"   POC METRICS REPORT: {workload_name}")
        print(f"{'='*60}")
        print(f" {('Execution Time'):<25} | {report['duration_seconds']:>15} s")
        print(f" {('Rows Processed'):<25} | {report['rows_processed'] if report['rows_processed'] else 'N/A':>15}")
        print(f" {('Throughput (Rows/sec)'):<25} | {report['throughput_rows_per_sec']:>15,.0f}")
        print(f"{'-'*60}")
        print(f" {('Max System CPU'):<25} | {report['max_system_cpu_percent']:>15}%")
        print(f" {('Avg Process CPU'):<25} | {report['avg_process_cpu_percent']:>15}%")
        print(f" {('Peak Memory (RSS)'):<25} | {report['max_process_memory_rss_mb']:>15} MB")
        print(f"{'-'*60}")
        print(f" {('Disk Read'):<25} | {report['total_disk_read_mb']:>15} MB")
        print(f" {('Disk Write'):<25} | {report['total_disk_write_mb']:>15} MB")
        print(f"{'='*60}\n")
        print(f"Report saved to {filename}")
        
        return report
