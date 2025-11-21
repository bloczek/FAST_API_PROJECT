from fastapi import FastAPI

from fast_api.src.web import explorer

app = FastAPI()

app.include_router(explorer.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/echo/{items}")
def echo_items(items: str):
    return {"echo": items}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
