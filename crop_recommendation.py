import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# ✅ Load dataset
data = pd.read_csv("Crop_recommendation_final_v2.csv")

# ✅ Map crops to numerical values
crop_dict = {crop: i+1 for i, crop in enumerate(data['label'].unique())}
reverse_crop_dict = {v: k for k, v in crop_dict.items()}  # Reverse mapping
data['crop_num'] = data['label'].map(crop_dict)
data.drop(['label'], axis=1, inplace=True)

# ✅ Train model only on these features (🚫 NO soil moisture)
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['crop_num']

# ✅ Print feature order for debugging
print("Feature order during training:", X.columns.tolist())

# ✅ Stratified Split (Ensures Balanced Classes in Train-Test)
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_index, test_index in split.split(X, y):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

# ✅ Feature Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ✅ Train Optimized RandomForest Model
model = RandomForestClassifier(
    n_estimators=300, max_depth=20, min_samples_split=10, min_samples_leaf=5, 
    max_features="sqrt", random_state=42
)
model.fit(X_train, y_train)

# ✅ Evaluate Model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"✅ Model Accuracy: {accuracy:.4f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))

# ✅ Feature Importance (Helps in Explainability)
plt.figure(figsize=(10, 6))
plt.barh(X.columns, model.feature_importances_, color="skyblue")
plt.xlabel("Feature Importance")
plt.ylabel("Features")
plt.title("Feature Importance in Crop Recommendation Model")
plt.show()

# ✅ Save Model & Preprocessing Objects
joblib.dump(model, "crop_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(reverse_crop_dict, "reverse_crop_dict.pkl")

print("\n✅ Model, Scaler, and Crop Dictionary saved successfully!")
