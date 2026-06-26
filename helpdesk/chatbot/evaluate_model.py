import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Load dataset
print("Loading dataset...")

df = pd.read_excel("dataset/oou_chatbot_dataset.xlsx")

questions = df["Question"]
labels = df["Category"]

# Load vectorizer
vectorizer = pickle.load(open("chatbot/vectorizer.pkl", "rb"))

# Convert text to vectors
X = vectorizer.transform(questions)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    labels,
    test_size=0.2,
    random_state=42
)

# Load trained model
model = pickle.load(open("chatbot/model.pkl", "rb"))

# Predict
predictions = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, predictions)

print("\n==============================")
print("MODEL EVALUATION")
print("==============================")

print(f"Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report\n")

print(classification_report(y_test, predictions))

print("\nConfusion Matrix\n")

print(confusion_matrix(y_test, predictions))