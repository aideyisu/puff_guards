
# coding=utf-8
import ast
import time
from kafka import KafkaConsumer # pip3 install kafka-python
import random
import redis
import requests
import os

# 内部调用
# import ai # 训练模型,用不到
import controller
import File_security

from threading import Lock, Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

# 配置项目
# time_interval = 1
time_interval = 10
# kafka_bootstrap_servers = "10.0.0.222:9092"
kafka_bootstrap_servers = "127.0.0.1:29092" # 定制kafka
redis_con_pool = redis.ConnectionPool(
    host='127.0.0.1', port=6379, decode_responses=True)


# 页面路由与对应页面的ws接口
# 系统时间
@socketio.on('connect', namespace='/sys_time')
def sys_time():
    def loop():
        redis_connection = redis.Redis(connection_pool=redis_con_pool)
        while True:
            socketio.sleep(time_interval)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            socketio.emit('sys_time',
                          {'data': current_time},
                          namespace='/sys_time')

    socketio.start_background_task(target=loop)


# 欢迎页面
@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('index.html', async_mode=socketio.async_mode)

def get_log(start_line, end_line):
    basepath = os.path.dirname(__file__)  # 当前文件所在路径
    data_path = f'{basepath[:-13]}\datasets\\access_log'

    result = []
    with open(data_path, "r") as file:
        all_line = file.readlines()
        result = all_line[start_line : end_line]
        for item in range(len(result)):
            result[item] = (bytes(result[item], 'ascii'))
    
    return result

# 实时日志流
@socketio.on('connect', namespace='/log_stream')
def log_stream():
    start_site = 0
    def loop():
        socketio.sleep(time_interval)
        # 每次消费全部数据
        consumer = KafkaConsumer("raw_log", bootstrap_servers=kafka_bootstrap_servers, auto_offset_reset='earliest')
        
        # consumer = [] # 准备读取日志信息并动态加载进来
        
        # consumer = [b'211.94.114.14 - - [21/Nov/2017:10:44:54 + 0800] "GET /HTTP/1.1" 200 65814',
        #             b'211.94.114.15 - - [21/Nov/2017:10:44:53 + 0800] "GET /HTTP/1.1" 200 51579',]
        
        # consumer = [b'211.94.114.14 - - [21/Nov/2017:10:44:54 + 0800] "GET /HTTP/1.1" 200 65814',
        #             b'211.94.114.15 - - [21/Nov/2017:10:44:53 + 0800] "GET /HTTP/1.1" 200 51579',
        #             b'211.94.114.16 - - [21/Nov/2017:10:44:52 +0800] "GET /scripts/search.jsp?q=%"<script>alert(1332010391)</script> HTTP/1.1" 251580',
        #             b'211.94.114.17 - - [21/Nov/2017:10:44:52 +0800] "GET /scripts/search.jsp?q=%"<script>alert(1332010391)</script> HTTP/1.1" 251580']
        
        # consumer = get_log(start_site, start_site + 3) # 暴力获取日志

        cache = ""
        for msg in consumer:
            # print(msg.value)
            # cache += bytes.decode(msg.value) 
            # cache += bytes.decode(msg) 
            # cache += bytes.decode(msg) + "\n"
            cache += bytes.decode(msg.value) + "\n"
            K = len(cache.split("\n"))
            print(msg.value)
            print(f'当前长度 {K}')
            print(cache)
            if len(cache.split("\n")) > 3:
                socketio.emit('log_stream',
                              {'data': cache},
                              namespace='/log_stream')
                cache = ""

    socketio.start_background_task(target=loop)


# 实时日志分析页面
@app.route('/analysis')
def analysis():
    return render_template('analysis.html', async_mode=socketio.async_mode)


