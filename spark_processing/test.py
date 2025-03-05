from pyspark.sql import SparkSession
from pyspark.sql import Row
spark = SparkSession.builder.master('local') \
    .appName("SimpleSparkExample") \
    .getOrCreate()
data = [
    Row(name="Alice", age=34),
    Row(name="Bob", age=45),
    Row(name="Catherine", age=29)
]
df = spark.createDataFrame(data)
df.show()
output_directory = "/app/spark_processing/output_test"
df.write.format("json").mode("overwrite").save(output_directory)
spark.stop()