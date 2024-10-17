"""Configure CoHere provider
"""

from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum

import cohere
import logging


class CoHereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
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

        self.clint = cohere.Client(api_key=api_key)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id, embedding_size):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[: self.max_input_num_tokens].strip()

    def embed_text(self, text, document_type=None):
        if not self.clint:
            self.logger.error("Embedding model for CoHere wasn't set, No clint!")
            return None

        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere wasn't set, No ID!")
            return None

        input_type = CoHereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY.value

        response = self.clint.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
        )

        if not response or not response.embeddings or not response.embeddings.float_[0]:
            self.logger.error("Error while embedding text with CoHere!")
            return None

        return response.embeddings.float_[0]

    def generate_text(
        self,
        prompt,
        chat_history=...,
        max_output_tokens=None,
        temprature=None,
    ):
        if not self.clint:
            self.logger.error("Generation model for CoHere wasn't set, No clint!")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere wasn't set, No ID!")
            return None

        max_output_tokens = (
            max_output_tokens if max_output_tokens else self.max_output_num_tokens
        )

        temprature = temprature if temprature else self.temperature

        response = self.clint.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temprature=temprature,
            max_tokens=max_output_tokens,
        )

        if not response or not response.txt:
            self.logger.error("Error while text generation with CoHere!")
            return None

        return response.text

    def construct_prompt(self, prompt, role):
        return {
            "role": role,
            "text": self.process_text(text=prompt),
        }
