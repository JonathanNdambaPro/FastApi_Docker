from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return "Hello world"

@app.get("/path")
def get_path():
    return "this is a path"

@app.post("/post_method")
def post_method():
    return "this is a post methode"