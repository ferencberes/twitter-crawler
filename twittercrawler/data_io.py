import os, json, socket
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
    """
    Abstract class to handle tweets export.

    Parameters
    ----------
    include_mask
        Include only the specified keys in the exported tweet JSON content.
    exclude_mask
        Exclude the specified keys from the exported tweet JSON content.
    export_filter
        Choose from these values `[None,"tweet","retweet","quote","mention"]` to filter the exported content. In case of the default value `None` every hit is exported.
    """
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
        
    def write(self, results, enc="utf-8"):
        """
        Export recently collected tweets
        
        Parameters
        ----------
        results
           List of collected tweets in JSON
        enc
           Set encoding for serialization
        """
        pass
    
    def close(self):
        """Close writer object"""
        pass

class FileWriter(Writer):
    """
    Export tweets to file.

    Parameters
    ----------
    file_path
        Output file path
    clear
        Clear output file. Use `clear=False` to append new tweets to former search results.
    """
    def __init__(self, file_path, clear=False, include_mask=None, exclude_mask=None, export_filter=None):
        super(FileWriter, self).__init__(include_mask, exclude_mask, export_filter)
        if clear or not os.path.exists(file_path):
            self._output_file = open(file_path, 'w')
        else:
            self._output_file = open(file_path, 'a')
            
    def write(self, results, enc="utf-8"):
        for res in results:
            record = self._prepare_record(res)
            if record != None:
                self._output_file.write("%s\n" % record)
            
    def close(self):
        self._output_file.close()

class SocketWriter(Writer):
    """
    Export tweets to socket.

    Parameters
    ----------
    port
        Set port for the socket
    host
        Set host for the socket
    ip
        Set IP address for the socket.
    max_size
        Set maximum set size for stored Tweet identifiers
    separator
        Set string separator between exported tweets
    """
    def __init__(self, port, host="localhost", ip=None, max_size=10000, separator="###SOCKETSEP###", include_mask=None, exclude_mask=None, export_filter=None):
        super(SocketWriter, self).__init__(include_mask, exclude_mask, export_filter)
        self._conn = None
        self._port = port
        self._ip = socket.gethostbyname(host) if ip == None else ip
        self._sep = separator
        self.max_size = max_size
        self.seen_ids = []
        self._connect()
        
    def _connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self._ip, self._port))
        print ("Socket binded to port %i" % self._port)
        s.listen(5)
        print ("Socket is listening...")
        self._conn, addr = s.accept()
        print ('Got connection from', addr)

    def write(self, results, enc="utf-8"):
        if self._conn == None:
            raise RuntimeError("No connection was established!")
        else:
            for res in results:
                record = self._prepare_record(res)
                tweet_id = res["id_str"]
                if record != None and not tweet_id in self.seen_ids:
                    record += self._sep
                    msg = record.encode(enc)
                    self._conn.send(msg)
                    self.seen_ids.append(tweet_id)
            if len(self.seen_ids) > self.max_size:
                self.seen_ids = self.seen_ids[int(max_size*0.2):]
            
    def close(self):
        if self._conn != None:
            self._conn.close()
        
class KafkaWriter(Writer):
    """
    Export tweets to Kafka queue.

    Parameters
    ----------
    topic
        Set topic for the KafkaProducer
    port
        Set port for the KafkaProducer
    host
        Set host for the KafkaProducer
    """
    def __init__(self, topic, port=9092, host="localhost", include_mask=None, exclude_mask=None, export_filter=None):
        super(KafkaWriter, self).__init__(include_mask, exclude_mask, export_filter)
        self.host = host
        self.port = port
        self.topic = topic
        self._producer = KafkaProducer(bootstrap_servers='%s:%i' % (self.host, self.port))

    def write(self, results, enc="utf-8"):
        for res in results:
            record = self._prepare_record(res)
            if record != None:
                key_b = res["id_str"].encode(enc)
                value_b = record.encode(enc)
                self._producer.send(self.topic, key=key_b, value=value_b)
            
    def close(self):
        self._producer.close()

### Readers ###

class StreamReader():
    def read(self, return_dict=True, enc="utf-8"):
        """
        Read exported tweets.
        
        Parameters
        ----------
        return dict
            Return tweet as a dictionary (instead of string)
        enc
            Encoding used for serialization
        """
        pass
    
    def close(self):
        """Close reader object"""
        pass

class FileReader():
    """
    Read exported tweets from file.

    Parameters
    ----------
    file_path
        File path of the exported tweets
    """
    def __init__(self, file_path):
        self._input_file = file_path
        
    def read(self, dataframe=True):
        """
        Read exported tweets.
        
        Parameters
        ----------
        dataframe
            Return results in a pandas.DataFrame
        """
        records = load_json_result(self._input_file)
        if dataframe:
            return pd.DataFrame(records)
        else:
            return records
        
class SocketReader(StreamReader):
    """
    Read exported tweets from socket.

    Parameters
    ----------
    port
        Port of the socket
    host
        Host of the socket
    ip
        IP address of the socket.
    buffersize
        Set buffersize for socket I/O
    separator
        String separator between exported tweets
    """
    def __init__(self, port, host="localhost", ip=None, buffersize=1024, separator="###SOCKETSEP###"):
        self.sock = None
        self._port = port
        self._ip = socket.gethostbyname(host) if ip == None else ip
        self._buffsize = buffersize
        self._sep = separator
        self._connect()
        
    def _connect(self):
        self.sock = socket.socket()
        self.sock.connect((self._ip, self._port))
            
    def read(self, return_dict=True, enc="utf-8"):
        received_str = ""
        received_msg = 0
        while True:
            bytes_received = self.sock.recv(self._buffsize)
            if bytes_received == b'':
                break
            received_str += bytes_received.decode(enc) 
            if self._sep in received_str:
                splitted = received_str.split(self._sep)
                received_str = splitted[-1]
                for msg in splitted[:-1]:
                    yield json.loads(msg) if return_dict else msg
            
    def close(self):
        if self.sock != None:
            self.sock.close()
        
class KafkaReader(StreamReader):
    """
    Read exported tweets from Kafka queue.

    Parameters
    ----------
    topic
        Topic for the KafkaConsumer
    port
        Port for the KafkaConsumer
    host
        Host for the KafkaConsumer
    """
    def __init__(self, topic, port=9092, host="localhost"):
        self.host = host
        self.port = port
        self.topic = topic
        self.consumer = KafkaConsumer(bootstrap_servers='%s:%i' % (self.host, self.port))
        
    def read(self, return_dict=True, enc="utf-8"):
        for message in consumer:
            msg_bytes = message.value
            msg = msg_bytes.decode(enc)
            yield json.loads(msg) if return_dict else msg
            
    def close(self):
        self.consumer.close()