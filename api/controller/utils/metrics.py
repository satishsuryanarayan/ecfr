import re

pattern: re.Pattern = re.compile(r'\b(shall|must|may not|prohibited|restricted|limited|regulated|restrained|curbed)\b')


def count_words(text: str) -> (int, int):
    return len(text.split()), len(pattern.findall(text, re.IGNORECASE))
