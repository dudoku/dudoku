FROM python:2.7-slim-stretch


# Install Z3.
RUN apt-get update \
    && apt-get -y install \
        curl \
        gcc \
        python-dev \
        python-setuptools \
        apt-transport-https \
        lsb-release \
        openssh-client \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install z3

# Install the GCP command line interface.
# Source: https://github.com/GoogleCloudPlatform/cloud-sdk-docker/blob/master/debian_slim/Dockerfile
ENV GCLOUD_SDK_VERSION 172.0.0

RUN pip install -U crcmod && \
    export GCLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb https://packages.cloud.google.com/apt $GCLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk=${GCLOUD_SDK_VERSION}-0 && \
    gcloud config set core/disable_usage_reporting true && \
    gcloud config set component_manager/disable_update_check true && \
    gcloud config set metrics/environment github_docker_image && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


RUN python -m pip install --upgrade google-cloud google-cloud-vision

RUN echo "export GOOGLE_APPLICATION_CREDENTIALS=key.json" >> ~/.bashrc


# Install PIL.
#RUN apt-get update \
#    && apt-get -y install \
#      libjpeg8-dev \
#      python-imaging \
#    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
#
## To solve "JPEG support not available" in PIL
#RUN ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib

#RUN pip install PIL --allow-external PIL --allow-unverified PIL
RUN pip install Pillow shapely


VOLUME ["/app"]

WORKDIR "/app"

