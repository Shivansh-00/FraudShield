from pathlib import Path
import joblib
import pandas as pd
import shap


def run_explain(sample_path: str = "data/creditcard.csv") -> None:
    model = joblib.load("ml-model/artifacts/fraud_model.joblib")
    scaler = joblib.load("ml-model/artifacts/scaler.joblib")
    df = pd.read_csv(sample_path).drop(columns=["Class"]).head(200)
    scaled = scaler.transform(df)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(scaled)

    output = Path("ml-model/artifacts")
    output.mkdir(parents=True, exist_ok=True)
    importance = pd.DataFrame(
        {"feature": df.columns, "importance": abs(shap_values).mean(axis=0)}
    ).sort_values("importance", ascending=False)
    importance.to_csv(output / "shap_importance.csv", index=False)
    print("Saved SHAP importance report")


if __name__ == "__main__":
    run_explain()
