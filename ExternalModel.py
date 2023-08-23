import openai
from enum import Enum
import tiktoken


class PromptTemplate(Enum):
    """Some templates of prompt for chatgpt"""
    CONSISTENCY_CHECK = "Do you think the following phrases or sentences reasonable? " \
                        + "Just tell me 'Yes' or 'No'."
    ISHEADER_CHECK = "Do you think the following words are headers of a table? Just tell me 'Yes' or 'No'."
    GRAMMAR_CORRECTION = "Correct grammar, spellings of the following paragraph."


class ExternalModel:
    """
    An abstraction of establishing connection,
    requesting response from external model(gpt-3.5-turbo)
    """

    def __init__(self, openai_key: str):
        """Instantiate with openai api key."""
        self.openai_key = openai_key

    def get_response(self, content: str, template: PromptTemplate):
        """Get response from the external model."""
        # set api key to establish connection
        openai.api_key = self.openai_key
        prompt = template.value + content
        # calculate the token needed
        max_tokens = ExternalModel.calculate_token_num(prompt, template)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user",
                       "content": prompt}],
            temperature=0,
            max_tokens=max_tokens
        )
        # extract response content
        return response.choices[0].message.content

    @staticmethod
    def calculate_token_num(prompt: str, template: PromptTemplate):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(prompt))
        if template == PromptTemplate.GRAMMAR_CORRECTION:
            result = 2 * num_tokens
        else:
            # if response is Yes or No
            result = num_tokens + 5
        return result
