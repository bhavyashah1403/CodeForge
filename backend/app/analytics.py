def feature_engineering(df):

    df["put_call_ratio"] = df["put_volume"] / df["call_volume"]

    df["total_oi"] = df["call_oi"] + df["put_oi"]

    return df