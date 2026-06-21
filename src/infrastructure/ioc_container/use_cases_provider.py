from dishka import Provider, Scope, provide

from src.application.use_cases.admin_message_use_case import AdminMessageUseCase
from src.application.use_cases.client_message_use_case import ClientMessageUseCase


class UseCasesProvider(Provider):
    client_message_use_case = provide(ClientMessageUseCase, scope=Scope.SESSION)
    admin_message_use_case = provide(AdminMessageUseCase, scope=Scope.REQUEST)
