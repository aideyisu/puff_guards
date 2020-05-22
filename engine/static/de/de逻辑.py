from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('log_reg').getOrCreate()

#读取测试数据
df = spark.read.csv('xxx.csv', inferSchema=True, header=True)

from pyspark.sql.functions import * 

# 1 查看数据情况，检测数据治疗和相关特征，以便对数据有一定认识
# 查看数据规模，全景统计

print((df.count(), len(df.columns())))
#查看数据规模，假定输出为 20000, 6 表示表有 2W行数据，6列

df.printSchema() #查看数据结构

df.cloumns # 查看列名

df.describe().show()
#全景数据分享统计，会对各列按照平均值, 方差， 最小值, 最大值，函数统计 这几个统计量来进行统计

#统计信息，使用API时候调用，使用SPark Sql可以达到相同效果

df.groupBy('Country').count().show()

df.groupBy('Platform').count().show()

df.groupBy('Status').count().show()

# 2 进行数据转换，主要将类别数据，转化为可以通过数据来度量，包括字符串

from pyspark.ml.feature import StringIndexer
#可以吧字符串的列按照出现频率排序，出现次数最高的Index为0

# 2.1 将字符串转换
search_engine_indexer = StringIndexer(inputCol="Platform", outputCol="Search_Engine_Num").fit(df)
# 返回对应模型
df = search_engine_indexer.transform(df) # 输入饿dataset进行模型转换，返回经过转换后的dataset

df.show(5, False)

# 2.2 进行独热编码？？？
from pyspark.ml.feature import OneHotEncode # 它可以实现将分类特征每个元素转化为一个可以用来计算的值