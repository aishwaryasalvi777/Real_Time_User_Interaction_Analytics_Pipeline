🛰️ Real-Time User Interaction Analytics Pipeline
This project simulates a real-time e-commerce environment where user interactions (like views, add-to-cart, and purchases) are streamed, aggregated, and analyzed to detect churn and visualize funnel trends using an end-to-end data pipeline.

🎯 Objective
Build a full-stack real-time analytics system that:

Ingests simulated user activity via Kafka.

Processes streams with Spark Structured Streaming.

Writes aggregates and predictions to PostgreSQL.

Predicts user churn in real time using a trained model.

Visualizes data with an interactive Streamlit dashboard.

📌 Key Features
✅ Kafka-based real-time event ingestion.

✅ Spark Streaming for session-level aggregation.

✅ Churn prediction using Logistic Regression.

✅ PostgreSQL for structured storage of KPIs and churn.

✅ Streamlit dashboard for real-time funnel and churn analysis.

✅ Modular & Dockerized for easy deployment.

🧱 Architecture
mermaid
Copy
Edit
flowchart TD
    A[Kafka Producer: Simulated Events] --> B[Spark Streaming]
    B --> C1[Funnel Aggregates → PostgreSQL]
    B --> C2[Churn Features → Logistic Regression Model]
    C2 --> C3[Churn Predictions → PostgreSQL]
    C1 & C3 --> D[Streamlit Dashboard]
📂 Project Structure
pgsql
Copy
Edit
realtime-user-analytics/
├── kafka_producer/
│   └── producer.py
├── spark_streaming/
│   ├── consumer.py
│   ├── aggregator.py
│   └── churn_feature_engineering.py
├── postgres_writer/
│   └── writer.py
├── ml_model/
│   ├── train_churn_model.py
│   ├── churn_model.pkl
│   └── fastapi_app.py
├── dashboard/
│   └── app.py
├── config/
│   ├── kafka_config.json
│   ├── spark_config.json
│   └── db_config.json
├── docker/
│   └── docker-compose.yml
├── requirements.txt
├── run_all.sh
└── README.md
⚙️ Tech Stack
Layer	Tech
Event Stream	Apache Kafka
Processing	Apache Spark Structured Streaming
Storage	PostgreSQL
Model	Scikit-learn Logistic Regression
Dashboard	Streamlit
Deployment	Docker, Docker Compose
API	FastAPI (for model deployment, optional)

🚀 How to Run
Pre-requisites: Docker, Python 3.10+, pip

1. Clone Repo
bash
Copy
Edit
git clone https://github.com/your-username/realtime-user-analytics.git
cd realtime-user-analytics
2. Start Docker Services
bash
Copy
Edit
docker-compose -f docker/docker-compose.yml up
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Train Churn Model
bash
Copy
Edit
python ml_model/train_churn_model.py
5. Run Kafka Producer
bash
Copy
Edit
python kafka_producer/producer.py
6. Start Spark Streaming Jobs
bash
Copy
Edit
python spark_streaming/consumer.py
python spark_streaming/aggregator.py
python spark_streaming/churn_feature_engineering.py
7. Launch Dashboard
bash
Copy
Edit
streamlit run dashboard/app.py
📊 Dashboard Features
Tab	Description
📈 Real-Time KPIs	View, Add-to-Cart, Purchase trends by time
🔄 Funnel Summary	Conversion funnel per session/user
⌛ User-Level Stats	Per-user event tracking
🛑 At-Risk Users	Real-time churn prediction using ML

Dashboard auto-refreshes every 10s.

🧠 Model Info: Churn Prediction
Features: num_views, num_adds_to_cart

Target: Session that ends without purchase → churn

Model: Logistic Regression (balanced, interpretable)

Format: Trained using train_churn_model.py, saved as churn_model.pkl

🧪 Testing the System
Kafka emits biased events: 60% views, 30% add-to-cart, 10% purchases.

PostgreSQL stores tables:

user_events_raw

funnel_summary

churn_predictions

🔍 Interview Soundbites
“Built an end-to-end real-time data pipeline using Kafka → Spark → PostgreSQL → Streamlit.”

“Predicted churn based on session-level features using a deployed Logistic Regression model.”

“Designed fully containerized environment with modular ETL + analytics pipeline.”

“Dashboard auto-refreshes to show live KPIs and churn insights for business stakeholders.”

📌 Future Improvements
Add user segmentation & cohort analysis.

Integrate email/SMS alerts for churned users.

Use PyTorch or XGBoost for better churn prediction.

Expose FastAPI endpoint for real-time scoring from external tools.

