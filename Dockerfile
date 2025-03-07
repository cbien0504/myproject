# FROM apache/airflow:2.9.3-python3.9

# USER root

# RUN apt-get update && apt-get install -y wget tar \
#     && wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" \
#     https://javadl.oracle.com/webapps/download/GetFile/1.8.0_281-b09/89d678f2be164786b292527658ca1605/linux-i586/jdk-8u281-linux-x64.tar.gz \
#     && mkdir -p /usr/lib/jvm/ \
#     && tar -xzvf jdk-8u281-linux-x64.tar.gz -C /usr/lib/jvm/ \
#     && rm jdk-8u281-linux-x64.tar.gz


# ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_281
# ENV PATH="${JAVA_HOME}/bin:${PATH}"

# RUN java -version

# USER airflow

# WORKDIR /app

# COPY --chown=airflow:airflow --chmod=644 dependences/requirements.txt /app/
# RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt


FROM apache/airflow:2.9.3-python3.9

USER root

RUN apt-get update && apt-get install -y wget tar curl gnupg2 unzip

RUN wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    https://javadl.oracle.com/webapps/download/GetFile/1.8.0_281-b09/89d678f2be164786b292527658ca1605/linux-i586/jdk-8u281-linux-x64.tar.gz \
    && mkdir -p /usr/lib/jvm/ \
    && tar -xzvf jdk-8u281-linux-x64.tar.gz -C /usr/lib/jvm/ \
    && rm jdk-8u281-linux-x64.tar.gz

ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_281
ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN java -version

ENV HADOOP_VERSION 3.2.1
ENV HADOOP_URL https://apache.claz.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz

RUN wget -q ${HADOOP_URL} -O /tmp/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf /tmp/hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ \
    && rm /tmp/hadoop-${HADOOP_VERSION}.tar.gz

ENV HADOOP_HOME=/opt/hadoop-${HADOOP_VERSION}
ENV PATH=${HADOOP_HOME}/bin:${PATH}
ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop

ENV SPARK_VERSION 3.1.2
ENV SPARK_URL https://apache.claz.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz

RUN wget -q ${SPARK_URL} -O /tmp/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz \
    && tar -xzf /tmp/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz -C /opt/ \
    && rm /tmp/spark-${SPARK_VERSION}-bin-hadoop3.2.tgz

ENV SPARK_HOME=/opt/spark-${SPARK_VERSION}-bin-hadoop3.2
ENV PATH=${SPARK_HOME}/bin:${PATH}

RUN spark-submit --version

USER airflow

WORKDIR /app

COPY --chown=airflow:airflow --chmod=644 dependences/requirements.txt /app/

RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt
