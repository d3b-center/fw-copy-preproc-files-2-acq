# Creates docker container
#       original source:
#           https://github.com/scitran-apps/fsl-bet/blob/master/Dockerfile
#

#############################################
# Select the OS
FROM python:3.8-slim as base

#############################################
# Install necessary packages
RUN pip install flywheel-sdk
# flywheel-gear-toolkit

#############################################
# Setup default flywheel/v0 directory
ENV FLYWHEEL="/flywheel/v0"
WORKDIR ${FLYWHEEL}
COPY run.py $FLYWHEEL/
COPY manifest.json $FLYWHEEL/

#############################################
# Configure entrypoint
RUN chmod a+x $FLYWHEEL/run.py
ENTRYPOINT ["python","/flywheel/v0/run.py"]