# 实时计数器
@socketio.on('connect', namespace='/count_board')
def count_board():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrange("statcode", 0, 40, withscores=True)

            # 总请求数（日志行数）
            host_count = redis_con.zscore("line", "count")

            # 成功请求数（状态码属于normal的个数）
            normal = ["200", "201", "202", "203", "204", "205", "206", "207"]
            success_count = 0
            for i in res:
                if i[0] in normal:
                    success_count += int(i[1])

            # 其他请求数（其他状态码个数）
            other_count = 0
            for i in res:
                other_count += int(i[1])
            other_count -= success_count

            # 访客数（不同的IP个数）
            visitor_count = redis_con.zcard("host")

            # 资源数（不同的url个数）
            url_count = redis_con.zcard("url")

            # 流量大小（bytes的和，MB）
            if redis_con.zscore("traffic", "sum"):
                traffic_sum = int(redis_con.zscore("traffic", "sum"))
            else:
                traffic_sum = 123

            # 日志大小（MB）
            if (redis_con.zscore("size", "sum")):
                log_size = int(redis_con.zscore("size", "sum"))
            else:
                log_size = 1234
            socketio.emit('count_board',
                          {'host_count': host_count,
                           'success_count': success_count,
                           'other_count': other_count,
                           'visitor_count': visitor_count,
                           'url_count': url_count,
                           'traffic_sum': traffic_sum,
                           'log_size': log_size},
                          namespace='/count_board')

    socketio.start_background_task(target=loop)


# 实时热门位置
@socketio.on('connect', namespace='/hot_geo')
def hot_geo():
    def loop():
        while True:
            socketio.sleep(2)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("host", 0, 50, withscores=True)
            data = []
            res = ['1.2.4.8', '8.8.8.8', '114.114.114.114', '139.199.188.178']
            for i in res:
                # 调用接口获取地理坐标
                req = requests.get("http://api.map.baidu.com/location/ip",
                                   {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                    'ip': i,
                                    'coor': 'bd09ll'})
                body = eval(req.text)

                # 仅显示境内定位
                if body['status'] == 0:
                    coor_x = body['content']['point']['x']
                    coor_y = body['content']['point']['y']

                    data.append(
                        {"name": i[0], "value": [coor_x, coor_y, i[1]]})

            socketio.emit('hot_geo',
                          {'data': data},
                          namespace='/hot_geo')

    socketio.start_background_task(target=loop)


# 实时热门资源排名
@socketio.on('connect', namespace='/hot_url')
def hot_url():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("url", 0, 9, withscores=True)
            data = []
            no = 1

            res = [["/", 40297], ["*", 2553]]

            for i in res:
                data.append({"no": no, "url": i[0], "count": i[1]})
                no += 1

            socketio.emit('hot_url',
                          {'data': data},
                          namespace='/hot_url')

    socketio.start_background_task(target=loop)


# 实时热门IP排名
@socketio.on('connect', namespace='/hot_ip')
def hot_ip():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("host", 0, 13, withscores=True)
            data = []
            no = 1

            res = ['1.2.4.8', '8.8.8.8', '114.114.114.114', '139.199.188.178']
            for i in res:
                # 调用接口获取地理坐标
                req = requests.get("http://api.map.baidu.com/location/ip",
                                   {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                    'ip': i,
                                    'coor': 'bd09ll'})
                body = eval(req.text)

                # 仅显示境内定位
                if body['status'] == 0:
                    address = body['content']['address']

                    data.append(
                        {"no": no, "ip": i[0], "address": address, "count": i[1]})
                    no += 1

            socketio.emit('hot_ip',
                          {'data': data},
                          namespace='/hot_ip')

    socketio.start_background_task(target=loop)


# 实时状态码比例
@socketio.on('connect', namespace='/status_code_pie')
def status_code_pie():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("statcode", 0, 100, withscores=True)
            data = []
            legend = []

            res = [['200', 201], ['404', 405], [
                '405', 406], ['202', 203], ['304', 305]]

            for i in res:
                if i[0] != 'foo':
                    data.append({"value": i[1], "name": i[0]})
                    legend.append(i[0])

            socketio.emit('status_code_pie',
                          {'legend': legend, 'data': data},
                          namespace='/status_code_pie')

    socketio.start_background_task(target=loop)


# 实时请求方式比例
@socketio.on('connect', namespace='/req_method_pie')
def req_method_pie():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("reqmt", 0, 100, withscores=True)
            data = []
            legend = []

            res = [['GET', 201], ['POST', 405], [
                'OPTIONS', 406], ['-', 203], ['HEAD', 305]]

            for i in res:
                if i[0] != 'foo':
                    data.append({"value": i[1], "name": i[0]})
                    legend.append(i[0])

            socketio.emit('req_method_pie',
                          {'legend': legend, 'data': data},
                          namespace='/req_method_pie')

    socketio.start_background_task(target=loop)


