from pyspark.sql.functions import format_number, udf, current_timestamp, date_format, expr
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, StringType
from merge_schema import merge_schema
from delta import *
from pyspark.sql import SparkSession
from delta.tables import DeltaTable
from config_spark_delta import config_spark_delta
from create_table_from_schema import create_table_from_schema

def to_uppercase(arr):
    if arr is not None:
        return [x.upper() if x is not None else None for x in arr]
    return None
uppercase_udf = udf(to_uppercase, ArrayType(StringType()))

def normalize_tgdd(ingest_id):
    spark = config_spark_delta()
    df = spark.read.format("json").load(f"/mnt/d/hust/code/thesis/warehouse/daily/tgdd/{ingest_id}/*.json")
    df = df.select("product_id", "product_name", "category", "url", "brand", "description", "price", "price_origin", "price_present", "crawled_at", "updated_at")
    df = df.withColumn("discount_percent", format_number((F.col("price_origin") - F.col("price_present")) / F.col("price_origin") * 100, 2))
    df = df.withColumn('price_origin', F.col('price_origin').cast('double'))
    df = df.withColumn('price_present', F.col('price_present').cast('double'))
    df = df.withColumn('discount', F.col('price_origin') - F.col('price_present'))
    df = df.withColumn('is_sale_off', (F.col('discount') > 0).cast('boolean'))
    df = df.withColumn("brand", uppercase_udf(F.col("brand")))
    df = df.withColumn("source", F.lit("tgdd"))
    df = df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
    normalized_table_path = f"/mnt/d/hust/code/thesis/warehouse/normalized/tgdd"
    table = create_table_from_schema(spark, df, normalized_table_path)
    merge_schema(spark, table, df)
    table = DeltaTable.forPath(spark, normalized_table_path)
    table_df = table.toDF()
    missing_cols = set(table_df.columns) - set(df.columns)
    df = df.withColumns({x: F.lit(None) for x in missing_cols})
    cols = {}
    for col in table_df.columns:
        if col == "created_at":
            continue
        cols[col] = F.when(df[col].isNotNull(), df[col]).otherwise(table_df[col])
    table.merge(
        df, table_df["product_id"] == df["product_id"]
    ).whenNotMatchedInsertAll().whenMatchedUpdate(
        set=cols,
    ).execute()
normalize_tgdd("20250225")
def upsert_master_from_tgdd(
    normalized_table_path: str,
    master_table_path: str,
):
    column_mapping = {
    "product_id": "src.product_id",
    "product_name": "src.product_name",
    "category": "src.category",
    "url": "src.url",
    "brand": "src.brand",
    "description": "src.description",
    "price": "src.price",
    "price_origin": "src.price_origin",
    "price_present": "src.price_present",
    "crawled_at": "src.crawled_at",
    "updated_at": "src.updated_at",
    "discount_percent": "src.discount_percent",
    "discount": "src.discount",
    "is_sale_off": "src.is_sale_off",
    "source": "src.source",
    }
    spark = config_spark_delta()
    normalized_df = spark.read.format("delta").load(normalized_table_path)
    normalized_df = normalized_df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
    table = create_table_from_schema(spark, normalized_df, master_table_path)
    merge_schema(spark, table, normalized_df)
    master_table = DeltaTable.forPath(spark, master_table_path)
    master_table.alias("dest").merge(
        normalized_df.alias("src"), "dest.product_id = src.product_id"
    ).whenMatchedUpdate(set=column_mapping).whenNotMatchedInsert(values=column_mapping).execute()
    master_table = master_table.toDF()
    master_columns = [col.name for col in master_table.schema.fields]
    if "uuid" not in master_columns:
        master_table = master_table.withColumn("uuid", F.lit(None).cast("string"))
    master_table = master_table.withColumn(
    "uuid", 
    expr("CASE WHEN uuid IS NULL THEN uuid() ELSE uuid END")
    )
    master_table.write.mode("overwrite").option("overwriteSchema", "true").format("delta").save(master_table_path)
upsert_master_from_tgdd(
    normalized_table_path = "/mnt/d/hust/code/thesis/warehouse/normalized/tgdd", 
    master_table_path = "/mnt/d/hust/code/thesis/warehouse/master"
    )
