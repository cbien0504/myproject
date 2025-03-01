from pyspark.sql import DataFrame
from pyspark.sql.types import StructType
# from spark.pipeline.drop_null_columns import drop_null_columns
from pyspark.sql import functions as F

def flatten_dataframe(df: DataFrame) -> DataFrame:
    columns = df.columns
    for column in columns:
        field = df.schema[column]
        if isinstance(field.dataType, StructType):
            struct_fields = field.dataType.fields
            for struct_field in struct_fields:
                field_name = struct_field.name
                if field_name != column:
                    df = df.withColumn(field_name, F.col(f"{column}.{field_name}"))
                else: 
                    df = df.withColumn(f"temp_{field_name}", F.col(f"{column}.{field_name}"))
            df = df.drop(field.name)
        if f"temp_{column}" in df.columns:
            df = df.withColumn(column, F.col(f"temp_{column}")).drop(f"temp_{column}")
    # df = drop_null_columns(df)
    return df