class QuerySearchException(Exception):
    def __init__(self, error_msg: str):
        self.error_msg = error_msg
        super().__init__(f"QuerySearchException: {self.error_msg}")
