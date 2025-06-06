import re

pattern: re.Pattern = re.compile(r'\b(shall|must|may not|prohibited)\b')


def count_words(text: str) -> (int, int):
    return len(text.split()), len(pattern.findall(text, re.IGNORECASE))
