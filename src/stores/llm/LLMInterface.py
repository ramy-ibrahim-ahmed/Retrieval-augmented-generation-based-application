"""Interface for llms

- Generation model
- Embedding model
"""

from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        chat_history: list = [],
        max_output_tokens: int = None,
        temprature: float = None,
    ):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """
        Before Generating the text the prompt must be handled.
        """
        pass

    @abstractmethod
    def dummy(self):
        """
        Dummy Interface function
        """
        pass
