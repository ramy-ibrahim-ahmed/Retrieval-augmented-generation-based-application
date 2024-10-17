"""Configure OpenAI provider

- In third party we need to metegate Errors
- So set hard validation
"""

from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI

import logging


class OpenAIProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        max_input_num_tokens: int = 1000,
        max_output_num_tokens: int = 100,
        temperature: float = 0.1,
    ):
        self.max_input_num_tokens = max_input_num_tokens
        self.max_output_num_tokens = max_output_num_tokens
        self.temperature = temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=api_key,
            api_url=api_url,
        )

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def dummy(self):
        raise NotImplementedError

    def embed_text(self, text, document_type=None):
        if not self.client:
            self.logger.error("Embedding model for OpenAI wasn't set, No clint!")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI wasn't set, No ID!")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text,
        )

        if (
            not response
            or not response.data
            or len(response.data) == 0
            or not response.data[0].embedding
        ):
            self.logger.error("Error while embedding the text with OpenAI!")
            return None

        return response.data[0].embedding

    def generate_text(
        self,
        prompt,
        chat_history=...,
        max_output_tokens=None,
        temperature=None,
    ):
        if not self.client:
            self.logger.error("Generation model for OpenAI wasn't set, No clint!")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI wasn't set, No ID!")
            return None

        max_output_tokens = (
            max_output_tokens if max_output_tokens else self.max_output_num_tokens
        )

        temprature = temprature if temprature else self.temperature

        chat_history.append(
            self.construct_prompt(
                prompt=prompt,
                role=OpenAIEnums.USER.value,
            )
        )

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )

        if (
            not response
            or not response.choices
            or len(response.choices) == 0
            or not response.choices[0].message
        ):
            self.logger.error("Error while text generation with OpenAI!")
            return None

        return response.choices[0].message["content"]

    def construct_prompt(self, prompt, role):
        return {
            "role": role,
            "content": self.process_text(text=prompt),
        }

    def process_text(self, text: str):
        """Process text
        - Cut on max input num tokens (characters).
        """
        return text[: self.max_input_num_tokens].strip()
