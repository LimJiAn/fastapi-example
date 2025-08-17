from fastapi import FastAPI


app = FastAPI(title="Elice Board API")

@app.get("/")
def root():
    return {
        "message": "Elice Board API", 
    }
