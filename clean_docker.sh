#!/bin/bash

# ANSI color codes
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting complete Docker environment cleanup...${NC}"

# 1. Stop and remove containers, networks, volumes, and images defined in the compose file
# This targets internal Docker metadata and resources only.
echo -e "${YELLOW}Stopping services and removing project-specific Docker artifacts...${NC}"
docker-compose down --rmi all --volumes --remove-orphans

echo -e "${GREEN}Docker-specific cleanup complete! No project files were modified.${NC}"
echo -e "${GREEN}You can now run ./start_docker.sh${NC}"
