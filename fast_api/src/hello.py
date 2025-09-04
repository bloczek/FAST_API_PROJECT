from fastapi import FastAPI

app = FastAPI()


@app.get("/hii")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("hello:app", reload=True)
