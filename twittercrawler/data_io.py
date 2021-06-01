import os, json
import pandas as pd
from .utils import load_json_result

### Writers ###

class FileWriter():
    def __init__(self, file_path, clear=False):
        if clear or not os.path.exists(file_path):
            self._output_file = open(file_path, 'w')
        else:
            self._output_file = open(file_path, 'a')
            
    def write(self, results):
        for res in results:
            self._output_file.write("%s\n" % json.dumps(res))
            
    def close(self):
        self._output_file.close()
        

### Readers ###

class FileReader():
    def __init__(self, file_path):
        self._input_file = file_path
        
    def read(self, dataframe=True):
        records = load_json_result(self._input_file)
        if dataframe:
            return pd.DataFrame(records)
        else:
            return records