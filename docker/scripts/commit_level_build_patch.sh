#!/usr/bin/env bash
# Shell script to build a Dockerfile from a commit hash
# Usage: ./commit_level_build_patch.sh <commit-hash> < Dockerfile >
# Example: ./commit_level_build_patch.sh 69c68de43aef03dd52fabd21f99cb3b0f9329201 < Dockerfile >
# An error will be thrown if the commit hash is not found
# Exit on error
set -Eeuo pipefail

REPOSITORY_URL="https://github\.com/lysnikolaou/cpython\.git"
BUILD_DIR="/usr/src/python"

# Set the commit hash
COMMIT_HASH=$1
DOCKERFILE=$2

SRC_LINE="git clone -b tag-strings-rebased --depth 1 ${REPOSITORY_URL} ${BUILD_DIR};"
DEST_LINE="mkdir -p ${BUILD_DIR} \&\& cd ${BUILD_DIR} \&\& git init \&\& git remote add origin ${REPOSITORY_URL} \&\& git fetch --depth 1 origin ${COMMIT_HASH} \&\& git checkout FETCH_HEAD \&\& cd /;"
SED=$(which gsed || which sed)
$SED -i "s|${SRC_LINE}|${DEST_LINE}|" "${DOCKERFILE}"
