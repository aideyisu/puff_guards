# puff_guards
the big create for puff

flume配置文档 - puff_guard.conf

----

### Kafka相关操作：

启动Kafka内置Zookeeper与Kafka服务(网上说的教程都是骗人的，啥配置也不用写)

```shell
sudo bin/zookeeper-server-start.sh config/zookeeper.properties

sudo bin/kafka-server-start.sh config/server.properties
```

创建Kafka Topic ，随后使用 --list 指令检查是否成功的创建了对应Topic, 也可以使用delete删除

```shell
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic puff

bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test

bin/kafka-topics.sh --list --zookeeper localhost:2181

bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic puff
```

最后在Kafka自测过程中，我们可以亲自建立生产者与消费者自测

```shell
bin/kafka-console-producer.sh --broker-list localhost:2181 --topic puff

bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic puff --from-beginning
```

----

flume唯一操作：启动flume（此处）

```shell
bin/flume-ng agent \
--name a1 \
--conf conf \
--conf-file conf/flume-conf.properties.template \
-Dflume.root.logger=INFO,console

bin/flume-ng agent \
--name a1 \
--conf conf \
--conf-file conf/kafka.properties \
-Dflume.root.logger=INFO,console
```

----

初次虚拟机中

kafka ： /opt/kafka

flume ： /usr/local2/flume

kafka-python ： /usr/local2/sca (基础的python调用生产者与消费者)

别问为啥目录这么傻吊..我当时就是这么傻吊

------

简易使用:

直接在engine中使用

```shell
python3 puff.py
```

开启后访问

http://127.0.0.1:5000

查看页面即可

进行中 : 
1 防篡改功能前端显示

细节 : 
前端正常显示变化曲线 - 已完成
添加另一个变化曲线 - 待办

待办list :
1 BP神经网络的流量预测
2 爱因斯坦计划-杀伤链 & 攻击树

目前已完成 : 
1 溯源取证
    实现手法:通过存储恶意流量的IP地址,同时开启定位,在交互界面可以显示分布概述.

2 可视化数据监控
    通过echart可以友好的显示在服务器的展示界面中.

3 镜像替身防篡改
    使用哈希检验保证文件完整性,可以实时显示网站文件改动情况,第一时间定位问题
    可以通过图表与数据第一时间得知当前系统情况

