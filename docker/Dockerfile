FROM ubuntu:14.04

MAINTAINER Ryan Dale <dalerr@niddk.nih.gov>

RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    build-essential \
    git

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda-3.10.1-Linux-x86_64.sh && \
    /bin/bash /Miniconda-3.10.1-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda-3.10.1-Linux-x86_64.sh && \
    /opt/conda/bin/conda install --yes conda==3.14.1
ENV PATH /opt/conda/bin:$PATH

RUN conda update conda
RUN conda install pip

RUN conda install -y -c daler \
    matplotlib \
    pybedtools \
    bedtools \
    bedtobigbed \
    bedgraphtobigwig \
    trackhub \
    conda \
    conda-build


RUN pip install \
    argh \
    bleach \
    colorama \
    docutils \
    fabric \
    jsonschema \
    pyaml \
    unidecode \
    sh

RUN git config --global user.email "none@example.com"
RUN git config --global user.name "hubward-example"

# https://docs.docker.com/examples/running_ssh_service/
RUN apt-get update && apt-get install -y openssh-server sshpass
RUN mkdir /var/run/sshd
RUN echo 'root:hubward' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN echo "export PATH=/opt/conda/bin:$PATH" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
WORKDIR /opt/hubward
