# coding - utf-8
import redis
import threading
import random
import time
import json


# kafka_connection redis_host, redis_port: "192.168.31.100:9092", "192.168.31.100", 63790

# Sink data from Kafka to Redis
class Sinker:
    def __init__(self, redis_host, redis_port):
        self.redis_host = redis_host
        self.redis_port = redis_port

    # For counting board and others

    def sink_total_reqs(self):
        #host = KafkaConsumer("logv-count-host", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            time.sleep(5)
            # Total reqs
            redis_connection.zincrby(
                "count-total-host", float(random.randint(1, 100)), "total-req")
            #print("[SINKER_total_reqs] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_visitor(self):
        #host = KafkaConsumer("logv-count-host", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = ['AA', 'BB', 'CC']
        while True:
            time.sleep(5)
            redis_connection.zincrby(
                "count-host", float(random.randint(1, 10)), random.choice(lst))
            #print("[SINKER_visitor] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_reqs(self):
        #statuscode = KafkaConsumer("logv-count-statuscode", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = ['200', '404', '405', '202', '304']
        while True:  # Valid reqs & not-found reqs
            time.sleep(5)
            redis_connection.zincrby(
                "count-statuscode", random.randint(1, 10), random.choice(lst))
            #print("[SINKER_reqs] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_traffic(self):
        #byte_s = KafkaConsumer("logv-count-bytes", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:  # Traffic
            time.sleep(5)
            redis_connection.zincrby(
                "count-bytes", float(random.randint(1, 10)*1024), "traffic")
            #print("[SINKER_traffic] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_log_size(self):
        #char = KafkaConsumer("logv-count-char", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:  # Log size
            time.sleep(5)
            redis_connection.zincrby(
                "count-char", float(random.randint(10, 25)*1024), "log-size")
            #print("[SINKER_log_size] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_req_method(self):
        #req_method = KafkaConsumer("logv-count-req_method", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = [b'web', b'mobile', b'local', b'others']
        while True:  # Req method count
            time.sleep(5)
            redis_connection.zincrby(
                "count-req-method", float(random.randint(1, 10)), random.choice(lst))
            #print("[SINKER_req_method] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_req_url(self):
        #req_url = KafkaConsumer("logv-count-req_url", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = [b'1.2.4.8', b'139.199.188.178', b'8.8.8.8', b'114.114.114.114']
        while True:
            time.sleep(5)
            redis_connection.zincrby(
                "count-req-url", float(random.randint(1, 20)), random.choice(lst))
            #print("[SINKER_req_url] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_datetime(self):
        #datetime = KafkaConsumer("logv-count-datetime", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = [b'time1', b'time2']
        while True:
            time.sleep(5)
            redis_connection.zincrby(
                "count-datetime", random.randint(1, 20), time.time())
            #print("[SINKER_datetime] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # Datetime formatting (for pattern like: 22/Nov/2018:06:54:33 -> 22/11/2018:06:54:33 -> TIMESTAMP)
    def datetime_converter(self, datetime):
        day = datetime.split(" ")[0].split("/")[0]
        month = datetime.split(" ")[0].split("/")[1]
        rest = datetime.split(" ")[0].split("/")[2]
        mapping = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                   "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        int_datetime = "/".join([str(day), str(mapping[month]), str(rest)])
        # timestamp
        return int(time.mktime(time.strptime(int_datetime, "%d/%m/%Y:%H:%M:%S")))

    # For 'Malicious' board
    # raw count
    def sink_intrusion_count(self):
        #intrusion = KafkaConsumer("logv-intrusion-count", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            time.sleep(5)
            redis_connection.zincrby(
                "count-intrusion", float(random.randint(1, 10)), "intrusion-count")
            #print("[SINKER_intrusion_count] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def sink_normal_count(self):
        #normal = KafkaConsumer("logv-normal-count", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            time.sleep(5)
            redis_connection.zincrby(
                "count-normal", float(random.randint(1, 10)), "normal-count")
            #print("[SINKER_normal_count] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    # datetime count
    def sink_intrusion_normal_datetime_count(self):
        #i_n_datetime_count = KafkaConsumer("logv-intrusion-normal-datetime-count",
        #                                   bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            time.sleep(5)
            timestamp = time.time()
            redis_connection.zincrby(
                "count-intrusion-datetime", random.randint(1, 20), timestamp)
            redis_connection.zincrby(
                "count-normal-datetime", random.randint(1, 20), timestamp)

    # Intrusion & normal info
    def sink_intrusion(self):
        #intrusion = KafkaConsumer("logv-intrusion", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = ['1.2.4.8', '8.8.8.8', '114.114.114.114', '139.199.188.178']
        while True:
            time.sleep(5)
            json_array = {}
            json_array['host'] = random.choice(lst)
            json_array['data'] = 'intrusion'
            json_array['datetime'] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())
            redis_connection.publish("intrusion", str(json_array))
            redis_connection.publish("normal", str(json_array))

    # Multi-threaded runner

    def run(self):
        threads = []
        threads.append(threading.Thread(target=self.sink_total_reqs))
        threads.append(threading.Thread(target=self.sink_visitor))
        threads.append(threading.Thread(target=self.sink_reqs))
        threads.append(threading.Thread(target=self.sink_traffic))
        threads.append(threading.Thread(target=self.sink_log_size))
        threads.append(threading.Thread(target=self.sink_req_method))
        threads.append(threading.Thread(target=self.sink_req_url))
        threads.append(threading.Thread(target=self.sink_datetime))
        threads.append(threading.Thread(target=self.sink_intrusion_count))
        threads.append(threading.Thread(target=self.sink_normal_count))
        threads.append(threading.Thread(
            target=self.sink_intrusion_normal_datetime_count))
        threads.append(threading.Thread(target=self.sink_intrusion))
        for i in threads:
            i.start()
