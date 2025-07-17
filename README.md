Real-Time User Interaction Analytics Pipeline

🧠 Objective:

Build a real-time data pipeline to simulate, stream, process, store, and visualize user behavior events (views, cart additions, purchases) from an e-commerce platform. The goal is to enable funnel analysis, churn prediction, and live KPIs to support marketing and product decisions.

⚙️ Architecture Overview:

Tech Stack: Kafka, Spark Structured Streaming, PostgreSQL, FastAPI, Streamlit, Docker Compose

+-------------+        +----------------+         +----------------+         +-------------------+        +-------------+
| Kafka       | -----> | Spark Consumer | ----->  | Spark Aggregator| -----> | PostgreSQL        | -----> | Streamlit   |
| Producer    |        | (Raw Events)   |         | (Funnel Counts)|         | (Event DB + KPIs) |        | Dashboard   |
+-------------+        +----------------+         +----------------+         +-------------------+        +-------------+
                                                                       \
                                                                        \-> FastAPI (Churn Model Serving)

📦 Project Structure

realtime-user-analytics/
├── kafka_producer/           # Simulates real-time user behavior
│   └── producer.py
│
├── spark_streaming/          # Real-time data processing using Spark
│   ├── consumer.py
│   ├── aggregator.py         # Performs windowed aggregations for funnel KPIs
│   └── churn_feature_engineering.py  # Generates churn features & writes to PostgreSQL
│
├── postgres_writer/          # Writes aggregated outputs to PostgreSQL
│   └── writer.py
│
├── ml_model/                 # Churn model + API
│   ├── train_churn_model.py
│   ├── fastapi_app.py
│   └── churn_model.pkl
│
├── dashboard/                # Streamlit dashboard
│   └── app.py
│
├── config/                   # Configs for Kafka, Spark, and DB
│
├── docker/                   # Docker Compose for Kafka, PostgreSQL, Spark
│   └── docker-compose.yml
│
├── requirements.txt
├── run_all.sh                # Convenience script to launch the pipeline
└── README.md

🔄 Phase-by-Phase Breakdown

✅ Phase 1: Kafka Producer Setup

Implemented producer.py to emit synthetic user events (view, add_to_cart, purchase) with realistic bias.

Ensured timestamp is included for proper event-time tracking.

Topics sent to Kafka: user_events

✅ Phase 2: Spark Consumer and Aggregator

consumer.py reads Kafka messages and writes raw events to PostgreSQL (raw_events table).

aggregator.py performs 10-minute tumbling window aggregations with watermarking.

Results stored in funnel_summary for dashboard usage.

✅ Phase 3: Feature Engineering for Churn

Created churn_feature_engineering.py to read events and build churn-related features like:

Total view/add_to_cart/purchase events per user

Time since last interaction

Spark watermarking used with correctness-safe logic to avoid late event issues.

Writes features into churn_features table in PostgreSQL.

✅ Phase 4: Churn Prediction Model

Built model using logistic regression in train_churn_model.py.

Trained on aggregated behavioral data.

Model saved as churn_model.pkl.

fastapi_app.py exposes /predict endpoint to serve real-time churn predictions.

✅ Phase 5: Real-Time Dashboard

Streamlit dashboard in dashboard/app.py:

Funnel KPIs (view → cart → purchase)

Live churn predictions (churned / not churned users)

Auto-refresh for real-time visibility

✅ Deliverables:

Real-time Kafka → Spark → PostgreSQL → Dashboard pipeline

Docker Compose setup for reproducibility

Trained churn prediction model & live prediction API

Interactive Streamlit dashboard

🧪 How to Run

Start the full pipeline:

bash run_all.sh

Open the Streamlit dashboard:

http://localhost:8501

Trigger churn predictions (optional):

Exposed via FastAPI

curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"user_id": "user_123"}'

🚀 Key Highlights for Interviews

Spark Structured Streaming: windowed aggregations + watermarking for correctness

Model Deployment: FastAPI + real-time inference

Kafka and PostgreSQL integration

Streamlit dashboard for live KPI tracking

End-to-end Dockerized pipeline

✅ Project Complete — Real-Time Behavioral Analytics & Churn Model

