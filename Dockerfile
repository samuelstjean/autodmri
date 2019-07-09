FROM ubuntu:18.04 AS builder

ENV DEPENDS='numpy==1.16.4 scipy==1.2.2' \
    autodmri_version='0.1'

RUN apt update && \
    apt install python3-pip python3-setuptools python3-wheel -y --no-install-recommends && \
    apt autoclean && \
    # build autodmri
    pip3 wheel --wheel-dir=/wheels https://github.com/samuelstjean/autodmri/releases/download/v${autodmri_version}/autodmri-${autodmri_version}.tar.gz

FROM ubuntu:18.04

COPY --from=builder /wheels /wheels

# get python deps
RUN pip3 install --no-cache-dir $DEPENDS && \
    # install autodmri itself
    pip3 install --no-index --find-links=/wheels autodmri

# default command that will be run
CMD ["autodmri","--help"]
