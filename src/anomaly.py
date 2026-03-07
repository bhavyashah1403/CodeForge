from sklearn.ensemble import IsolationForest
import pandas as pd


def detect_anomalies(df, feature_cols, contamination=0.02):
    if df.empty:
        return pd.Series(dtype=int)
    X = df[feature_cols].fillna(0)
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(X)
    return pd.Series(preds, index=df.index)
