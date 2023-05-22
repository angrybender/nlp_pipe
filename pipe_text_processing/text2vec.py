import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.feature_extraction.text import HashingVectorizer
import tqdm


class BertVectorizer:
    D_SIZE = 312

    def __init__(self, model_path, use_gpu=False):
        if model_path[-1] != '/':
            model_path += '/'

        self._tokenizer = AutoTokenizer.from_pretrained(model_path + 'tokenizer')
        self._model = AutoModel.from_pretrained(model_path)
        self._use_gpu = use_gpu

        if use_gpu:
            self._model.cuda()

    def _embed_bert_cls(self, text):
        t = self._tokenizer(text, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self._model(**{k: v.to(self._model.device) for k, v in t.items()})
        embeddings = model_output.last_hidden_state[:, 0, :]
        embeddings = torch.nn.functional.normalize(embeddings)
        return embeddings[0].cpu().numpy()

    def fit_transform(self, texts, use_progress=False):
        X = []

        iterator = tqdm.tqdm_notebook(texts) if use_progress else texts

        for t in iterator:
            X.append(self._embed_bert_cls(t).tolist())

        return X


class BowVectorizer:
    D_SIZE = 312

    def __init__(self):
        self._model = HashingVectorizer(n_features=self.D_SIZE, analyzer='char_wb', ngram_range=(3, 3))

    def get_vec(self, text: str):
        return self._model.fit_transform([text]).toarray()[0]

    def fit_transform(self, texts):
        return [v.tolist() for v in self._model.fit_transform(texts).toarray()]
