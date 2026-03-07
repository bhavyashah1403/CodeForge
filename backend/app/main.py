from fastapi import FastAPI
import pandas as pd

app = FastAPI()

df = pd.read_csv("data/options_data.csv")

@app.get("/volume")
def volume():

    data = df.groupby("timestamp")[["call_volume","put_volume"]].sum()

    return data.to_dict()