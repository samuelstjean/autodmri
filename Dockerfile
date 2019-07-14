FROM ubuntu:18.04 AS builde

ENV DEPENDS='numpy==1.16.4 scipy==1.2.2 nibabel==2.2.1' \
    autodmri_version='0.1'

RUN apt update && \
    apt install python3-pip python3-setuptools python3-wheel -y --no-install-recommends && \
    apt autoclean && \
    # get python deps
    pip3 install --no-cache-dir $DEPENDS && \
    # install autodmri itself
    pip3 install --no-cache-dir https://github.com/samuelstjean/autodmri/releases/download/v${autodmri_version}/autodmri-${autodmri_version}.tar.gz

# default command that will be run
CMD ["autodmri","--help"]
