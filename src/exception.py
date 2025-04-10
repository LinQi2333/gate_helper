class FileDownloadError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message