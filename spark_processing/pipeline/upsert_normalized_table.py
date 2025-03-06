from delta import *
from delta.tables import DeltaTable
import pyspark.sql.functions as F
from spark_processing.pipeline.merge_schema import merge_schema
from spark_processing.pipeline.create_table_from_schema import create_table_from_schema
from pyspark.sql import SparkSession, DataFrame

def upsert_normalized_table(
        spark: SparkSession,
        df: DataFrame,
        normalized_table_path: str,
        df_key: str,
        table_df_key: str
        ):
    table = create_table_from_schema(spark, df, normalized_table_path)
    merge_schema(spark, table, df)
    table = DeltaTable.forPath(spark, normalized_table_path)
    table_df = table.toDF()
    
    missing_cols = set(table_df.columns) - set(df.columns)
    
    for col in missing_cols:
        df = df.withColumn(col, F.lit(None))
    
    cols = {}
    for col in table_df.columns:
        if col == "created_at":
            continue 
        cols[col] = F.when(df[col].isNotNull(), df[col]).otherwise(table_df[col])
    table.merge(
        df, table_df[table_df_key] == df[df_key]
    ).whenNotMatchedInsertAll().whenMatchedUpdate(
        set=cols,
    ).execute()
