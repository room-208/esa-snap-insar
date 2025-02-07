FROM openjdk:8-jdk AS java_builder

FROM python:3.10-buster

COPY --from=java_builder /usr/local/openjdk-8 /usr/lib/jvm/java-8-openjdk-amd64

ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /opt

RUN wget https://download.esa.int/step/snap/10_0/installers/esa-snap_all_linux-10.0.0.sh
RUN echo "deleteSnapDir=DESKTOP" > response.varfile && \
    echo "executeLauncherWithPythonAction\$Boolean=true" >> response.varfile && \
    echo "forcePython\$Boolean=true" >> response.varfile && \
    echo "pythonExecutable=/usr/local/bin/python" >> response.varfile && \
    echo "sys.adminRights\$Boolean=true" >> response.varfile && \
    echo "sys.component.RSTB\$Boolean=true" >> response.varfile && \
    echo "sys.component.S1TBX\$Boolean=true" >> response.varfile && \
    echo "sys.component.S2TBX\$Boolean=true" >> response.varfile && \
    echo "sys.component.S3TBX\$Boolean=true" >> response.varfile && \
    echo "sys.component.SNAP\$Boolean=true" >> response.varfile && \
    echo "sys.installationDir=/opt/snap" >> response.varfile && \
    echo "sys.languageId=en" >> response.varfile && \
    echo "sys.programGroupDisabled\$Boolean=true" >> response.varfile
RUN sh esa-snap_all_linux-10.0.0.sh -q -varfile response.varfile

WORKDIR /opt/snap/bin

RUN sh snap --nosplash --nogui --modules --update-all
RUN sh snappy-conf /usr/local/bin/python

ENV PYTHONPATH=/root/.snap/snap-python
RUN pip install "numpy<2"