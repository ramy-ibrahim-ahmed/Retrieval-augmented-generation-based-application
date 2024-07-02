from fastapi import FastAPI

app = FastAPI()

# Get request
@app.get("/welcome")
def welcome():
    return {"message": "hello world!"}
