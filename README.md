# 基于大数据的安全态势感知系统

## 项目背景

​	一句话描述 ： 通过Web日志分析，显示网站当前与历史状况

​	整合了web日志聚合、分发、实时分析、入侵检测、数据存储与可视化的日志分析解决方案。聚合采用Apache Flume，分发采用Apache Kafka，实时处理采用Spark Streaming，入侵检测采用Spark MLlib，数据存储使用HDFS与Redis，可视化采用Flask、SocketIO、Echarts、Bootstrap。

## 项目使用

#### 简易使用说明

​	开箱即用，直接在v2目录中使用

```shell
python3 app.py
# 开启后直接访问,即可使用该系统
http://127.0.0.1:5000
```
----

## 相关配置

flume配置文档 - puff_guard.conf

### Kafka相关配置：

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

kafka ： /opt/kafka

flume ： /usr/local2/flume

kafka-python ： /usr/local2/sca (基础的python调用生产者与消费者)

另外需要自己安装好redis等相关组件

上述为各个组件位置

## 当前任务列表

#### 进行中 : 

​	1 神经网络流量预测
​        需要讨论前端流量预测的表现形式

#### ToDo :

​	1 杀伤链 & 攻击树展示
​        计划主要为前端页面显示

#### 已完成 : 

1 溯源取证

​	实现手法:通过存储恶意流量的IP地址,同时开启定位,在交互界面可以显示分布概述.

2 可视化数据监控

​	通过echart可以友好的显示在服务器的展示界面中.

3 文件监控防篡改

​    使用哈希检验保证文件完整性,可以实时显示网站文件改动情况,第一时间定位问题可以通过图表与数据第一时间得知当前系统情况

4 相关功能前端显示

​	通过Echart展示文件数据的历史变化曲线

## 项目界面介绍

#### 欢迎界面

![index](images/index.png)

可以在欢迎界面看到系统时间，以及实时日志流

#### 分析界面

![analysis](images/analysis.png)

![analysis2](images/analysis2.png)

日志分析界面，可以看出历史统计，包括哪些IP高频访问，历史流量规模等等，可以通过此列表判断历史访问请求

#### 地理位置分析

<img src="images/site2.png" alt="site2" style="zoom:50%;" />

![site](images/site.png)

在实时入侵检测界面可以实时分析IP地理位置进行攻击溯源，同时可以显示当时访问日志流，同时对其地理位置进行溯源

#### 文件安全检测

#### ![filesafe](images/filesafe.png)

通过文件安全检测可以看出当前系统总大小，文件数量，最后一次修改时间，各层级文件数量，网络流量日志的大小

#### 文件历史折线图

![filelan](images/filelan.png)

通过文件大小历史折线图，文件数量历史折线图展示网站修改历史

## 系统架构

![arch](images/arch.png)

系统架构图通过由flume底层获取数据联动至flask-socket，前端ECharts数据可视化处理。

从flume获取日志信息，分发给kafka消息队列

#### 数据流

![dataflow](images/dataflow.png)

在项目中通过实时日志生成器，持续生产Web访问日志，通过flume将数据聚合，转送至kafka，在kafka使用spark流处理，进行日志分析，与分类。将分析后的结果传送到缓存redis

最后使用flask-socketio进行异步加载，最终显示到前端echart界面

#### 训练流

![idsflow](images/idsflow.png)

学习过程，通过前期手动标记正常URL数据集，异常URL数据集，进行数据训练

## 数据准备

### 环境准备

我们需要一个伪分布式环境（测试环境为CentOS 7），并完成了所有对应版本组件依赖的配置与运行。
使用`flume`目录下的`standalone.conf`启动一个Flume Agent。
将`datasets`文件夹中的`learning-datasets`提交如下路径：

```
/home/logv/learning-datasets
```

将`datasets`文件夹中的`access_log`提交如下路径：

```
/home/logv/access_log
```

### 入侵检测模型训练与测试

提交`jar`包至Spark集群并执行入侵检测模型的生成与测试：

```shell
spark-submit --class learning logvision.jar
```

![idoutput](images/idoutput.png)

上图为数据样例

## 项目完整运行

特别注意：在开始之前，需要修改源码或配置文件中的IP为**自己的地址**。
								具体涉及到flume配置文件、Spark主程序、Flask Web后端。

### 启动可视化后端

在`flask`目录下执行如下命令，下载依赖包：

```shell
pip3 install -r requirements.txt
```

启动Flask Web：

```shell
python3 app.py
```

### 启动实时日志生成器

`log_gen`中的实时日志生成器可根据传入参数（每次写入行数、写入间隔时间）将样本日志中的特定行块追加至目标日志中，以模拟实时日志的生成过程，供后续实时处理。

```shell
java log_gen [日志源] [目标文件] [每次追加的行数] [时间间隔（秒）]
```

提交至环境，编译并运行，每2秒将`/home/logv/access_log`文件中的5行追加至`/home/logSrc`中：

```shell
javac log_gen.java
java log_gen /home/logv/access_log /home/logSrc 5 2
```

## 结语

有任意意见还希望各位多多指出，还有很多细节需要讨论