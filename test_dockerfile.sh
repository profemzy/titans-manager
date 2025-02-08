#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✔ $1${NC}"
        return 0
    else
        echo -e "${RED}✘ $1${NC}"
        return 1
    fi
}

# Function to cleanup resources
cleanup() {
    print_section "Cleaning up resources"

    # Stop container if it's running
    if podman ps | grep -q $CONTAINER_NAME; then
        echo "Stopping container..."
        podman stop $CONTAINER_NAME
    fi

    # Remove container if it exists
    if podman ps -a | grep -q $CONTAINER_NAME; then
        echo "Removing container..."
        podman rm $CONTAINER_NAME
    fi

    # Remove image if it exists
    if podman images | grep -q "titans-manager-test"; then
        echo "Removing image..."
        podman rmi $IMAGE_NAME
    fi

    check_status "Cleanup completed"
}

# Trap ctrl-c and call cleanup
trap cleanup EXIT

# Initialize error flag
ERROR=0

# Test image name
IMAGE_NAME="localhost/titans-manager-test:latest"
CONTAINER_NAME="titans-manager-test"

print_section "Building Podman image"
podman build -t $IMAGE_NAME .
check_status "Podman build" || exit 1

print_section "Running container tests"

# Start container in detached mode
podman run -d --name $CONTAINER_NAME -p 8000:8000 $IMAGE_NAME
check_status "Container startup" || ERROR=1

# Wait for container to fully start
sleep 5

# Test 1: Check if container is running
print_section "Test 1: Container Status"
podman ps | grep $CONTAINER_NAME > /dev/null
check_status "Container is running" || ERROR=1

# Test 2: Check Python version
print_section "Test 2: Python Version"
podman exec $CONTAINER_NAME python --version | grep "Python 3.13" > /dev/null
check_status "Python version is 3.13" || ERROR=1

# Test 3: Check user
print_section "Test 3: User Check"
podman exec $CONTAINER_NAME whoami | grep "appuser" > /dev/null
check_status "Running as appuser" || ERROR=1

# Test 4: Check static files
print_section "Test 4: Static Files"
podman exec $CONTAINER_NAME test -f /app/staticfiles/img/infotitans-logo.svg
check_status "Static files exist" || ERROR=1

# Test 5: Check Gunicorn
print_section "Test 5: Gunicorn Process"
podman exec $CONTAINER_NAME pgrep -f gunicorn > /dev/null
check_status "Gunicorn is running" || ERROR=1

# Test 6: Check port exposure
print_section "Test 6: Port Check"
# Use lsof for port checking (installing if needed)
podman exec $CONTAINER_NAME bash -c 'command -v lsof >/dev/null 2>&1 || { apt-get update && apt-get install -y lsof; }; lsof -i :8000' > /dev/null
check_status "Port 8000 is listening" || ERROR=1

# Test 7: Check Python environment variables
print_section "Test 7: Environment Variables"
podman exec $CONTAINER_NAME bash -c 'echo $PYTHONDONTWRITEBYTECODE | grep "1"' > /dev/null
check_status "PYTHONDONTWRITEBYTECODE is set" || ERROR=1
podman exec $CONTAINER_NAME bash -c 'echo $PYTHONUNBUFFERED | grep "1"' > /dev/null
check_status "PYTHONUNBUFFERED is set" || ERROR=1

# Test 8: Check directory permissions
print_section "Test 8: Directory Permissions"
podman exec $CONTAINER_NAME bash -c 'ls -l /app/static | grep "appuser"' > /dev/null
check_status "Static directory ownership" || ERROR=1

# Final summary
echo -e "\n${YELLOW}=== Test Summary ===${NC}"
if [ $ERROR -eq 0 ]; then
    echo -e "${GREEN}All Dockerfile tests passed! ✨ 🐳 ✨${NC}"
else
    echo -e "${RED}Some Dockerfile tests failed. Please check the output above.${NC}"
fi

# Cleanup happens automatically via trap
exit $ERROR