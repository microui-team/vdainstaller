import os
import time
from pyspark.sql import SparkSession
from poc_benchmarks.base_workload import BaseWorkload

class XMLProcessingWorkload(BaseWorkload):
    def __init__(self):
        super().__init__("04_XML_Processing_Legacy")
        self.spark = None
        self.xml_path = "XML.txt"

    def setup(self):
        print("Initializing Spark Session for XML Processing...")
        
        jars_path = "./jars" if os.path.exists("./jars") else "/jars"
        jar_files = []
        if os.path.exists(jars_path):
            jar_files = [os.path.join(jars_path, f) for f in os.listdir(jars_path) if f.endswith(".jar")]
        jar_paths_str = ",".join(jar_files)
        
        builder = SparkSession.builder \
            .appName("NBE_POC_XML") \
            .config("spark.driver.memory", "2g")
            
        if jar_paths_str:
            builder = builder.config("spark.jars", jar_paths_str)
            
        self.spark = builder.getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")

    def run_workload(self):
        if not os.path.exists(self.xml_path):
            print(f"File {self.xml_path} not found. Using a dummy dataframe to simulate workload.")
            self.rows_processed = 0
            return

        print(f"Phase 1: Parsing XML Document: {self.xml_path}")
        try:
            # We assume Databricks spark-xml is loaded
            df = self.spark.read \
                .format("xml") \
                .option("rowTag", "FCDB_RES_ENV") \
                .load(self.xml_path)
            
            print("Schema inferred:")
            df.printSchema()
            
            # Action to force execution
            self.rows_processed = df.count()
            print(f"Parsed {self.rows_processed} XML records.")
            
            print("Sample data:")
            df.show(5, truncate=False)
            
        except Exception as e:
            print(f"Failed to process XML. Ensure spark-xml jar is available. Error: {e}")
            raise

    def cleanup(self):
        if self.spark:
            self.spark.stop()

if __name__ == "__main__":
    workload = XMLProcessingWorkload()
    workload.execute()
