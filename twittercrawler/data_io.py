import os, json
import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
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
        
class KafkaWriter():
    def __init__(self, topic, host="localhost", port=9092):
        self.host = host
        self.port = port
        self.topic = topic
        self._producer = KafkaProducer(bootstrap_servers='%s:%i' % (self.host, self.port))

    def write(self, results):
        for res in results:
            key_b = res["id_str"].encode("utf-8")
            value_b = json.dumps(res).encode("utf-8")
            self._producer.send(self.topic, key=key_b, value=value_b)
            
    def close(self):
        self._producer.close()

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
        
class KafkaReader():
    def __init__(self, topic, host="localhost", port=9092):
        self.host = host
        self.port = port
        self.topic = topic
        self.consumer = KafkaConsumer(bootstrap_servers='%s:%i' % (self.host, self.port))
            
    def close(self):
        self.consumer.close()