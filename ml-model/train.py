"""Train FraudShield models on Kaggle credit card fraud dataset."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ARTIFACTS = Path("ml-model/artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def evaluate(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_true, y_prob), 4),
    }


def main(data_path: str = "data/creditcard.csv") -> None:
    df = load_dataset(data_path)
    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=250, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "xgboost": XGBClassifier(
            n_estimators=250,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        ),
    }

    results = {}
    best_name = ""
    best_auc = -1.0

    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        prob = model.predict_proba(X_test_scaled)[:, 1]
        pred = (prob >= 0.5).astype(int)
        metrics = evaluate(y_test.values, pred, prob)
        results[name] = metrics

        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_name = name

    iso = IsolationForest(contamination=0.0017, random_state=42)
    iso.fit(X_train_scaled)
    anomaly = (iso.predict(X_test_scaled) == -1).astype(int)
    results["isolation_forest"] = evaluate(y_test.values, anomaly, anomaly)

    best_model = models[best_name]
    joblib.dump(best_model, ARTIFACTS / "fraud_model.joblib")
    joblib.dump(scaler, ARTIFACTS / "scaler.joblib")
    pd.DataFrame(results).T.to_csv(ARTIFACTS / "model_metrics.csv")

    print("Training complete. Best model:", best_name)
    print(pd.DataFrame(results).T)


if __name__ == "__main__":
    main()
