import uvicorn


def main() -> None:
    uvicorn.run(
        "src.vakil_vision.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
