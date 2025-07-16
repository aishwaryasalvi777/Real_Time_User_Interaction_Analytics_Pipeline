# consumer.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, StringType, IntegerType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaToPostgresRawConsumer") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Kafka config
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "user_events"

# PostgreSQL config
POSTGRES_URL = "jdbc:postgresql://localhost:5432/postgres"
POSTGRES_PROPERTIES = {
    "user": "postgres",
    "password": "pass1234",
    "driver": "org.postgresql.Driver"
}
POSTGRES_TABLE = "user_events_raw"

# Correct schema matching your producer
schema = StructType() \
    .add("user_id", IntegerType()) \
    .add("product_id", IntegerType()) \
    .add("event_type", StringType()) \
    .add("timestamp", StringType())  # Match 'timestamp' field in producer

# Read from Kafka
print("📡 Starting Kafka read...")
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# Parse and convert timestamp
df_parsed = df_raw.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp"))  # Convert ISO string to timestamp

# Write each micro-batch to PostgreSQL
def write_to_postgres(batch_df, batch_id):
    print(f"\n🚀 Batch ID: {batch_id}, Count: {batch_df.count()}")
    batch_df.show(truncate=False)
    try:
        batch_df.write.jdbc(
            url=POSTGRES_URL,
            table=POSTGRES_TABLE,
            mode="append",
            properties=POSTGRES_PROPERTIES
        )
        print("✅ Written to PostgreSQL\n")
    except Exception as e:
        print("❌ PostgreSQL Error:", str(e), "\n")

# Start streaming
query = df_parsed.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/spark_checkpoints/user_events_raw") \
    .start()

query.awaitTermination()
