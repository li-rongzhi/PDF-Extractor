import openai
from enum import Enum

import tiktoken


class PromptTemplate(Enum):
    CONSISTENCY_CHECK = "Do you think the following phrases or sentences reasonable? " \
                       + "Just tell me 'Yes' or 'No'."
    ISHEADER_CHECK = "Do you think the following words are headers of a table? Just tell me 'Yes' or 'No'."
    GRAMMAR_CORRECTION = "Correct grammar, spellings and whitespace usage of the following paragraph."


class ExternalModel:
    def __init__(self, openai_key):
        self.openai_key = openai_key

    def get_response(self, content, template, stop_sequence=None):
        openai.api_key = self.openai_key
        prompt = template.value + content
        max_tokens = ExternalModel.calculate_token_num(prompt, template)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user",
                       "content": prompt}],
            temperature=0,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    @staticmethod
    def calculate_token_num(prompt, template):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(prompt))
        result = num_tokens + 5
        if template == PromptTemplate.GRAMMAR_CORRECTION:
            result = 2 * num_tokens
        return result
