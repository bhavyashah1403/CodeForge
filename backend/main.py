from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Options Analytics Backend Running"}