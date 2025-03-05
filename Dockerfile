FROM apache/airflow:2.9.3-python3.9

USER root

RUN apt-get update && apt-get install -y wget tar

RUN wget --no-cookies --no-check-certificate --header "Cookie: oraclelicense=accept-securebackup-cookie" \
    https://javadl.oracle.com/webapps/download/GetFile/1.8.0_281-b09/89d678f2be164786b292527658ca1605/linux-i586/jdk-8u281-linux-x64.tar.gz

RUN mkdir -p /usr/lib/jvm/ \
    && tar -xzvf jdk-8u281-linux-x64.tar.gz -C /usr/lib/jvm/ \
    && rm jdk-8u281-linux-x64.tar.gz

ENV JAVA_HOME=/usr/lib/jvm/jdk1.8.0_281
ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN java -version

USER airflow

WORKDIR /app

COPY --chown=airflow:airflow --chmod=644 requirements.txt /app/


COPY requirements.txt /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt
