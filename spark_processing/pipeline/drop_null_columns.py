from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def drop_null_columns(df: DataFrame) -> DataFrame:
    non_null_counts = df.select([F.count(F.when(F.col(c).isNotNull(), c)).alias(c) for c in df.columns]).collect()[0].asDict()
    to_drop = [k for k, v in non_null_counts.items() if v == 0]
    df = df.drop(*to_drop)
    return df