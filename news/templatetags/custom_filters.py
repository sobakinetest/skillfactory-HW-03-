from django import template
from news.resources import CENSORED_WORDS
import re

register = template.Library()

@register.filter
def censor(text):
    if not isinstance(text, str):
        return text

    for word in CENSORED_WORDS:
        if len(word) <= 1:
            continue

        def replace_match(match):
            matched_word = match.group()
            return matched_word[0] + '*' * (len(matched_word) - 1)

        pattern = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
        text = pattern.sub(replace_match, text)

    return text