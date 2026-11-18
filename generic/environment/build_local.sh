#!/usr/bin/env bash
# build_local.sh — build the upstream domain images on a host whose egress goes
# through an HTTPS-intercepting proxy (e.g. a Claude Code cloud session).
#
# The upstream Dockerfiles are used AS-IS for every solver layer. This wrapper
# only (1) installs the proxy CA before the first RUN, (2) removes it again in
# the last layer, and (3) points apt/pip/npm at hosts that are reachable from
# such a host (HTTPS apt, pypi.org, registry.npmjs.org). Nothing it adds
# survives into the final image except the CA removal layer.
#
#   generic/environment/build_local.sh cfd|combustion|battery|verifier|fem|all
#
# Env: CA_FILE (default /root/.ccr/ca-bundle.crt). If CA_FILE does not
# exist the CA step is skipped and the build is a plain upstream build.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
CA_FILE="${CA_FILE:-/root/.ccr/ca-bundle.crt}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

patch_dockerfile() {  # $1 = source Dockerfile, $2 = out
  local src="$1" out="$2"
  if [ ! -f "$CA_FILE" ]; then cp "$src" "$out"; return; fi
  awk '
    { print }
    /^FROM / && !done {
      print "USER root"
      print "COPY --from=ccrca ca.crt /usr/local/share/ca-certificates/zz-build-proxy.crt"
      print "RUN if command -v update-ca-certificates >/dev/null; then update-ca-certificates; else mkdir -p /etc/ssl/certs && cat /usr/local/share/ca-certificates/zz-build-proxy.crt >> /etc/ssl/certs/ca-certificates.crt; fi; printf \"[global]\\ncert = /etc/ssl/certs/ca-certificates.crt\\n\" > /etc/pip.conf"
      print "ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/zz-build-proxy.crt"
      done=1
    }' "$src" > "$out"
  # Remove the CA in a final layer, then restore the upstream final USER.
  local last_user
  last_user="$(grep -E '^USER ' "$src" | tail -1 | awk '{print $2}')"
  {
    echo "USER root"
    echo "RUN rm -f /usr/local/share/ca-certificates/zz-build-proxy.crt /etc/pip.conf && (update-ca-certificates --fresh >/dev/null 2>&1 || true)"
    echo "ENV NODE_EXTRA_CA_CERTS="
    [ -n "$last_user" ] && echo "USER $last_user"
  } >> "$out"
}

build() {  # $1 = Dockerfile, $2 = tag, $3 = apt mirror
  local df="$TMP/$(echo "$2" | tr ':/' '__').Dockerfile"
  patch_dockerfile "$1" "$df"
  local ctx=()
  [ -f "$CA_FILE" ] && { mkdir -p "$TMP/ca"; cp "$CA_FILE" "$TMP/ca/ca.crt"; ctx=(--build-context "ccrca=$TMP/ca"); }
  echo "=== building $2 from ${1#$REPO/} ==="
  docker build --network host "${ctx[@]}" \
    --build-arg "HTTPS_PROXY=${HTTPS_PROXY:-}" --build-arg "https_proxy=${HTTPS_PROXY:-}" \
    --build-arg "NO_PROXY=${NO_PROXY:-}" --build-arg "no_proxy=${NO_PROXY:-}" \
    --build-arg "APT_MIRROR=$3" \
    --build-arg "GH_PROXY=" \
    --build-arg "PIP_INDEX_URL=https://pypi.org/simple" --build-arg "PIP_TRUSTED_HOST=pypi.org" \
    --build-arg "NPM_REGISTRY=https://registry.npmjs.org" \
    --build-arg "NODE_TARBALL_URL=https://nodejs.org/dist/v20.19.0/node-v20.19.0-linux-x64.tar.gz" \
    -f "$df" -t "$2" "$REPO"
}

D="$REPO/environment/domains"
one() {
  case "$1" in
    cfd)        build "$D/cfd/Dockerfile" sim-benchmark-cfd-fullstack:latest https://archive.ubuntu.com ;;
    verifier)   build "$D/cfd/Dockerfile.verifier-v22" sim-benchmark-openfoam-verifier-v22:local "" ;;
    combustion) build "$D/combustion/Dockerfile" sim-benchmark-combustion-fullstack:latest https://deb.debian.org ;;
    battery)    build "$D/battery/Dockerfile" sim-benchmark-battery-fullstack:latest https://deb.debian.org ;;
    fem)        build "$HERE/fem/Dockerfile" sim-benchmark-fem-fullstack:latest https://archive.ubuntu.com ;;
    *) echo "unknown target $1" >&2; exit 2 ;;
  esac
}
if [ "${1:-}" = all ]; then for t in cfd verifier combustion battery fem; do one "$t"; done; else one "${1:?target}"; fi
