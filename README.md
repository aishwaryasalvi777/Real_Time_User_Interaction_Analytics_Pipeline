# 📊 Real-Time User Interaction Analytics Pipeline

This project builds a **real-time analytics system** that ingests simulated e-commerce user interaction events (e.g., view, add\_to\_cart, purchase), processes them using **Apache Kafka** and **Spark Structured Streaming**, stores summaries in **PostgreSQL**, applies a **churn prediction ML model**, and visualizes insights on a **Streamlit dashboard**.

---

## ✅ Objective

To design and deploy a real-time data pipeline that:

* Simulates user behavior on an e-commerce platform.
* Aggregates event data for funnel analysis.
* Predicts churn using a trained ML model in real time.
* Displays key KPIs and churn alerts on a live dashboard.

---

## ⚙️ Project Architecture

```text
Kafka Producer → Spark Streaming Jobs → PostgreSQL → ML Model (FastAPI) → Streamlit Dashboard
```

### Modules Breakdown

1. **Kafka Producer**:

   * Emits user events to the `user_events` topic with a biased distribution:

     * 60% `view`, 30% `add_to_cart`, 10% `purchase`.
   * Events include: `user_id`, `event_type`, `timestamp`, `session_id`.

2. **Spark Streaming Layer**:

   * `consumer.py`: Reads Kafka stream, writes raw events to PostgreSQL.
   * `aggregator.py`: Aggregates event counts per user in 10-minute windows, stores in `funnel_summary`.
   * `churn_feature_engineering.py`:

     * Consumes `funnel_summary`, creates features.
     * Calls **FastAPI churn model** and writes predictions to `churn_prediction` table.
     * Includes proper watermarking and windowing logic.

3. **Churn Prediction Model**:

   * Trained using historical funnel summaries.
   * Features: `num_views`, `num_add_to_cart`, `num_purchases`, conversion ratios.
   * Deployed as a **FastAPI** REST endpoint.
   * Accepts JSON feature input and returns `churned: true/false`.

4. **PostgreSQL**:

   * Tables: `raw_events`, `funnel_summary`, `churn_prediction`.
   * Stores both raw and processed data.

5. **Streamlit Dashboard**:

   * Shows real-time KPIs: event trend graphs, funnel metrics, churn prediction summary.
   * Auto-refreshes every 15 seconds using `st.experimental_rerun()`.

---

## 🐳 Dockerized Setup

All services (Kafka, Zookeeper, PostgreSQL, Spark, FastAPI, Streamlit) are containerized using **Docker Compose**.

```bash
# Start all services
bash run_all.sh
```

---

## 📁 Folder Structure

```bash
realtime-user-analytics/
│
├── kafka_producer/
│   └── producer.py
│
├── spark_streaming/
│   ├── consumer.py
│   ├── aggregator.py
│   └── churn_feature_engineering.py
│
├── postgres_writer/
│   └── db_writer.py
│
├── ml_model/
│   ├── train_churn_model.py
│   └── fastapi_app.py
│
├── dashboard/
│   └── app.py
│
├── config/
│   ├── kafka_config.json
│   ├── spark_config.json
│   └── db_config.json
│
├── docker/
│   └── docker-compose.yml
│
├── run_all.sh
└── README.md
```

---

## 🧠 Key Learnings and Issues Solved

| Phase           | Challenges Faced                     | Solution                                                          |
| --------------- | ------------------------------------ | ----------------------------------------------------------------- |
| Kafka Producer  | Biased event generation logic        | Used weighted random logic with `random.choices()`                |
| Spark Streaming | Watermark correctness errors         | Tuned watermark + window duration and avoided out-of-order events |
| PostgreSQL      | Batch inserts from Spark             | Used JDBC sink and partitioned writing                            |
| ML Prediction   | Model deployment + real-time scoring | Used FastAPI for fast JSON API scoring                            |
| Dashboard       | Live refresh of churn table          | Used `st.experimental_rerun()` + polling PostgreSQL               |

---

## ✅ Deliverables

* `producer.py`: Kafka event simulator
* Spark jobs: `consumer.py`, `aggregator.py`, `churn_feature_engineering.py`
* Trained `churn_model.pkl` and `fastapi_app.py` service
* Streamlit dashboard at `localhost:8501`
* Dockerized stack with single launch script `run_all.sh`

---

## 📍How to Run

```bash
# 1. Launch the pipeline
bash run_all.sh

# 2. Monitor Streamlit dashboard
http://localhost:8501

# 3. Test FastAPI (optional)
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"num_views":5,"num_add_to_cart":2,"num_purchases":0}'
```
