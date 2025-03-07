from pyspark.sql import SparkSession
from delta import *

def config_spark_delta():
    builder = SparkSession.builder \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.hadoop.fs.s3a.endpoint", "localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "BAf5vpl6A6hbQyU7l2Tg") \
        .config("spark.hadoop.fs.s3a.secret.key", "SmwuniUvmj25h68WGwA2yYPFELnAKP8ahyM38q6y") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .config("spark.driver.maxResultSize", "16G") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.jars", "dependencies/jars/aws-java-sdk-core-1.12.150.jar,dependencies/jars/aws-java-sdk-dynamodb-1.12.187.jar,dependencies/jars/aws-java-sdk-s3-1.12.150.jar,dependencies/jars/hadoop-aws-3.2.1.jar") \
        .config("spark.jars.repositories","https://repo1.maven.org/maven2")
    builder = configure_spark_with_delta_pip(builder)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark
spark = config_spark_delta()
data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
columns = ["name", "age"]
df = spark.createDataFrame(data, columns)
df.show()
df.write.mode("overwrite").csv("s3a://data/data.csv")