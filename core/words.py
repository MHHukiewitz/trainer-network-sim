from typing import List

words: List[str]
with open('resources/words_alpha.txt') as word_file:
    words = list(word_file.read().split())
