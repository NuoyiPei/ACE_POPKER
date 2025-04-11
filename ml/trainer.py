import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import List, Tuple
import numpy as np

def prepare_data(records: List[dict]) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare training data from hand records"""
    df = pd.DataFrame(records)
    X = df[["is_suited", "rank_gap", "high_card", "position_index", 
            "pot", "current_bet", "num_community_cards", "is_pair",
            "is_connector", "is_ace", "pot_odds"]]
    y = df["action"]
    return X, y

def train_model(X: np.ndarray, y: np.ndarray, model_path: str = "ml/model.pkl") -> None:
    """Train and save the model"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    joblib.dump(model, model_path)
    
    # Print model performance
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"Training accuracy: {train_score:.2f}")
    print(f"Testing accuracy: {test_score:.2f}")

def load_model(model_path: str = "ml/model.pkl"):
    """Load trained model"""
    return joblib.load(model_path) 