from abc import ABC, abstractmethod
from poc_benchmarks.metrics import MetricsCollector
import traceback

class BaseWorkload(ABC):
    def __init__(self, name):
        self.name = name
        self.metrics = MetricsCollector(interval_sec=1.0)
        self.rows_processed = 0

    def setup(self):
        """Override to setup database connections, spark sessions, etc. (Not benchmarked)"""
        pass

    @abstractmethod
    def run_workload(self):
        """Override to implement the actual workload to benchmark."""
        pass

    def cleanup(self):
        """Override to close connections, spark sessions, etc."""
        pass

    def execute(self):
        print(f"\\n{'='*50}")
        print(f"Setting up workload: {self.name}")
        self.setup()
        
        print(f"Starting benchmark for: {self.name}")
        self.metrics.start()
        
        try:
            self.run_workload()
        except Exception as e:
            print(f"Workload {self.name} failed: {e}")
            traceback.print_exc()
        finally:
            self.metrics.stop()
            self.cleanup()
            
            self.metrics.save_report(self.name, rows_processed=self.rows_processed)
            print(f"{'='*50}\\n")
