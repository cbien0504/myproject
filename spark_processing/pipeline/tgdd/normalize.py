import os, sys
sys.path.append(os.getcwd())
from delta import *
import pyspark.sql.functions as F
from pyspark.sql.functions import format_number, current_timestamp, date_format
from spark_processing.pipeline.tgdd.udf import *
from spark_processing.pipeline.config_spark_delta import config_spark_delta

def normalize_tgdd(ingest_id):
    spark = config_spark_delta()
    tgdd_daily_path = os.path.join(os.getcwd(), 'data', 'tgdd', ingest_id)
    tgdd_normalized_path = f's3a://warehouse/normalized/tgdd/{ingest_id}'
    df = spark.read.format("json").load(tgdd_daily_path)
    df = df.withColumn("discount_percent", format_number((F.col("price_origin") - F.col("price_present")) / F.col("price_origin") * 100, 2))
    df = df.withColumn('price_origin', F.col('price_origin').cast('double'))
    df = df.withColumn('price_present', F.col('price_present').cast('double'))
    df = df.withColumn('discount', F.col('price_origin') - F.col('price_present'))
    df = df.withColumn('is_sale_off', (F.col('discount') > 0).cast('boolean'))
    df = df.withColumn("brand", to_uppercase(F.col("brand")))
    df = df.withColumn("source", F.lit("tgdd"))
    df = df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
    df = extract_review_column(df)
    df = df.withColumn("reviews_count", F.size(F.coalesce(df["review_author_name"], F.array())))
    df = df.withColumn("reviews", create_list_reviews_udf(*review_column_names))
    df.write.format("delta").save(tgdd_normalized_path)

if __name__ == "__main__":
    ingest_id = sys.argv[1]
    normalize_tgdd(ingest_id)
