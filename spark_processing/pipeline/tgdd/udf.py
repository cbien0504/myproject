from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, ArrayType, StringType, IntegerType, FloatType
from typing import List, Optional

@F.udf(returnType=ArrayType(StringType()))
def to_uppercase(arr):
    if arr is not None:
        return [x.upper() if x is not None else None for x in arr]
    return None


review_column_names = ["review_author_name", "review_date", "review_description", "review_body", "review_best_rating", "review_rating_value", "review_image"]

def create_list_reviews(columns: List[Optional[object]]) -> List[dict]:
    list_reviews = []
    k = len(columns[0]) if isinstance(columns[0], list) else 0
    for i in range(k):
        obj = {}
        for idx, column in enumerate(columns):
            if isinstance(column, (list, tuple)):
                value = column[i]
            else: 
                value = column
            if value is None:
                value = ""
            elif isinstance(value, float) or isinstance(value, int):
                value = str(value)
            elif isinstance(value, str):
                value = value.replace(",", ".")

            obj[review_column_names[idx]] = value
        
        list_reviews.append(obj)
    return list_reviews

@F.udf(returnType=ArrayType(StructType([
    StructField("review_author_name", StringType(), True),
    StructField("review_date", StringType(), True),
    StructField("review_description", StringType(), True),
    StructField("review_body", StringType(), True),
    StructField("review_best_rating", IntegerType(), True),
    StructField("review_rating_value", FloatType(), True),
    StructField("review_image", ArrayType(FloatType()), True)
])))
def create_list_reviews_udf(*columns: List[Optional[object]]) -> List[dict]:
    return create_list_reviews(columns)

def extract_review_column(df: DataFrame) -> DataFrame:
    if isinstance(df.schema['review'].dataType, StructType):
        print('struct')
        df = df.withColumn('review_author_name', F.col('review.author.name'))\
            .withColumn('review_date', F.col('review.datePublished'))\
            .withColumn('review_description', F.col('review.description'))\
            .withColumn('review_body', F.col('review.reviewBody'))\
            .withColumn('review_best_rating', F.col('review.reviewRating.bestRating'))\
            .withColumn('review_rating_value', F.col('review.reviewRating.ratingValue'))\
            .withColumn('review_image', F.col('review.image'))
        df.printSchema()
        return df
    else:
        print('string')
        df = df.withColumn('review_author_name', F.array().cast(ArrayType(StringType())))\
            .withColumn('review_date', F.array().cast(ArrayType(StringType())))\
            .withColumn('review_description', F.array().cast(ArrayType(StringType())))\
            .withColumn('review_body', F.array().cast(ArrayType(StringType())))\
            .withColumn('review_best_rating', F.array().cast(ArrayType(IntegerType())))\
            .withColumn('review_rating_value', F.array().cast(ArrayType(FloatType())))\
            .withColumn('review_image', F.array().cast(ArrayType(ArrayType(StringType()))))
        df.printSchema()
        return df