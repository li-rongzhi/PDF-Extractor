import openai
from enum import Enum

import tiktoken


class PromptTemplate(Enum):
    CONSISTENCY_CHECK = "Do you think the following phrases or sentences reasonable? " \
                       + "Just tell me 'Yes' or 'No'."
    ISHEADER_CHECK = "Do you think the following words are headers of a table? Just tell me 'Yes' or 'No'."
    GRAMMAR_CORRECTION = "Correct grammar and spellings of the following paragraph."


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

    # @staticmethod
    # def calculate_token_num(prompt, template):
    #     tokenizer = tiktoken.Tokenizer('gpt-3.5-turbo')
    #     token_count = tokenizer.count_tokens(prompt)
    #     token_num = token_count + 5
    #     if template == PromptTemplate.GRAMMAR_CORRECTION:
    #         token_num = 2 * token_count
    #     return token_num

    @staticmethod
    def calculate_token_num(prompt, template):
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(prompt))
        result = num_tokens + 5
        if template == PromptTemplate.GRAMMAR_CORRECTION:
            result = 2 * num_tokens
        return result


# key = "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"
# model = ExternalModel(key)
# content = "Category; Count; Price"
# answer = model.get_response(content, PromptTemplate.ISHEADER_CHECK)
# print(answer)
# content = """Copyright © 20 20 NonDisclosureAgreement.com . All Rights Reserved.  Page 1 of 2 NON -DISCLOSURE AGREEMENT  (NDA)
# This Nondisclosure Agreement or ("Agreement") has been  entered into on the date of
# ______________________________ and is by and between :"""
# answer = model.get_response(content, PromptTemplate.GRAMMAR_CORRECTION)
# print(answer)
# footnotes = {'0': ['Copyright © 2020 NonDisclosureAgreement.com. All Rights Reserved.', 'Page 1 of 2'],
#              '1': ['Copyright © 2020 NonDisclosureAgreement.com. All Rights Reserved.', 'Page 2 of 2']}
#
# for footnote in footnotes['0']:
#     if footnote in answer:
#         answer = answer.replace(footnote, "")
#         print(footnote)
#
# print(answer)
