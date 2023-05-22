from typing import List
import re
import unicodedata
_REPLACE_PATTERNS = [
    ('\xa0', ' '),
    ('\u202f', '')
]


def _strip_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    cleaned = u"".join([c for c in nfkd_form if ord(c) != 769])
    return unicodedata.normalize('NFKC', cleaned)


def create_items_from_text(text: str, min_words_cnt, split_paragraphs, merge_paragraphs) -> List[str]:
    for _from, _to in _REPLACE_PATTERNS:
        text = text.replace(_from, _to)
    text = _strip_accents(text)

    if not split_paragraphs and min_words_cnt > 0:
        return [text] if len(text) > min_words_cnt else []
    elif not split_paragraphs:
        return [text]

    paragraphs = text.split("\n")
    paragraphs = [{'cnt': len(p.split()), 'text': p} for p in paragraphs if p]
    if min_words_cnt > 0:
        paragraphs = [p for p in paragraphs if p['cnt'] >= min_words_cnt]

    if len(paragraphs) == 0:
        return []

    if not merge_paragraphs:
        return [p['text'] for p in paragraphs]

    avg_words = sum([p['cnt'] for p in paragraphs])/len(paragraphs)
    for i, p in enumerate(paragraphs):
        if i == 0 or not p:
            continue

        last_len = paragraphs[i - 1]['cnt']
        current_len = paragraphs[i]['cnt']

        if current_len < avg_words:
            paragraphs[i]['text'] = paragraphs[i - 1]['text'] + ' ' + p['text']
            paragraphs[i]['cnt'] += last_len
            paragraphs[i - 1] = {}

    return [p['text'] for p in paragraphs if p]