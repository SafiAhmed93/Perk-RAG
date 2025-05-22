import uvicorn


def main():
    uvicorn.run("ragapp.app:app", port=5001, reload=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
