class LocalException(Exception):
    detail: str
    status: int
    message: str

    def __init__(self, **kwargs):
        super().__init__()
        self.message = kwargs.get('message') or ''
        self.status: int = kwargs.get('status') or 500  # or (200 if self.message == '' else 400)
        self.detail = {'loc': [kwargs.get('location')], 'msg': self.message, 'type': kwargs.get('type')}.__str__()

    def __str__(self):
        return self.message
