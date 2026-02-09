from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World from Python Backend Skill"}

# Add your REST API endpoints here to support your mission control dashboard and other projects
