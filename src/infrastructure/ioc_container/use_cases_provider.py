from dishka import Provider, Scope, provide

from src.application.use_cases.client_message_use_case import ClientMessageUseCase
from src.application.use_cases.publish_client_message_use_case import PublishClientMessageUseCase


class UseCasesProvider(Provider):
    client_message_use_case = provide(ClientMessageUseCase, scope=Scope.SESSION)
    publish_client_message_use_case = provide(PublishClientMessageUseCase, scope=Scope.SESSION)
