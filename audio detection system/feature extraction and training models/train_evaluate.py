import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

#loading the csv files
fake_val = pd.read_csv("features_fake_val.csv")
fake_train = pd.read_csv("features_fake_train.csv")
fake_test = pd.read_csv("features_fake_test.csv")

real_val = pd.read_csv("features_real_val.csv")
real_train = pd.read_csv("features_real_train.csv")
real_test = pd.read_csv("features_real_test.csv")

# Combining the csv files, defining the features and target,normalizing scales,removing rows with missing valus and getting the csv dataset ready for training
data_fake = pd.concat([fake_val, fake_train, fake_test], axis=0)
data_real = pd.concat([real_val, real_train, real_test], axis=0)

data_fake['label'] = 0  # Fake = 0
data_real['label'] = 1  # Real = 1
data = pd.concat([data_fake, data_real], axis=0).reset_index(drop=True)
feature_columns = ['wav2vec_embeddings', 'mfcc', 'formants', 'hnr', 'pause_analysis', 'wavelets', 'psychoacoustic']
X = data[feature_columns].values
y = data['label'].values

def parse_feature_array(column):
    parsed_data = []
    for row in column:
        if isinstance(row, str):
            try:
                arr = np.fromstring(row.strip("[]"), sep=",")
                parsed_data.append(arr.flatten())  
            except ValueError:
                print(f"Warning: Skipping malformed data: {row}")
                parsed_data.append(np.zeros((1,)))  
        elif isinstance(row, float):
            if np.isnan(row):
                print("Warning: Encountered NaN, replacing with zeros.")
                parsed_data.append(np.zeros((1,)))  
            else:
                parsed_data.append(np.array([row]))  
        elif isinstance(row, (np.ndarray, list)):
            parsed_data.append(np.array(row).flatten())  
        elif pd.isnull(row):
            print("Warning: Encountered NaN, replacing with zeros.")
            parsed_data.append(np.zeros((1,)))
        else:
            raise ValueError(f"Unsupported data type in feature column: {type(row)}")
    return np.array(parsed_data)
parsed_features = []
for col in feature_columns:
    print(f"Parsing column: {col}")
    feature_array = parse_feature_array(data[col])
    print(f"Shape of {col}: {feature_array.shape}")
    parsed_features.append(feature_array)

parsed_features = [arr if arr.ndim == 2 else arr.reshape(-1, 1) for arr in parsed_features]
X = np.hstack(parsed_features)

print("checking for na")
if np.isnan(X).any():
    print("removing rows containing na")
    nan_mask = ~np.isnan(X).any(axis=1)  # Mask for rows without NaN
    X = X[nan_mask]
    y = y[nan_mask]
    print(f"updated rows: {X.shape}")
else:
    print("no missing values")


scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)



#training models
#gradient boost model
gb_model = GradientBoostingClassifier()
gb_model.fit(X_train, y_train)
gb_predictions = gb_model.predict(X_test)
gb_accuracy = accuracy_score(y_test, gb_predictions)
print(f"Gradient Boost accuracy: {gb_accuracy:.2f}")

#random forest model
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)
rf_predictions = rf_model.predict(X_test)
rf_accuracy = accuracy_score(y_test, rf_predictions)
print(f"Random Forest accuracy: {rf_accuracy:.2f}")

#SVM model
svm_model = SVC(probability=True)
svm_model.fit(X_train, y_train)
svm_predictions = svm_model.predict(X_test)
svm_accuracy = accuracy_score(y_test, svm_predictions)
print(f"SVM accuracy: {svm_accuracy:.2f}")

# FCNN model
class FCNN(nn.Module):
    def __init__(self, input_size, num_classes):
        super(FCNN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.fc(x)

def prepare_dataloader(X, y, batch_size=32):
    tensor_X = torch.tensor(X, dtype=torch.float32)
    tensor_y = torch.tensor(y, dtype=torch.long)
    dataset = TensorDataset(tensor_X, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

def train_fcnn(X_train, y_train, X_val, y_val, input_size, num_classes, epochs=20, batch_size=32):
    model = FCNN(input_size=input_size, num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_loader = prepare_dataloader(X_train, y_train, batch_size)
    val_loader = prepare_dataloader(X_val, y_val, batch_size)

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        print(f"epoch {epoch+1}/{epochs}, train Loss: {train_loss/len(train_loader):.4f}, "
              f"val Loss: {val_loss/len(val_loader):.4f}, val Accuracy: {100 * correct/total:.2f}%")

    return model

fcnn_model = train_fcnn(
    X_train=X_train, y_train=y_train,
    X_val=X_val, y_val=y_val,
    input_size=X_train.shape[1], num_classes=len(set(y)),
    epochs=20
)

#FCNN testing
def test_fcnn(model, X_test, y_test):
    model.eval()
    test_loader = prepare_dataloader(X_test, y_test, batch_size=32)
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    return 100 * correct / total

fcnn_accuracy = test_fcnn(fcnn_model, X_test, y_test)
print(f"FCNN accuracy: {fcnn_accuracy:.2f}%")

