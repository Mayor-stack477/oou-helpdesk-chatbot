import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# -----------------------------------------------------
# PATHS
# -----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET = BASE_DIR / "dataset" / "oou_chatbot_dataset.xlsx"

# -----------------------------------------------------
# LOAD DATASET
# -----------------------------------------------------
print("Loading dataset...")

df = pd.read_excel(DATASET)

# Remove empty rows
df = df.dropna(subset=["Question", "Category"])

questions = df["Question"].astype(str)
labels = df["Category"].astype(str)

print(f"Loaded {len(df)} questions.")
print(f"Categories: {labels.nunique()}")

# -----------------------------------------------------
# SPLIT DATASET
# -----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    questions,
    labels,
    test_size=0.20,
    random_state=42,
    stratify=labels
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")

# -----------------------------------------------------
# TF-IDF
# -----------------------------------------------------
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# -----------------------------------------------------
# TRAIN MLP
# -----------------------------------------------------
model = MLPClassifier(
    hidden_layer_sizes=(128, 64),
    activation="relu",
    solver="adam",
    learning_rate_init=0.001,
    max_iter=1000,
    random_state=42
)

print("\nTraining model...")
model.fit(X_train_vec, y_train)

# -----------------------------------------------------
# EVALUATE MODEL
# -----------------------------------------------------
print("\nEvaluating model...")

predictions = model.predict(X_test_vec)

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, average="weighted")
recall = recall_score(y_test, predictions, average="weighted")
f1 = f1_score(y_test, predictions, average="weighted")

print("\n===================================")
print("MODEL PERFORMANCE")
print("===================================")

print(f"Accuracy : {accuracy*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
print(f"Recall   : {recall*100:.2f}%")
print(f"F1-Score : {f1*100:.2f}%")

print("\n===================================")
print("CLASSIFICATION REPORT")
print("===================================")

print(classification_report(y_test, predictions))

# -----------------------------------------------------
# CONFUSION MATRIX
# -----------------------------------------------------
conf_matrix = confusion_matrix(y_test, predictions)

print("\n===================================")
print("CONFUSION MATRIX")
print("===================================")

print(conf_matrix)

classes = sorted(labels.unique())

plt.figure(figsize=(10,8))

sns.heatmap(
    conf_matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=classes,
    yticklabels=classes
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted Class")
plt.ylabel("Actual Class")

plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)

plt.tight_layout()

plt.savefig(BASE_DIR / "confusion_matrix.png", dpi=300)

plt.show()

# -----------------------------------------------------
# PERFORMANCE BAR CHART
# -----------------------------------------------------

metrics = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1-Score"
]

values = [
    accuracy * 100,
    precision * 100,
    recall * 100,
    f1 * 100
]

plt.figure(figsize=(8,5))

bars = plt.bar(metrics, values)

plt.ylim(0,100)

plt.ylabel("Percentage (%)")

plt.title("Performance Evaluation of MLP Model")

for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 1,
        f"{height:.2f}%",
        ha="center"
    )

plt.tight_layout()

plt.savefig(BASE_DIR / "model_performance.png", dpi=300)

plt.show()

# -----------------------------------------------------
# SAVE MODEL
# -----------------------------------------------------

MODEL_PATH = Path(__file__).resolve().parent

pickle.dump(
    model,
    open(MODEL_PATH / "model.pkl", "wb")
)

pickle.dump(
    vectorizer,
    open(MODEL_PATH / "vectorizer.pkl", "wb")
)

print("\n===================================")
print("Training completed successfully.")
print("model.pkl saved")
print("vectorizer.pkl saved")
print("confusion_matrix.png saved")
print("model_performance.png saved")
print("===================================")