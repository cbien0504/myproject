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
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.driver.maxResultSize", "16G") \
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.2.1") \
        .config("spark.jars.repositories", "https://repo1.maven.org/maven2")
    builder = configure_spark_with_delta_pip(builder)
    spark = builder.getOrCreate()
    return spark