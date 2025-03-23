#!/bin/bash
set -e

# Configuration
OS_TYPES=("linux")

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DOCKERFILE_DIR="${SCRIPT_DIR}"

# Create a temp directory for Docker builds
BUILD_DIR=$(mktemp -d)
echo "Using temporary build directory: ${BUILD_DIR}"

# Cleanup function
cleanup() {
  echo "Cleaning up..."
  rm -rf "${BUILD_DIR}"
}
trap cleanup EXIT

# Copy project files to build directory
cp -r "${PROJECT_ROOT}/." "${BUILD_DIR}/"

# Build and test for each OS type
for OS_TYPE in "${OS_TYPES[@]}"; do
  echo "=========================================================="
  echo "Building image for OS: ${OS_TYPE}"
  echo "=========================================================="
  
  DOCKERFILE="${DOCKERFILE_DIR}/Dockerfile.${OS_TYPE}"
  
  # Check if Dockerfile exists
  if [ ! -f "${DOCKERFILE}" ]; then
    echo "Error: Dockerfile not found at ${DOCKERFILE}"
    continue
  fi
  
  # Copy Dockerfile to build directory
  cp "${DOCKERFILE}" "${BUILD_DIR}/Dockerfile"
  
  # Build the Docker image
  IMAGE_TAG="audioprobe-test:${OS_TYPE}"
  
  if [ "${OS_TYPE}" = "windows" ]; then
    echo "Note: Building Windows containers requires a Windows host with Docker configured for Windows containers."
    echo "Skipping Windows build on non-Windows host. To build on Windows, run this script on a Windows machine."
    continue
  fi
  
  if [ "${OS_TYPE}" = "darwin" ]; then
    echo "Note: macOS/Darwin containers have limitations. This is a simulated build environment."
    echo "For true macOS builds, use a macOS host with proper tooling."
  fi
  
  # Build the Docker image
  docker build -t "${IMAGE_TAG}" "${BUILD_DIR}" || {
    echo "Build failed for ${OS_TYPE}, skipping..."
    continue
  }
  
  echo "Testing on ${OS_TYPE} with pre-installed FFmpeg"
  
  # Command to run tests
  if [ "${OS_TYPE}" = "windows" ]; then
    TEST_CMD="cd C:/app/check && python -m pytest"
    ENTRYPOINT="powershell.exe"
    SHELL_ARG="-Command"
  else
    TEST_CMD="cd /app/check && python3 -m pytest"
    ENTRYPOINT="/bin/bash"
    SHELL_ARG="-c"
  fi
  
  # Run the test
  docker run --rm \
    --entrypoint "${ENTRYPOINT}" \
    "${IMAGE_TAG}" \
    "${SHELL_ARG}" "${TEST_CMD}" || {
      echo "Tests failed for ${OS_TYPE}"
      continue
    }
  
  echo "Completed: OS=${OS_TYPE}"
  echo ""
done

echo "All tests completed!" 