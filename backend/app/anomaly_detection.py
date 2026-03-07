from sklearn.ensemble import IsolationForest

def detect_anomalies(df):

    model = IsolationForest(contamination=0.01)

    df["anomaly"] = model.fit_predict(
        df[["call_volume","put_volume","call_oi","put_oi"]]
    )

    return df