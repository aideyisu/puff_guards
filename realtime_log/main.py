mport random
import linecache #读取文件并缓存文件中的所有文本
import time

'''
此脚本可以从stock.log,随机读取随机条数的日志，并添加至src.log
与日志同目录下创建log_repo文件并创建stock.log生成日志向 src.log写文件
'''

stock_log_path = "../puff/stock.log"
target_log_path = "../puff/src.log"

stock_log = linecache.getlines(stock_log_path)

sleep_time = 1
maximum_items = 10

while True:
    target_log = open(target_log_path, 'a+')
    print(len(stock_log))
    start = random.randint(1, len(stock_log))
    end = start + random.randint(1, maximum_items)
    if end > len(stock_log):
        start = random.randint(1, len(stock_log))
        end = start + random.randint(1, maximum_items)
    clip = stock_log[start:end]
    for i in clip:
        target_log.write(i)
    print("[Puff] Appended " + str(len(clip)) + " record(s).")
    target_log.close()
    time.sleep(sleep_time)
