from typing import List


def create_items_from_text(text: str, min_words_cnt, split_paragraphs, merge_paragraphs) -> List[str]:
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