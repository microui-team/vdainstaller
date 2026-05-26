import os
import time
import shutil
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from poc_benchmarks.base_workload import BaseWorkload

class RealTimeProcessingWorkload(BaseWorkload):
    def __init__(self):
        super().__init__("03_RealTime_Processing_ACTB_DAILY_LOG")
        self.spark = None
        self.mock_stream_dir = "/tmp/poc_data/actb_daily_log_stream"
        self.checkpoint_dir = "/tmp/poc_data/checkpoints/actb_daily_log"
        self.output_dir = "/tmp/poc_data/actb_daily_log_output"
        
        # In MapR, this would point to the MapR Streams or Kafka cluster
        self.kafka_bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.kafka_topic = os.environ.get("KAFKA_TOPIC", "actb_daily_log")
        self.use_mock_stream = os.environ.get("USE_MOCK_STREAM", "true").lower() == "true"

    def setup(self):
        print("Initializing Spark Structured Streaming...")
        
        jars_path = "./jars" if os.path.exists("./jars") else "/jars"
        jar_files = []
        if os.path.exists(jars_path):
            jar_files = [os.path.join(jars_path, f) for f in os.listdir(jars_path) if f.endswith(".jar")]
        jar_paths_str = ",".join(jar_files)
        
        builder = SparkSession.builder \
            .appName("NBE_POC_RealTime") \
            .config("spark.driver.memory", "2g")
            
        if jar_paths_str:
            builder = builder.config("spark.jars", jar_paths_str)
            
        self.spark = builder.getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Clean up previous runs for repeatable tests
        for d in [self.mock_stream_dir, self.checkpoint_dir, self.output_dir]:
            if os.path.exists(d):
                shutil.rmtree(d)
            os.makedirs(d)

    def run_workload(self):
        schema = StructType([
            StructField("log_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("amount", DoubleType(), True),
            StructField("timestamp", TimestampType(), True)
        ])

        if self.use_mock_stream:
            print(f"Phase 1: Setting up mock stream from directory: {self.mock_stream_dir}")
            
            # Start streaming read
            streaming_df = self.spark.readStream \
                .schema(schema) \
                .json(self.mock_stream_dir)
                
            print("Phase 2: Starting the stream writer...")
            # Start streaming write
            query = streaming_df.writeStream \
                .format("parquet") \
                .option("checkpointLocation", self.checkpoint_dir) \
                .option("path", self.output_dir) \
                .trigger(processingTime="2 seconds") \
                .start()
                
            # Simulate real-time data arriving
            print("Phase 3: Simulating data ingestion...")
            for i in range(5):
                batch_file = os.path.join(self.mock_stream_dir, f"batch_{i}.json")
                with open(batch_file, "w") as f:
                    f.write('{"log_id": "L1", "event_type": "TXN", "amount": 100.50, "timestamp": "2026-01-01T10:00:00Z"}\\n')
                    f.write('{"log_id": "L2", "event_type": "LOGIN", "amount": 0.0, "timestamp": "2026-01-01T10:00:01Z"}\\n')
                print(f"  -> Dropped micro-batch {i}")
                time.sleep(3)
                
            print("Stopping stream...")
            query.stop()
            self.rows_processed = 10 # 5 batches * 2 records
            
        else:
            print(f"Connecting to Kafka at {self.kafka_bootstrap}, topic: {self.kafka_topic}")
            # Placeholder for actual Kafka integration during the POC
            df = self.spark.readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap) \
                .option("subscribe", self.kafka_topic) \
                .load()
                
            # Usually we'd cast value to string and parse JSON here
            query = df.writeStream \
                .format("console") \
                .start()
                
            # Let it run for 30 seconds for benchmark profiling
            time.sleep(30)
            query.stop()

    def cleanup(self):
        if self.spark:
            self.spark.stop()

if __name__ == "__main__":
    workload = RealTimeProcessingWorkload()
    workload.execute()