# 实时请求计数（按时间顺序）
@socketio.on('connect', namespace='/req_count_timeline')
def req_count_timeline():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = dict(redis_con.zrange(
                "datetime", 0, 10000000, withscores=True))
            data = []
            date = []

            res = [time.time(), time.time()]
            # 按时间排序
            for i in sorted(res):
                datetime = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(int(i) / 1000))
                data.append(1000)
                date.append(datetime)

            socketio.emit('req_count_timeline',
                          {"data": data, "date": date},
                          namespace='/req_count_timeline')

    socketio.start_background_task(target=loop)


# IP请求数排序
@socketio.on('connect', namespace='/ip_ranking')
def timestamp_count_timeline():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            res = redis_con.zrevrange("host", 0, 50, withscores=True)
            ip = []
            count = []

            res = [['1.2.3.4', 1000], ['8.8.8.8', 888],
                   ['114.114.114.114', 1144]]

            for i in res:
                ip.append(i[0])
                count.append(i[1])

            socketio.emit('ip_ranking',
                          {"ip": ip, "count": count},
                          namespace='/ip_ranking')

    socketio.start_background_task(target=loop)


@app.route('/id')
def id():
    return render_template("id.html", async_mode=socketio.async_mode)


# 异常请求计数
@socketio.on('connect', namespace='/bad_count')
def bad_count():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            if redis_con.zscore("bad", "bad"):
                res = int(redis_con.zscore("bad", "bad"))
            else:
                res = 99999

            socketio.emit('bad_count',
                          {"data": res},
                          namespace='/bad_count')

    socketio.start_background_task(target=loop)


# 正常请求计数
@socketio.on('connect', namespace='/good_count')
def bad_count():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            if redis_con.zscore("good", "good"):
                res = int(redis_con.zscore("good", "good"))
            else:
                res = 11111

            socketio.emit('good_count',
                          {"data": res},
                          namespace='/good_count')

    socketio.start_background_task(target=loop)


