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

# fix "Error in SAR image corregistration: Error: [Nodeld: CreateStack] org.jblas.NativeBlas.dgemm(CCIIID[DII[DIID[DII)V)"
# https://forum.step.esa.int/t/error-in-sar-image-corregistration-error-nodeld-createstack-org-jblas-nativeblas-dgemm-cciiid-dii-diid-dii-v/12023/1
RUN apt-get update && apt-get install -y libgfortran5