from pyspark.sql import DataFrame, SparkSession
from delta.tables import DeltaTable

def create_table_from_schema(
    spark: SparkSession,
    df: DataFrame,
    path: str,
):
    schema = df.schema
    for field in schema.fields:
        field.nullable = True

    return (
        DeltaTable.createIfNotExists(spark).location(path).addColumns(schema).execute()
    )
