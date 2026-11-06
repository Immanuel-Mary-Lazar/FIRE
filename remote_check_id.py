import pandas as pd

DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"
test = pd.read_csv(f"{DATA_DIR}/test.csv", nrows=5)
sub = pd.read_csv(f"{DATA_DIR}/sample_submission.csv", nrows=5)

print("Test columns:", list(test.columns)[:10])
print("'ID' in test.columns:", 'ID' in test.columns)
print("Sub head:")
print(sub)

