import sys, os
sys.path.append(os.getcwd())
from delta import *
from pyspark.sql.functions import current_timestamp, date_format
from spark_processing.pipeline.tgdd.udf import *
from spark_processing.pipeline.config_spark_delta import config_spark_delta
from spark_processing.pipeline.upsert_normalized_table import upsert_normalized_table

def save_common_normalize(ingest_id):
    spark = config_spark_delta()
    df = spark.read.format("delta").load(f'warehouse/normalized/tgdd/{ingest_id}')
    df = df.select("product_id", "product_name", "category", "url", "brand", "description", "price", "price_origin", "price_present", "crawled_at", "updated_at",
            'discount_percent', 'discount', 'is_sale_off', 'source',
            'review_author_name', 'review_date', 'review_description', 'review_body', 'review_best_rating', 'review_rating_value', 'review_image', 'reviews_count')
    df = df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
    common_normalized_path = "warehouse/common_normalized/tgdd"
    upsert_normalized_table(spark, df, common_normalized_path, 'product_id', 'product_id')
if __name__ == "__main__":
    ingest_id = sys.argv[1]
    save_common_normalize(ingest_id)