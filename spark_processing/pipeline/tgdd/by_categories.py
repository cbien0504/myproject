import os, sys 
sys.path.append('/mnt/d/hust/code/thesis')
print(sys.path)
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import current_timestamp, date_format
from spark_processing.pipeline.drop_null_columns import drop_null_columns
from spark_processing.pipeline.flatten_dataframe import flatten_dataframe
from spark_processing.pipeline.upsert_normalized_table import upsert_normalized_table

from delta import *
from spark_processing.pipeline.tgdd.udf import *

def upsert_by_categories(ingest_id):
    builder = SparkSession.builder \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    normalized_daily_table = f"/mnt/d/hust/code/thesis/warehouse/normalized/tgdd/{ingest_id}"
    df = spark.read.format("delta").load(normalized_daily_table).limit(100)
    categories_df = df.select("category").distinct()
    category_list = [row['category'] for row in categories_df.collect()]
    for category in category_list:
        new_df = df.filter(F.col("category") == category)
        new_df = flatten_dataframe(new_df)
        new_df = drop_null_columns(new_df)
        new_df = new_df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
        normalized_table_path = f"/mnt/d/hust/code/thesis/warehouse/categories/tgdd/{category}"
        upsert_normalized_table(spark, new_df, normalized_table_path, 'product_id', 'product_id')
upsert_by_categories('20250301')
