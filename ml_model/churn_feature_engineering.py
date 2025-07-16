from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window, count
from pyspark.sql.types import StructType, StringType, IntegerType
import requests
import json

# Spark session
spark = SparkSession.builder \
    .appName("ChurnFeatureEngineering") \
    .config("spark.sql.streaming.statefulOperator.checkCorrectness.enabled", "false") \
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
POSTGRES_TABLE = "churn_predictions"

# JSON schema for Kafka messages
schema = StructType() \
    .add("user_id", IntegerType()) \
    .add("product_id", IntegerType()) \
    .add("event_type", StringType()) \
    .add("timestamp", StringType())

# Read from Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# Parse and convert timestamp
df_parsed = df_raw.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", to_timestamp("timestamp"))

# Aggregate views and adds per user every 10 minutes
df_ready = df_parsed \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(col("user_id"), window(col("timestamp"), "10 minutes")) \
    .pivot("event_type", ["view", "add_to_cart", "purchase"]) \
    .agg(count("*")) \
    .na.fill(0) \
    .withColumnRenamed("view", "num_views") \
    .withColumnRenamed("add_to_cart", "num_adds")

# Function to call FastAPI model and write prediction to PostgreSQL
def predict_and_write(batch_df, batch_id):
    print(f"\n🚀 Batch ID: {batch_id}")
    batch_df.show()

    if batch_df.count() == 0:
        print("⚠️ No data in batch")
        return

    # Collect and send to FastAPI
    records = batch_df.select("user_id", "num_views", "num_adds").collect()
    output = []

    for row in records:
        payload = {
            "num_views": int(row["num_views"]),
            "num_adds": int(row["num_adds"])
        }
        try:
            response = requests.post("http://localhost:8001/predict_churn", json=payload)
            churned = response.json().get("churned", False)
        except Exception as e:
            print(f"❌ FastAPI error for user {row['user_id']}: {e}")
            churned = False

        output.append((row["user_id"], payload["num_views"], payload["num_adds"], churned))

    # Convert to DataFrame and write to PostgreSQL
    result_df = spark.createDataFrame(output, ["user_id", "num_views", "num_adds", "churned"])

    try:
        result_df.write.jdbc(
            url=POSTGRES_URL,
            table=POSTGRES_TABLE,
            mode="append",
            properties=POSTGRES_PROPERTIES
        )
        print("✅ Written to churn_predictions table\n")
    except Exception as e:
        print("❌ PostgreSQL Error:", str(e), "\n")

# Start streaming
query = df_ready.writeStream \
    .foreachBatch(predict_and_write) \
    .outputMode("update") \
    .option("checkpointLocation", "/tmp/spark_checkpoints/churn_features") \
    .start()

query.awaitTermination()
