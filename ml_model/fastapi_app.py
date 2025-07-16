from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

# 🚀 FastAPI app
app = FastAPI(title="Churn Prediction API")

# 📦 Request schema
class ChurnFeatures(BaseModel):
    num_views: int
    num_adds: int

# 🔍 Prediction endpoint
@app.post("/predict_churn")
def predict_churn(features: ChurnFeatures):
    # 🧾 Log incoming request
    print("🔍 Received request:", features.dict())

    # 🔁 Replace this with model prediction when ready
    # X = np.array([[features.num_views, features.num_adds]])
    # y_pred = model.predict(X)[0]

    # ✅ Temporary rule-based logic for testing
    num_views = features.num_views
    num_adds = features.num_adds

    # 🎯 Relaxed threshold for forced churn=True for some rows
    churned = (num_views < 5 and num_adds < 2)

    return {
        "churned": churned,
        "input": features.dict()
    }
