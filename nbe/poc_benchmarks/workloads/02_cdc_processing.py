import os
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
from poc_benchmarks.base_workload import BaseWorkload

class CDCProcessingWorkload(BaseWorkload):
    def __init__(self):
        super().__init__("02_CDC_Processing_STTM_CUST_ACCOUNT")
        self.spark = None
        self.target_delta_path = "/tmp/poc_data/sttm_cust_account_delta"
        self.use_mock_data = os.environ.get("USE_MOCK_DATA", "true").lower() == "true"

    def setup(self):
        print("Initializing Spark Session with Delta Lake support...")
        
        jars_path = "./jars" if os.path.exists("./jars") else "/jars"
        jar_files = []
        if os.path.exists(jars_path):
            jar_files = [os.path.join(jars_path, f) for f in os.listdir(jars_path) if f.endswith(".jar")]
        jar_paths_str = ",".join(jar_files)
        
        # Delta Lake requires specific configurations
        builder = SparkSession.builder \
            .appName("NBE_POC_CDC") \
            .config("spark.driver.memory", "4g") \
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            
        if jar_paths_str:
            builder = builder.config("spark.jars", jar_paths_str)
            
        self.spark = builder.getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")

    def run_workload(self):
        print("Phase 1: Generating Base Historical Table (H_STTM_CUST_ACCOUNT)")
        
        # 1. Create a large base table
        num_base_records = 5000000 if self.use_mock_data else 100000
        base_df = self.spark.range(0, num_base_records).selectExpr(
            "id as account_id",
            "cast(rand() * 100000 as decimal(18,2)) as balance",
            "'ACTIVE' as status",
            "current_timestamp() as last_updated"
        )
        
        print(f"Writing {num_base_records} records to Delta Lake at {self.target_delta_path}...")
        base_df.write.format("delta").mode("overwrite").save(self.target_delta_path)
        
        print("Phase 2: Processing CDC Updates (STTM_CUST_ACCOUNT changes)")
        
        # 2. Simulate incoming CDC data (10% updates, some new inserts)
        num_cdc_records = num_base_records // 10
        cdc_df = self.spark.range(0, num_cdc_records).selectExpr(
            "id as account_id",
            "cast(rand() * 100000 as decimal(18,2)) as balance",
            "CASE WHEN id % 2 == 0 THEN 'CLOSED' ELSE 'ACTIVE' END as status",
            "current_timestamp() as last_updated"
        )
        
        # Create a view for the SQL Merge
        cdc_df.createOrReplaceTempView("cdc_updates")
        
        # 3. Perform the Delta Lake MERGE
        print(f"Applying MERGE INTO operation with {num_cdc_records} records...")
        merge_start = time.time()
        
        from delta.tables import DeltaTable
        
        try:
            delta_table = DeltaTable.forPath(self.spark, self.target_delta_path)
            
            delta_table.alias("target").merge(
                cdc_df.alias("updates"),
                "target.account_id = updates.account_id"
            ) \
            .whenMatchedUpdate(set = {
                "balance": "updates.balance",
                "status": "updates.status",
                "last_updated": "updates.last_updated"
            }) \
            .whenNotMatchedInsert(values = {
                "account_id": "updates.account_id",
                "balance": "updates.balance",
                "status": "updates.status",
                "last_updated": "updates.last_updated"
            }) \
            .execute()
            
            merge_time = time.time() - merge_start
            self.rows_processed = num_cdc_records
            print(f"MERGE completed successfully in {merge_time:.2f} seconds.")
            
        except Exception as e:
            print(f"Delta Merge failed (ensure delta-core jar is present): {e}")
            raise

    def cleanup(self):
        if self.spark:
            self.spark.stop()

if __name__ == "__main__":
    workload = CDCProcessingWorkload()
    workload.execute()
