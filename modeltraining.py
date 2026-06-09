<<<<<<< HEAD
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset
df = pd.read_csv("book.csv")

# Clean column names

df["gender"] = df["gender"].str.strip().str.lower()
df["mood"] = df["mood"].str.strip().str.lower()
df["platform"] = df["platform"].str.strip().str.lower()

#Encode
le_gender = LabelEncoder()
le_mood = LabelEncoder()
le_platform = LabelEncoder()

df["gender"] = le_gender.fit_transform(df["gender"])
df["mood"] = le_mood.fit_transform(df["mood"])
df["platform"] = le_platform.fit_transform(df["platform"])
# Features and target
x = df[["age", "gender", "platform","frequency", "timespent", "mood"]].values
y = df["stress"]

print(x)
# Train model
model = LinearRegression()
model.fit(x, y)

# Accuracy
print("R2 Score:", model.score(x, y))

# Save model and encoders
with open("model_train.pkl", "wb") as f:
    pickle.dump(model, f)

with open("gender_encoder.pkl", "wb") as f:
    pickle.dump(le_gender, f)

with open("mood_encoder.pkl", "wb") as f:
    pickle.dump(le_mood, f)

with open("platform_encoder.pkl","wb") as f:
    pickle.dump(le_platform,f)

print(le_platform.classes_)
print("Model trained and saved successfully!")
=======
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import pickle

# Load dataset
df = pd.read_csv("book.csv")

# Clean column names

df["gender"] = df["gender"].str.strip().str.lower()
df["mood"] = df["mood"].str.strip().str.lower()
df["platform"] = df["platform"].str.strip().str.lower()

#Encode
le_gender = LabelEncoder()
le_mood = LabelEncoder()
le_platform = LabelEncoder()

df["gender"] = le_gender.fit_transform(df["gender"])
df["mood"] = le_mood.fit_transform(df["mood"])
df["platform"] = le_platform.fit_transform(df["platform"])
# Features and target
x = df[["age", "gender", "platform","frequency", "timespent", "mood"]].values
y = df["stress"]

print(x)
# Train model
model = LinearRegression()
model.fit(x, y)

# Accuracy
print("R2 Score:", model.score(x, y))

# Save model and encoders
with open("model_train.pkl", "wb") as f:
    pickle.dump(model, f)

with open("gender_encoder.pkl", "wb") as f:
    pickle.dump(le_gender, f)

with open("mood_encoder.pkl", "wb") as f:
    pickle.dump(le_mood, f)

with open("platform_encoder.pkl","wb") as f:
    pickle.dump(le_platform,f)

print(le_platform.classes_)
print("Model trained and saved successfully!")
>>>>>>> 4b1ebbc87824798c417faee0baa7f601b0d9ebe8
