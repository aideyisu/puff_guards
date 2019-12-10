# coding : utf-8

import kafka
from pyspark import SParkContext, SParkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, OffsetRange, TopicAndPartition

#
# @project: logv_streaming
# @description: NCSA log structure
# @author: Love's Ys
# @create: 2019-12-xx xx:xx
#

class log:
    host = ''
    rfc = ''
    username = ''
    datetime = ''
    req_method = ''
    req_url = ''
    req_protocol = ''
    statuscode = ''
    bytes = ''
    referrer = ''
    user_agent = ''

#每十秒处理一次数据
