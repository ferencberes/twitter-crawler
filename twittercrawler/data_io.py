import os, json
import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
from .utils import load_json_result

### Writers ###

filter_options = [None,"tweet","retweet","quote","mention"]

def filter_data(record, filter_type):
    if filter_type == "tweet":
        return (not "retweeted_status" in record) and (not "quoted_status" in record)
    elif filter_type == "retweet":
        return "retweeted_status" in record
    elif filter_type == "quote":
        return "quoted_status" in record
    elif filter_type == "mention":
        return "user_mentions" in record["entities"] and len(record["entities"]["user_mentions"]) > 0
    else:
        return True

class Writer():
    def __init__(self, include_mask=None, exclude_mask=None, export_filter=None):
        self._include_mask = include_mask
        self._exclude_mask = exclude_mask
        if export_filter in filter_options:
            self._export_filter = export_filter
        else:
            raise ValueError("Invalid filter option! Choose from: %s" % str(filter_options))
        
    def _prepare_record(self, record):
        accepted = filter_data(record, self._export_filter)
        if accepted:
            if self._include_mask != None:
                rec = {}
                for key in self._include_mask:
                    rec[key] = record[key]
            else:
                rec = record.copy()
                if self._exclude_mask != None:
                    for key in self._exclude_mask:
                        del rec[key]
            return json.dumps(rec)
        else:
            return None
        
    def write(self, results):
        pass

class FileWriter(Writer):
    def __init__(self, file_path, clear=False, include_mask=None, exclude_mask=None, export_filter=None):
        super(FileWriter, self).__init__(include_mask, exclude_mask, export_filter)
        if clear or not os.path.exists(file_path):
            self._output_file = open(file_path, 'w')
        else:
            self._output_file = open(file_path, 'a')
            
    def write(self, results):
        for res in results:
            record = self._prepare_record(res)
            if record != None:
                self._output_file.write("%s\n" % record)
            
    def close(self):
        self._output_file.close()
        
class KafkaWriter(Writer):
    def __init__(self, topic, host="localhost", port=9092, include_mask=None, exclude_mask=None, export_filter=None):
        super(KafkaWriter, self).__init__(include_mask, exclude_mask, export_filter)
        self.host = host
        self.port = port
        self.topic = topic
        self._producer = KafkaProducer(bootstrap_servers='%s:%i' % (self.host, self.port))

    def write(self, results):
        for res in results:
            record = self._prepare_record(res)
            if record != None:
                key_b = res["id_str"].encode("utf-8")
                value_b = record.encode("utf-8")
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