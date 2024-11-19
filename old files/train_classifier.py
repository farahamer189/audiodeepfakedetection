import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_and_evaluate(csv_path, model_output="classifier.pkl"):
    # Load dataset
    data = pd.read_csv(csv_path, header=None)
    X = data.iloc[:, :-1].values
    y = data.iloc[:, -1].values

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train classifier
    clf = SVC()
    clf.fit(X_train, y_train)

    # Evaluate classifier
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100:.2f}%")

    # Save the trained classifier
    import joblib
    joblib.dump(clf, model_output)
    print(f"Classifier saved to {model_output}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train and evaluate SVM classifier")
    parser.add_argument("--csv_path", type=str, required=True, help="Path to input CSV dataset")
    parser.add_argument("--model_output", type=str, default="classifier.pkl", help="Path to save trained classifier")
    args = parser.parse_args()
    train_and_evaluate(args.csv_path, args.model_output)
