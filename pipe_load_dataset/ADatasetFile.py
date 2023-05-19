from typing import List
import json
import pandas as pd

class ADatasetFile:
    @staticmethod
    def farbic(d_type):
        if d_type == 'ljson':
            return LoadLJSON()
        elif d_type == 'csv':
            return LoadCSV()
        else:
            raise Exception("Invalid type!")

    def __int__(self):
        self.file_path = ''

    def load(self, file_path, parameters=None):
        self.file_path = file_path
        self.parameters = parameters

    def get_count(self) -> int:
        pass

    def get_items(self) -> List[str]:
        pass


class LoadLJSON(ADatasetFile):
    def _read_lines(self):
        with open(self.file_path, 'r', encoding='utf8') as f:
            return [line for line in f.read().split("\n") if line]

    def get_items(self) -> List[str]:
        assert 'field' in self.parameters

        lines = (json.loads(line) for line in self._read_lines())
        return [line[self.parameters['field']] for line in lines if line[self.parameters['field']]]

    def get_count(self) -> int:
        return len(self._read_lines())


class LoadCSV(ADatasetFile):
    def get_count(self) -> int:
        df = pd.read_csv(self.file_path)
        return df.shape[0]

    def get_items(self) -> List[str]:
        assert 'field' in self.parameters
        df = pd.read_csv(self.file_path)
        df.fillna('', inplace=True)
        return df[self.parameters['field']].values

