import pickle
import pandas as pd

# Load trained model
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# Load Excel dataset
df = pd.read_excel("dataset/oou_chatbot_dataset.xlsx")

def get_response(tag):
    # Find all rows that match the predicted category
    responses = df[df["Category"] == tag]["Answer"].tolist()

    if responses:
        return responses[0]   # Return the first answer
    else:
        return "Sorry, I don't have an answer for that."

while True:
    message = input("You: ")

    if message.lower() == "exit":
        break

    X = vectorizer.transform([message])

    tag = model.predict(X)[0]

    response = get_response(tag)

    print("Bot:", response)