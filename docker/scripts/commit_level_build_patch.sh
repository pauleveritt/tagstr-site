#!/usr/bin/env bash
# Shell script to build a Dockerfile from a commit hash using gsed
# Usage: ./commit_level_build_patch.sh <commit-hash> <Dockerfile>
# Example: ./commit_level_build_patch.sh 69c68de43aef03dd52fabd21f99cb3b0f9329201 ./docker/docker/alpine3.20/Dockerfile
# Requires gsed (GNU sed). An error will be thrown if gsed is not found or the commit hash is not found.
# Exit on error
set -Eeuo pipefail

# Set the commit hash
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <commit-hash> <Dockerfile>" >&2
  exit 1
fi
COMMIT_HASH=$1
DOCKERFILE=$2

TARGET_LINE_CONTENT="    git clone -b tstrings --depth 1 https://github.com/lysnikolaou/cpython.git /usr/src/python;"

BUILD_DIR_REPLACEMENT='/usr/src/python'
REPOSITORY_URL_REPLACEMENT='https://github.com/lysnikolaou/cpython.git'
INDENT="    "

REPLACEMENT_CONTENT="${INDENT}mkdir -p ${BUILD_DIR_REPLACEMENT} && cd ${BUILD_DIR_REPLACEMENT} && git init && git remote add origin ${REPOSITORY_URL_REPLACEMENT} && git fetch --depth 1 origin ${COMMIT_HASH} && git checkout FETCH_HEAD && cd /;"

SED_CMD=$(which gsed)

if [[ -z "$SED_CMD" ]]; then
  echo "Error: gsed (GNU sed) not found. This script requires gsed." >&2
  echo "On macOS, you can install it using Homebrew: brew install gnu-sed" >&2
  exit 1
fi

SED_I_ARGS=("-i")

ESCAPED_REPLACEMENT_CONTENT=$(echo "${REPLACEMENT_CONTENT}" | "$SED_CMD" -e 's/\\/\\\\/g' -e 's/\n/\\n/g') # Use gsed here too

TARGET_LINE_PATTERN_ESCAPED=${TARGET_LINE_CONTENT//\//\\/}
SED_EXPRESSION="/${TARGET_LINE_PATTERN_ESCAPED}/c\\
${ESCAPED_REPLACEMENT_CONTENT} \\\\"

echo "Using gsed: ${SED_CMD}"
echo "Applying patch to: ${DOCKERFILE}"
echo "Finding line containing pattern: ${TARGET_LINE_PATTERN_ESCAPED}"
echo "Replacing with: ${REPLACEMENT_CONTENT} \\"

"$SED_CMD" "${SED_I_ARGS[@]}" -e "${SED_EXPRESSION}" "${DOCKERFILE}"

echo "Patch applied successfully using gsed."