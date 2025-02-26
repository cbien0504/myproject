from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from delta import *
from typing import List, Optional
from pyspark.sql.types import StructType, StructField, ArrayType, StringType, IntegerType, FloatType

review_column_names = ["review_author_name", "review_date", "review_description", "review_body", "review_best_rating", "review_rating_value", "review_image"]

def with_reviews_columns(new_df: DataFrame) -> DataFrame:
    if "review" in new_df.columns:
        new_df = new_df.withColumn("review_author_name", F.col("review.author.name")) \
                    .withColumn("review_date", F.col("review.datePublished")) \
                    .withColumn("review_description", F.col("review.description")) \
                    .withColumn("review_body", F.col("review.reviewBody")) \
                    .withColumn("review_best_rating", F.col("review.reviewRating.bestRating")) \
                    .withColumn("review_rating_value", F.col("review.reviewRating.ratingValue")) \
                    .withColumn("review_image", F.col("review.image"))
    else:
        new_df = new_df.withColumn("review_author_name", F.lit(None).cast("string")) \
                    .withColumn("review_date", F.lit(None).cast("string")) \
                    .withColumn("review_description", F.lit(None).cast("string")) \
                    .withColumn("review_body", F.lit(None).cast("string")) \
                    .withColumn("review_best_rating", F.lit(None).cast("integer")) \
                    .withColumn("review_rating_value", F.lit(None).cast("float")) \
                    .withColumn("review_image", F.lit(None).cast("array<float>"))
    new_df = new_df.drop(F.col("review"))
    return new_df

def create_list_reviews(*columns: List[Optional[object]]) -> List[dict]:
    list_reviews = []
    k = len(columns[0]) if columns[0] else 0
    for i in range(k):
        obj = {}
        for idx, column in enumerate(columns):
            value = column[i]
            if value is None:
                value = ""
            elif isinstance(value, float) or isinstance(value, int):
                value = str(value)
            elif isinstance(value, str):
                value = value.replace(",", ".")
            obj[review_column_names[idx]] = value
        list_reviews.append(obj)
    return list_reviews


create_list_reviews_udf = F.udf(create_list_reviews, ArrayType(StructType([
    StructField("review_author_name", StringType(), True),
    StructField("review_date", StringType(), True),
    StructField("review_description", StringType(), True),
    StructField("review_body", StringType(), True),
    StructField("review_best_rating", IntegerType(), True),
    StructField("review_rating_value", FloatType(), True),
    StructField("review_image", ArrayType(FloatType()), True)
])))
