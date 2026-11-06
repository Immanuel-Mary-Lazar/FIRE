import pandas as pd
from sklearn.dummy import DummyClassifier

DATA_DIR = "/kaggle/input/competitions/workstation-rental-price-tier-prediction/kaggle_ready_dataset"

print("Loading train and test datasets...")
train = pd.read_csv(f"{DATA_DIR}/train.csv", usecols=["space_id", "price_tier"])
test = pd.read_csv(f"{DATA_DIR}/test.csv", usecols=["space_id"])
sub = pd.read_csv(f"{DATA_DIR}/sample_submission.csv")

print(f"Train shape: {train.shape}, Test shape: {test.shape}")

# Fit DummyClassifier with most_frequent strategy
print("Fitting DummyClassifier (strategy='most_frequent')...")
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(train[["space_id"]], train["price_tier"])

# Generate predictions
print("Predicting on test data...")
preds = dummy.predict(test[["space_id"]])

# Populate submission
sub["price_tier"] = preds

output_path = "/kaggle/working/submission.csv"
sub.to_csv(output_path, index=False)
print(f"\nSaved dummy model submission to {output_path} successfully!")
print("Submission Preview:")
print(sub.head(10))
print(f"\nTotal rows: {len(sub):,}")
print("Predicted Class Counts:")
print(sub["price_tier"].value_counts())

