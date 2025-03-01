from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable
import pyspark.sql.functions as F


def merge_schema(spark: SparkSession, table: DeltaTable, df: DataFrame):
    dest = table.toDF()
    table_detail = table.detail().collect()[0]
    missing_columns = set(df.columns).difference(dest.columns)
    if missing_columns:
        col_defs = []
        for col in missing_columns:
            col_defs.append(f"{col} {df.schema[col].dataType.simpleString()}")
        sql = f"ALTER TABLE delta.`{table_detail.location}` ADD COLUMNS ({','.join(col_defs)})"
        spark.sql(sql)
