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

    # datetime count
    def sink_intrusion_normal_datetime_count(self):
        #i_n_datetime_count = KafkaConsumer("logv-intrusion-normal-datetime-count",
        #                                   bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            timestamp = time.time()
            redis_connection.zincrby(
                "count-intrusion-datetime", random.randint(1, 20), timestamp)
            redis_connection.zincrby(
                "count-normal-datetime", random.randint(1, 20), timestamp)
            time.sleep(10)

    # Intrusion & normal info
    def sink_intrusion(self):
        #intrusion = KafkaConsumer("logv-intrusion", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        lst = ['1.2.4.8', '8.8.8.8', '114.114.114.114', '139.199.188.178']
        while True:
            json_array = {}
            json_array['host'] = random.choice(lst)
            json_array['data'] = 'intrusion'
            json_array['datetime'] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime())
            redis_connection.publish("intrusion", str(json_array))
            redis_connection.publish("normal", str(json_array))
            time.sleep(10)

    def sink_file_num_change(self):
        #i_n_datetime_count = KafkaConsumer("logv-intrusion-normal-datetime-count",
        #                                   bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            timestamp = time.time()
            redis_connection.zincrby(
                "count-file-add-datetime", random.randint(1, 20), timestamp)
            redis_connection.zincrby(
                "count-file-sub-datetime", random.randint(1, 20), timestamp)
            time.sleep(10)

    def sink_file_size_change(self):
        #datetime = KafkaConsumer("logv-count-datetime", bootstrap_servers=self.kafka_connection)
        redis_connection = redis.Redis(
            host=self.redis_host, port=self.redis_port, db=0)
        while True:
            redis_connection.zincrby(
                "count-file-size-change", random.randint(1, 2000), time.time())
            #print("[SINKER_datetime] " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            time.sleep(10)

    # Multi-threaded runner

    def run(self):
        threads = []

        threads.append(threading.Thread(
            target=self.sink_intrusion_normal_datetime_count))
        threads.append(threading.Thread(target=self.sink_intrusion))
        threads.append(threading.Thread(target=self.sink_file_size_change))
        threads.append(threading.Thread(target=self.sink_file_num_change))
        for i in threads:
            i.start()

