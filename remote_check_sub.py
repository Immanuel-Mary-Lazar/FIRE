import pandas as pd

DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"
sub = pd.read_csv(f"{DATA_DIR}/sample_submission.csv")
print("Sub shape:", sub.shape)
print("Sub head:")
print(sub.head(3))
print("Sub tail:")
print(sub.tail(3))
print("Is ID range(len):", (sub["ID"].values == list(range(len(sub)))).all())

