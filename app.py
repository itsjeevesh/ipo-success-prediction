from fastapi import FastAPI
from pydantic import BaseModel
from lime.lime_text import LimeTextExplainer
from model_loader import model

from prediction_service import predict_ipo_success

app = FastAPI(title="IPO Success Prediction API")


class PredictionRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/predict")
def predict(request: PredictionRequest):

    result = predict_ipo_success(request.text)

    return result

explainer = LimeTextExplainer(class_names=["Unsuccessful", "Successful"])

@app.post("/explain")
def explain(request: PredictionRequest):

    text = request.text

    exp = explainer.explain_instance(
        text,
        model.predict_proba,
        num_features=10
    )

    return {
        "explanation": exp.as_list()
    }

@app.get("/")
def home():
    return {"message": "IPO Success Prediction API is running"}