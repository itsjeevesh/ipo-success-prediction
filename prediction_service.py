from model_loader import model

def predict_ipo_success(text):

    probability = model.predict_proba([text])[0][1]

    prediction = "Successful IPO" if probability > 0.5 else "Unsuccessful IPO"

    return {
        "prediction": prediction,
        "probability": float(probability)
    }