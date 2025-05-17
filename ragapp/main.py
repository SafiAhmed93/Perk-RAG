import uvicorn


def main():
    uvicorn.run("ragapp.app:app", port=5001, reload=True)


if __name__ == "__main__":
    main()
