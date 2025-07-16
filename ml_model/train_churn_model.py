# ml_model/train_churn_model.py

import pandas as pd
import psycopg2
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

# 📦 Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="postgres",
    user="postgres",
    password="pass1234"
)

# 📥 Step 1: Load raw user events
query = """
    SELECT user_id, event_type, timestamp
    FROM user_events_raw
    WHERE timestamp >= NOW() - INTERVAL '1 day';
"""
df = pd.read_sql(query, conn)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 📊 Step 2: Feature Engineering
# Group by user over 10-minute windows (session simulation)
session_features = []

for user_id, group in df.groupby("user_id"):
    group = group.sort_values("timestamp")
    session_start = group['timestamp'].min()
    session_end = session_start + pd.Timedelta(minutes=10)

    session_df = group[(group['timestamp'] >= session_start) & (group['timestamp'] <= session_end)]
    features = {
        'user_id': user_id,
        'num_views': (session_df['event_type'] == 'view').sum(),
        'num_adds': (session_df['event_type'] == 'add_to_cart').sum(),
        'num_purchases': (session_df['event_type'] == 'purchase').sum(),
    }
    features['churned'] = 1 if features['num_purchases'] == 0 else 0
    session_features.append(features)

features_df = pd.DataFrame(session_features)

# 🧹 Step 3: Prepare ML input
X = features_df[['num_views', 'num_adds']]
y = features_df['churned']

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🧠 Step 4: Train model pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression())
])
pipeline.fit(X_train, y_train)

# 🧪 Step 5: Evaluate
y_pred = pipeline.predict(X_test)
print("🧪 Classification Report:\n", classification_report(y_test, y_pred))

# 💾 Step 6: Save model
joblib.dump(pipeline, "ml_model/churn_model.pkl")
print("✅ Model saved to ml_model/churn_model.pkl")
