import re
import string

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer

punctuation = set(string.punctuation)
stop_words = set(stopwords.words('english'))
pattern: re.Pattern = re.compile(r'\b(shall|must|may not|prohibited|restricted|limited|regulated|restrained|curbed)\b')


def count_words(text: str) -> (int, int):
    tokens = word_tokenize(text)
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words and word not in punctuation]
    return len(filtered_tokens), len(
        pattern.findall(TreebankWordDetokenizer().detokenize(filtered_tokens), re.IGNORECASE))
