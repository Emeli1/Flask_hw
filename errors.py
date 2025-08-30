class HttpError(Exception):
    def __init__(self, status_code: int, message: dict | str | list):
        self.status_code = status_code
        self.message = message