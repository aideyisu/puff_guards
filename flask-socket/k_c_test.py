from kafka import KafkaConsumer

consumer = KafkaConsumer('raw_log', bootstrap_servers= ['localhost:29092'])

cache = ""
for msg in consumer:
    cache += str(msg.value)
    print(f'当前接收了 {cache}')


'''
https://zhuanlan.zhihu.com/p/38330574

'''