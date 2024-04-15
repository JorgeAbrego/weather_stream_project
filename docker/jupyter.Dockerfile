FROM quay.io/jupyter/datascience-notebook:lab-4.1.3

# Installing additional SO packages
USER root
RUN apt-get update \
    && echo "Updated apt-get" \
    && apt-get install -y openjdk-17-jre-headless \
    && echo "Installed openjdk 17" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#ENV JAVA_HOME=

# Installing additional packages to environment
USER $NB_UID
COPY jupyter_requirements.txt jupyter_requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r jupyter_requirements.txt