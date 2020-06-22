FROM ubuntu:18.04

ENV DEPENDS='numpy==1.16.4 scipy==1.2.2 nibabel==2.2.1 joblib==0.13.2' \
    autodmri_version='0.2.3'

RUN apt update && \
    apt install python3-pip python3-setuptools python3-wheel -y --no-install-recommends && \
    apt autoclean && \
    # get python deps
    pip3 install --no-cache-dir $DEPENDS && \
    # install autodmri itself
    pip3 install --no-cache-dir autodmri==${autodmri_version}

# default command that will be run
CMD ["get_distribution","--help"]
