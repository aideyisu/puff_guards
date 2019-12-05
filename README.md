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
别问为啥目录这么傻吊..我当时就是这么傻吊