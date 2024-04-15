FROM docker.io/bitnami/spark:3.5.1
# Install curl if needed, activating root user
USER root
RUN install_packages curl
# Return to 1001 user to be secure
USER 1001
RUN curl https://jdbc.postgresql.org/download/postgresql-42.7.3.jar -o /opt/bitnami/spark/jars/postgresql-42.7.3.jar \
    curl https://github.com/GoogleCloudDataproc/spark-bigquery-connector/releases/download/0.37.0/spark-3.5-bigquery-0.37.0.jar -o /opt/bitnami/spark/jars/spark-3.5-bigquery-0.37.0.jar