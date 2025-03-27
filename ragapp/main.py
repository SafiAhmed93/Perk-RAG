import uvicorn


def main():
    uvicorn.run("ragapp.app:app", port=5001, reload=True)
    # uvicorn.run("ragapp.app:app", port=5001)


if __name__ == "__main__":
    main()
