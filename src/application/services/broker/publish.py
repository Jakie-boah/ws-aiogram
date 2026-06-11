import structlog


class PublisherService:
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger

    async def publish_client_message(self):
        pass

    async def publish_admin_message(self):
        pass
