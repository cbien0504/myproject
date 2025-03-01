from delta import *
from delta.tables import DeltaTable
import pyspark.sql.functions as F
from pyspark.sql.functions import current_timestamp, date_format, expr
from spark_processing.pipeline.tgdd.udf import *
from spark_processing.pipeline.merge_schema import merge_schema
from spark_processing.pipeline.config_spark_delta import config_spark_delta
from spark_processing.pipeline.create_table_from_schema import create_table_from_schema
from spark_processing.pipeline.mapping_master import *

def upsert_master(
    normalized_table_path: str,
    master_table_path: str,
    column_mapping: dict,
    df_key: str,
    master_key: str
):
    spark = config_spark_delta()
    normalized_df = spark.read.format("delta").load(normalized_table_path)
    normalized_df = normalized_df.withColumn("updated_at", date_format(current_timestamp(), 'yyyy-MM-dd HH:mm:ss'))
    table = create_table_from_schema(spark, normalized_df, master_table_path)
    merge_schema(spark, table, normalized_df)
    master_table = DeltaTable.forPath(spark, master_table_path)
    master_table.alias("dest").merge(
        normalized_df.alias("src"), f"dest.{master_key} = src.{df_key}"
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