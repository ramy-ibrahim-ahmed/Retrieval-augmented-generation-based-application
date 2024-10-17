from .LLMEnums import LLMEnums
from . import OpenAIProvider, CoHereProvider


class LLMProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAPI_URL,
                max_input_num_tokens=self.config.MAX_INPUT_NUM_TOKENS,
                max_output_num_tokens=self.config.MAX_OUTPUT_NUM_TOKENS,
                temperature=self.config.TEMPERATURE,
            )

        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                max_input_num_tokens=self.config.MAX_INPUT_NUM_TOKENS,
                max_output_num_tokens=self.config.MAX_OUTPUT_NUM_TOKENS,
                temperature=self.config.TEMPERATURE,
            )

        return None
