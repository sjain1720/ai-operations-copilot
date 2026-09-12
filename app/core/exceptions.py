class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, identifier: object) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' was not found")


class LLMConfigurationError(Exception):
    pass


class LLMProviderError(Exception):
    pass


class ToolExecutionError(Exception):
    pass
