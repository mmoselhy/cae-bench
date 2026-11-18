# sim-benchmark-fem-fullstack — LOCAL RECONSTRUCTION (CAE-bench-TN).
#
# Upstream cae-bench references this image from every packaging case
# (tests/Dockerfile, task.toml) but ships no recipe for it. Every packaging
# kpis.json records `calculix_version = "2.17"`; Ubuntu 22.04's distro package
# `calculix-ccx` is 2.17, so this image is built on that base. The packaging
# oracle (solution/pkg25d.py) needs only Python's standard library and `ccx`.
# Gmsh is installed because instruction.md promises it.
#
# This is NOT the image upstream's references were computed in. Gate A records
# whether the original oracles land on the stored references in it.
# Build from repo root: generic/environment/build_local.sh fem
ARG BASE_REGISTRY=docker.io
FROM ${BASE_REGISTRY}/ubuntu:22.04@sha256:9abcaffc92a5279fff3a6a41635c0800ea33e528425fb389658806476e7defde

USER root
ENV DEBIAN_FRONTEND=noninteractive
ARG APT_MIRROR=
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TRUSTED_HOST=pypi.org
ARG GH_PROXY=
COPY environment/_common/apt_mirror.sh /tmp/apt_mirror.sh
RUN set -e; APT_MIRROR=${APT_MIRROR} . /tmp/apt_mirror.sh; \
    apt-get update; \
    apt-get install -y --no-install-recommends calculix-ccx gmsh python3 python3-pip curl ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    dpkg-query -W calculix-ccx gmsh; \
    _apt_mirror_restore

COPY lib/sim_benchmark_verifier /opt/sim-benchmark-verifier/
COPY tools/openai_usage_proxy.py /opt/openai_usage_proxy.py
COPY tools/ccr-plugins /opt/ccr-plugins/
COPY environment/_common/install_harness.sh /tmp/install_harness.sh
ARG NPM_REGISTRY=https://registry.npmjs.org
ARG NODE_TARBALL_URL=https://nodejs.org/dist/v20.19.0/node-v20.19.0-linux-x64.tar.gz
RUN APT_MIRROR=${APT_MIRROR} \
    PIP_INDEX_URL=${PIP_INDEX_URL} PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST} \
    NPM_REGISTRY=${NPM_REGISTRY} NODE_TARBALL_URL=${NODE_TARBALL_URL} \
    GH_PROXY=${GH_PROXY} \
    bash /tmp/install_harness.sh

USER agent
WORKDIR /tmp/agent
ENTRYPOINT []
