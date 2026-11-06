import pandas as pd
import numpy as np

DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"
train = pd.read_csv(f"{DATA_DIR}/train.csv", nrows=1000)

cat_cols = []
num_cols = []
date_cols = []

for c in train.columns:
    if c in ['space_id', 'price_tier']:
        continue
    if 'date' in c:
        date_cols.append(c)
    elif train[c].dtype == 'object':
        cat_cols.append(c)
    else:
        num_cols.append(c)

print(f"Num cols ({len(num_cols)}):", num_cols[:10])
print(f"Cat cols ({len(cat_cols)}):", cat_cols)
print(f"Date cols ({len(date_cols)}):", date_cols)

