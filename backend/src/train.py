import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preprocess import split_and_prepare
from config import BEST_MODEL_PATH

def evaluate_model(model, X_test, y_test):
    # Predict classes and probabilities
    preds = model.predict(X_test)
    
    # If CatBoost or XGBoost outputs floats, convert to int binary
    preds = np.round(preds).astype(int)
    
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_test)[:, 1]
    else:
        probs = preds  # Fallback

    accuracy = accuracy_score(y_test, preds)
    precision = precision_score(y_test, preds, zero_division=0)
    recall = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    roc_auc = roc_auc_score(y_test, probs)

    return {
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "ROC-AUC": roc_auc
    }

def train_and_evaluate():
    print("Preparing dataset splits...")
    try:
        X_train, y_train, X_val, y_val, X_test, y_test = split_and_prepare()
    except Exception as e:
        print(f"Error preparing splits: {e}")
        raise e

    # Initialize candidate algorithms
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, eval_metric="logloss"),
        "LightGBM": LGBMClassifier(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, verbosity=-1),
        "CatBoost": CatBoostClassifier(iterations=150, depth=6, learning_rate=0.05, random_state=42, verbose=0)
    }

    results = []
    trained_models = {}

    print("\nTraining candidate models...")
    for name, model in models.items():
        print(f"Training {name}...")
        try:
            model.fit(X_train, y_train)
            trained_models[name] = model
            
            # Evaluate on Validation
            val_metrics = evaluate_model(model, X_val, y_val)
            # Evaluate on Test
            test_metrics = evaluate_model(model, X_test, y_test)
            
            results.append({
                "Model": name,
                "Val_Accuracy": val_metrics["Accuracy"],
                "Val_Precision": val_metrics["Precision"],
                "Val_Recall": val_metrics["Recall"],
                "Val_F1": val_metrics["F1-Score"],
                "Val_ROC-AUC": val_metrics["ROC-AUC"],
                "Test_Accuracy": test_metrics["Accuracy"],
                "Test_Precision": test_metrics["Precision"],
                "Test_Recall": test_metrics["Recall"],
                "Test_F1": test_metrics["F1-Score"],
                "Test_ROC-AUC": test_metrics["ROC-AUC"],
            })
        except Exception as e:
            print(f"Error training {name}: {e}")

    results_df = pd.DataFrame(results)
    
    print("\n" + "="*80)
    print("MODEL COMPARISON (VALIDATION SET)")
    print("="*80)
    val_cols = ["Model", "Val_Accuracy", "Val_Precision", "Val_Recall", "Val_F1", "Val_ROC-AUC"]
    print(results_df[val_cols].to_string(index=False))

    print("\n" + "="*80)
    print("MODEL COMPARISON (TEST SET)")
    print("="*80)
    test_cols = ["Model", "Test_Accuracy", "Test_Precision", "Test_Recall", "Test_F1", "Test_ROC-AUC"]
    print(results_df[test_cols].to_string(index=False))
    print("="*80 + "\n")

    # Select the best model based on Validation ROC-AUC
    best_idx = results_df["Val_ROC-AUC"].idxmax()
    best_model_name = results_df.loc[best_idx, "Model"]
    best_val_auc = results_df.loc[best_idx, "Val_ROC-AUC"]
    
    print(f"Best Model selected: {best_model_name} with Val ROC-AUC = {best_val_auc:.4f}")
    
    best_model = trained_models[best_model_name]
    
    # Save the trained model
    os.makedirs(os.path.dirname(BEST_MODEL_PATH), exist_ok=True)
    joblib.dump(best_model, BEST_MODEL_PATH)
    print(f"Saved best model to: {BEST_MODEL_PATH}")

if __name__ == "__main__":
    train_and_evaluate()
