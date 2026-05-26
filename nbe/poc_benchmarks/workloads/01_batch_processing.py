import os
from pyspark.sql import SparkSession
import duckdb
import time
from poc_benchmarks.base_workload import BaseWorkload

class BatchProcessingWorkload(BaseWorkload):
    def __init__(self):
        super().__init__("01_Batch_Processing_ACTB_HISTORY")
        self.spark = None
        self.duckdb_conn = None
        self.parquet_path = "/tmp/poc_data/actb_history.parquet"
        
        # In a real environment, these would come from env vars
        self.jdbc_url = os.environ.get("ORACLE_JDBC_URL", "jdbc:oracle:thin:@//localhost:1521/XEPDB1")
        self.db_user = os.environ.get("ORACLE_USER", "system")
        self.db_pass = os.environ.get("ORACLE_PASSWORD", "oracle")
        self.use_mock_data = os.environ.get("USE_MOCK_DATA", "true").lower() == "true"

    def setup(self):
        print("Initializing Spark Session...")
        
        # Discover jars
        jars_path = "./jars" if os.path.exists("./jars") else "/jars"
        jar_files = []
        if os.path.exists(jars_path):
            jar_files = [os.path.join(jars_path, f) for f in os.listdir(jars_path) if f.endswith(".jar")]
        jar_paths_str = ",".join(jar_files)
        
        builder = SparkSession.builder \
            .appName("NBE_POC_Batch") \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.sql.shuffle.partitions", "200")
            
        if jar_paths_str:
            builder = builder.config("spark.jars", jar_paths_str)
            
        self.spark = builder.getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")
        
        self.duckdb_conn = duckdb.connect()

    def run_workload(self):
        # 1. Spark Extraction Phase
        print("Phase 1: Spark Data Extraction (Oracle -> Parquet)")
        
        if self.use_mock_data:
            print("Using mock data generator for ACTB_HISTORY simulation...")
            # Simulate a large table (e.g., 10 million rows for local test)
            df = self.spark.range(0, 10000000).selectExpr(
                "id as txn_id", 
                "rand() * 10000 as amount", 
                "cast(rand() * 100 as int) as branch_cd",
                "current_date() as txn_date"
            )
        else:
            print(f"Connecting to Oracle: {self.jdbc_url}")
            df = self.spark.read.format("jdbc") \
                .option("url", self.jdbc_url) \
                .option("dbtable", "ACTB_HISTORY") \
                .option("user", self.db_user) \
                .option("password", self.db_pass) \
                .option("driver", "oracle.jdbc.driver.OracleDriver") \
                .option("fetchsize", "10000") \
                .load()
                
        # Write to Parquet to simulate EDF tiering
        print(f"Writing data to {self.parquet_path}...")
        df.write.mode("overwrite").parquet(self.parquet_path)
        
        self.rows_processed = df.count()
        print(f"Extraction complete. {self.rows_processed} rows written.")
        
        # 2. Analytics Phase (Spark)
        print("Phase 2: Analytical Queries (PySpark)")
        spark_start = time.time()
        spark_df = self.spark.read.parquet(self.parquet_path)
        
        # Complex aggregation: total amount per branch
        spark_result = spark_df.groupBy("branch_cd").sum("amount").orderBy("branch_cd").limit(10).collect()
        spark_time = time.time() - spark_start
        print(f"PySpark query completed in {spark_time:.2f} seconds.")
        
        # 3. Analytics Phase (DuckDB)
        print("Phase 3: Analytical Queries (DuckDB)")
        duckdb_start = time.time()
        # DuckDB queries the Parquet directly! Extremely fast.
        query = f"""
            SELECT branch_cd, SUM(amount) 
            FROM '{self.parquet_path}/*.parquet' 
            GROUP BY branch_cd 
            ORDER BY branch_cd 
            LIMIT 10
        """
        duckdb_result = self.duckdb_conn.execute(query).fetchall()
        duckdb_time = time.time() - duckdb_start
        print(f"DuckDB query completed in {duckdb_time:.2f} seconds.")
        
        # The metrics collector is capturing the overall resource usage during these phases.

    def cleanup(self):
        if self.spark:
            self.spark.stop()
        if self.duckdb_conn:
            self.duckdb_conn.close()

if __name__ == "__main__":
    workload = BatchProcessingWorkload()
    workload.execute()
