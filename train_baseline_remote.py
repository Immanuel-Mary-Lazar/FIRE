import time
import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report

start_time = time.time()
DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"

print("1. Loading train, test, and sample submission...")
train = pd.read_csv(f"{DATA_DIR}/train.csv")
test = pd.read_csv(f"{DATA_DIR}/test.csv")
sub = pd.read_csv(f"{DATA_DIR}/sample_submission.csv")

print(f"Train: {train.shape}, Test: {test.shape}, Sub: {sub.shape}")

# Target: price_tier in {1, 2, 3, 4} -> map to 0, 1, 2, 3
y = train["price_tier"].values - 1

# Identify column types
drop_cols = ["space_id", "price_tier"]
date_cols = [c for c in train.columns if "date" in c]

features = [c for c in train.columns if c not in drop_cols]
cat_cols = [c for c in features if train[c].dtype == "object" and c not in date_cols]
num_cols = [c for c in features if c not in cat_cols and c not in date_cols]

print(f"Features: {len(features)} (Cat: {len(cat_cols)}, Num: {len(num_cols)}, Date: {len(date_cols)})")

# Preprocessing: convert categories to category dtype and parse basic date features
print("2. Preprocessing features...")
for df in [train, test]:
    # Extract year/month/day from date columns
    for dc in date_cols:
        dt = pd.to_datetime(df[dc], errors="coerce")
        df[f"{dc}_year"] = dt.dt.year
        df[f"{dc}_month"] = dt.dt.month
        df[f"{dc}_day"] = dt.dt.day
    
    # Categoricals
    for cc in cat_cols:
        df[cc] = df[cc].astype(str).fillna("MISSING").astype("category")

all_date_feats = [f"{dc}_{s}" for dc in date_cols for s in ["year", "month", "day"]]
used_features = num_cols + cat_cols + all_date_feats
print(f"Total used features: {len(used_features)}")

X = train[used_features]
X_test = test[used_features]

# 5-Fold Stratified CV
print("3. Training 5-Fold LightGBM Baseline...")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

oof_preds_proba = np.zeros((len(train), 4), dtype=np.float32)
test_preds_proba = np.zeros((len(test), 4), dtype=np.float32)

params = {
    "objective": "multiclass",
    "num_class": 4,
    "metric": "multi_logloss",
    "boosting_type": "gbdt",
    "learning_rate": 0.1,
    "num_leaves": 63,
    "max_depth": -1,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "n_jobs": -1,
    "random_state": 42,
    "verbose": -1,
}

for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    print(f"\n--- Fold {fold + 1} / 5 ---")
    X_tr, y_tr = X.iloc[train_idx], y[train_idx]
    X_va, y_val = X.iloc[val_idx], y[val_idx]
    
    trn_data = lgb.Dataset(X_tr, label=y_tr, categorical_feature=cat_cols, free_raw_data=False)
    val_data = lgb.Dataset(X_va, label=y_val, reference=trn_data, categorical_feature=cat_cols, free_raw_data=False)
    
    model = lgb.train(
        params,
        trn_data,
        num_boost_round=500,
        valid_sets=[trn_data, val_data],
        callbacks=[
            lgb.early_stopping(stopping_rounds=30, verbose=False),
            lgb.log_evaluation(period=100)
        ]
    )
    
    val_probs = model.predict(X_va, num_iteration=model.best_iteration)
    oof_preds_proba[val_idx] = val_probs
    
    val_preds_cls = np.argmax(val_probs, axis=1)
    acc = accuracy_score(y_val, val_preds_cls)
    f1_m = f1_score(y_val, val_preds_cls, average="macro")
    print(f"Fold {fold + 1} Best Iteration: {model.best_iteration} | Accuracy: {acc:.4f} | Macro F1: {f1_m:.4f}")
    
    test_probs = model.predict(X_test, num_iteration=model.best_iteration)
    test_preds_proba += test_probs / 5.0

# Overall OOF metrics
oof_classes = np.argmax(oof_preds_proba, axis=1)
overall_acc = accuracy_score(y, oof_classes)
overall_f1 = f1_score(y, oof_classes, average="macro")

print("\n" + "=" * 50)
print(f"Overall OOF Accuracy : {overall_acc:.4f}")
print(f"Overall OOF Macro F1 : {overall_f1:.4f}")
print("=" * 50)
print("\nClassification Report (OOF):")
print(classification_report(y + 1, oof_classes + 1, digits=4))

# Prepare submission
test_pred_classes = np.argmax(test_preds_proba, axis=1) + 1
sub["price_tier"] = test_pred_classes

out_path = "/kaggle/working/submission.csv"
sub.to_csv(out_path, index=False)
print(f"\nSaved submission to {out_path}!")
print("Submission Head:")
print(sub.head(10))
print("\nPredicted Class Distribution:")
print(sub["price_tier"].value_counts().sort_index())
print(f"Total time: {time.time() - start_time:.1f}s")