# 正常请求地理标记
@socketio.on('connect', namespace='/good_geo')
def good_geo():
    def loop():
        while True:
            socketio.sleep(time_interval)
            # consumer = KafkaConsumer(
            #     "good_result", bootstrap_servers=kafka_bootstrap_servers)
            consumer = [[{'host': '1.2.4.8', 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.1.com', 'timestamp': time.time(
            )}, {'host': '139.199.188.178', 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.2.com', 'timestamp': time.time()}]]

            data = []

            for msg in consumer:
                # result = ast.literal_eval(bytes.decode(msg.value))
                result = msg
                for record in result:
                    if record['host'] != "foo":
                        # 调用接口获取地理坐标
                        req = requests.get("http://api.map.baidu.com/location/ip",
                                           {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                            'ip': record['host'],
                                            'coor': 'bd09ll'})
                        body = eval(req.text)
                        # 仅显示境内定位
                        if body['status'] == 0:
                            coor_x = body['content']['point']['x']
                            coor_y = body['content']['point']['y']
                            datetime = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(int(record['timestamp']) / 1000))

                            data.append({"name": record['host'], "value": [coor_x, coor_y,
                                                                           record['url'],
                                                                           datetime,
                                                                           record['req_method'],
                                                                           record['protocol'],
                                                                           record['status_code']]})
                            socketio.emit('good_geo',
                                          {"data": data},
                                          namespace='/good_geo')

    socketio.start_background_task(target=loop)


# 异常请求地理标记
@socketio.on('connect', namespace='/bad_geo')
def bad_geo():
    def loop():
        while True:
            socketio.sleep(time_interval)
            # consumer = KafkaConsumer(
            #     "bad_result", bootstrap_servers=kafka_bootstrap_servers)
            consumer = [[{'host': '1.2.4.8', 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.1.com', 'timestamp': time.time(
            )}, {'host': '139.199.188.178', 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.2.com', 'timestamp': time.time()}]]

            data = []

            for msg in consumer:
                result = msg
                # result = ast.literal_eval(bytes.decode(msg))
                for record in result:
                    if record['host'] != "foo":
                        # 调用接口获取地理坐标
                        req = requests.get("http://api.map.baidu.com/location/ip",
                                           {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                            'ip': record['host'],
                                            'coor': 'bd09ll'})
                        body = eval(req.text)
                        # 仅显示境内定位
                        if body['status'] == 0:
                            coor_x = body['content']['point']['x']
                            coor_y = body['content']['point']['y']
                            datetime = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(int(record['timestamp']) / 1000))

                            data.append({"name": record['host'], "value": [coor_x, coor_y,
                                                                           record['url'],
                                                                           datetime,
                                                                           record['req_method'],
                                                                           record['protocol'],
                                                                           record['status_code']]})
                            socketio.emit('bad_geo',
                                          {"data": data},
                                          namespace='/bad_geo')

    socketio.start_background_task(target=loop)


# 实时入侵分类计数（按时间顺序）
@socketio.on('connect', namespace='/url_cate_count_timeline')
def url_cate_count_timeline():
    def loop():
        while True:
            socketio.sleep(time_interval)
            redis_con = redis.Redis(connection_pool=redis_con_pool)
            good_res = dict(redis_con.zrange(
                "goodts", 0, 10000000, withscores=True))
            bad_res = dict(redis_con.zrange(
                "badts", 0, 10000000, withscores=True))

            good_res = [time.time(), time.time()]
            bad_res = [time.time(), time.time()]
            # 求正常和异常结果的时间戳的并集，并排序。再生成对应的正常和异常计数
            date = []
            date_ts = []
            good_date = []
            bad_date = []

            good_data = []
            bad_data = []
            # 求并集并排序
            for i in good_res:
                good_date.append(i)
            for j in bad_res:
                bad_date.append(j)
            for k in sorted(list(set(good_date) | set(bad_date))):
                date_ts.append(k)

            # 生成对应的计数
            for t in date_ts:
                if t in good_res:
                    # good_data.append(good_res[t])
                    good_data.append(t)
                else:
                    good_data.append(0)
                if t in bad_res:
                    # bad_data.append(bad_res[t])
                    bad_data.append(t)
                else:
                    bad_data.append(0)
            # 时间戳转字符串
            for ts in date_ts:
                date.append(time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.localtime(int(ts) / 1000)))

            socketio.emit('url_cate_count_timeline',
                          {"date": date, "good_data": good_data,
                              "bad_data": bad_data},
                          namespace='/url_cate_count_timeline')

    socketio.start_background_task(target=loop)


# 实时异常请求概览
@socketio.on('connect', namespace='/bad_detail')
def bad_detail():
    def loop():
        k = 0
        while True:
            socketio.sleep(time_interval)
            # consumer = KafkaConsumer(
            #     "bad_result", bootstrap_servers=kafka_bootstrap_servers)
            if k == 0:
                consumer = [[{'host': '1.2.4.8', 'prediction': '大好人', 'probability': 80,  'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.1.com', 'timestamp': time.time(
                )}, {'host': '139.199.188.178', 'prediction': '小好人', 'probability': 90, 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.2.com', 'timestamp': time.time()}]]

            else:
                consumer = [[]]
            data = []

            for msg in consumer:
                result = msg
                # result = ast.literal_eval(bytes.decode(msg.value))
                break
                for record in result:
                    if record['host'] != "foo":
                        # 调用接口获取地理坐标
                        req = requests.get("http://api.map.baidu.com/location/ip",
                                           {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                            'ip': record['host'],
                                            'coor': 'bd09ll'})
                        body = eval(req.text)
                        # 仅显示境内定位
                        if body['status'] == 0:
                            address = body['content']['address']

                            datetime = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(int(record['timestamp']) / 1000))

                            data.append({"host": record['host'], "address": address, "url": record['url'],
                                         "datetime": datetime, "req_method": record['req_method'],
                                         "protocol": record['protocol'], "status_code": record['status_code'],
                                         "pred": record['prediction'], 'prob': record['probability']})
                            print(k, (data))
                            socketio.emit('bad_detail',
                                          {"data": [
                                              item for item in data if data.count(item) == 1]},
                                          namespace='/bad_detail')
    socketio.start_background_task(target=loop)


# 实时正常请求概览
@socketio.on('connect', namespace='/good_detail')
def good_detail():
    def loop():
        k = 1
        while True:
            socketio.sleep(time_interval)
            # consumer = KafkaConsumer(
            #     "good_result", bootstrap_servers=kafka_bootstrap_servers)
            if k == 0:
                consumer = [[{'host': '1.2.4.8', 'prediction': '大坏蛋', 'probability': 80,  'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.1.com', 'timestamp': time.time(
                )}, {'host': '139.199.188.178', 'prediction': '小坏蛋', 'probability': 90, 'status_code': 200, 'protocol': 'HTTP', 'req_method': 'GET', 'url': 'www.2.com', 'timestamp': time.time()}]]

            else:
                consumer = [[]]
            data = []

            for msg in consumer:
                result = msg

                break
                # result = ast.literal_eval(bytes.decode(msg.value))
                for record in result:
                    if record['host'] != "foo":
                        # 调用接口获取地理坐标
                        req = requests.get("http://api.map.baidu.com/location/ip",
                                           {'ak': 'RNeT2wMdQiyB2lssimPBW9N2jdIL6jBt',
                                            'ip': record['host'],
                                            'coor': 'bd09ll'})
                        body = eval(req.text)
                        # 仅显示境内定位
                        if body['status'] == 0:
                            address = body['content']['address']

                            datetime = time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(int(record['timestamp']) / 1000))

                            data.append({"host": record['host'], "address": address, "url": record['url'],
                                         "datetime": datetime, "req_method": record['req_method'],
                                         "protocol": record['protocol'], "status_code": record['status_code'],
                                         "pred": record['prediction'], 'prob': record['probability']})

                            socketio.emit('good_detail',
                                          {"data": [
                                              item for item in data if data.count(item) == 1]},
                                          namespace='/good_detail')
    socketio.start_background_task(target=loop)


def background_thread():
    #sinker = controller.Sinker("192.168.83.33:9092", "192.168.83.33:9092", 6379).run()
    # sinker = controller.Sinker("127.0.0.1", 6379).run()
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        # Get data from Redis
        # Counting board & redis data entry - sorted set
        redis_connection = redis.Redis(host="127.0.0.1", port=6379, db=0)

        intrusion_datetime_count_raw = redis_connection.zrange(
            "count-intrusion-datetime", 0, -1, withscores=True)
        normal_datetime_count_raw = redis_connection.zrange(
            "count-normal-datetime", 0, -1, withscores=True)

        add_file_datetime_count_raw = redis_connection.zrange(
            "count-file-add-datetime", 0, -1, withscores=True)
        sub_file_datetime_count_raw = redis_connection.zrange(
            "count-file-sub-datetime", 0, -1, withscores=True)
        # Intrusion & Normal datetime statistics
        intrusion_container = {}
        normal_container = {}
        i_n_intrusion_count = []
        i_n_normal_count = []
        i_n_datetime_sorted = []
        for i in intrusion_datetime_count_raw:
            intrusion_container.update({bytes.decode(i[0]): int(i[1])})
        for i in normal_datetime_count_raw:
            normal_container.update({bytes.decode(i[0]): int(i[1])})

        for i in sorted(intrusion_container):
            # Or normal_container, they're all the same.
            i_n_intrusion_count.append(intrusion_container[i])
            i_n_normal_count.append(normal_container[i])
            i_n_datetime_sorted.append(time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(int(float(i)))))

        # Intrusion & Normal datetime statistics
        file_add_container = {}
        file_sub_container = {}
        file_add_count = []
        file_sub_count = []
        file_datetime_add_sub_sorted = []
        for i in add_file_datetime_count_raw:
            file_add_container.update({bytes.decode(i[0]): int(i[1])})
        for i in sub_file_datetime_count_raw:
            file_sub_container.update({bytes.decode(i[0]): int(i[1])})

        for i in sorted(file_add_container):
            # Or file_sub_container, they're all the same.
            file_add_count.append(file_add_container[i])
            file_sub_count.append(file_sub_container[i])
            file_datetime_add_sub_sorted.append(time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(int(float(i)))))

        # SocketIO emitting
        socketio.emit('FileSecurity',
                      {'file_add_count': file_add_count,
                       'file_sub_count': file_sub_count,
                       'file_datetime_add_sub_sorted': file_datetime_add_sub_sorted,
                       'i_n_datetime_sorted': i_n_datetime_sorted,
                       'i_n_intrusion_count': i_n_intrusion_count,
                       'i_n_normal_count': i_n_normal_count}, namespace='/FileSecurity')


@socketio.on('connect', namespace='/FileSecurity')
def FileSecurity():
    global thread
    with thread_lock:
        if thread is None:
            socketio.start_background_task(target=background_thread)


@app.route('/file_security')
def file_security():
    content = File_security.read_safe_content()
    return render_template('file_security.html', num=content['file_num'],
                           size=content['file_size'], file_list=content['file_list'],
                           last_modify_time=content['last_modify_time'],
                           first=len(content['first']), second=len(content['second']), other=len(content['other']),
                           async_mode=socketio.async_mode)


@app.route('/about')
def about():
    return render_template("about.html", async_mode=socketio.async_mode)


if __name__ == '__main__':
    File_security.set_safe_content() # 设置文件安全状态
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
