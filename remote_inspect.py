import pandas as pd
import numpy as np

DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"
train = pd.read_csv(f"{DATA_DIR}/train.csv")
test = pd.read_csv(f"{DATA_DIR}/test.csv")
sub = pd.read_csv(f"{DATA_DIR}/sample_submission.csv")

print("Train shape:", train.shape)
print("Test shape:", test.shape)
print("Sample sub shape:", sub.shape)

print("\nTrain columns and dtypes:")
print(train.dtypes)

print("\nSample submission head:")
print(sub.head())

target_col = [c for c in train.columns if c not in test.columns]
print("\nTarget column(s):", target_col)
if target_col:
    print("\nTarget distribution:")
    print(train[target_col[0]].value_counts(dropna=False))

