from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:29092'])

for i in range(5):
    future = producer.send('raw_log' , value= b'my_value', partition= 0)
    result = future.get(timeout= 10)
    print(result)

