#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
VIOLET='\033[0;35m'
NC='\033[0m'

echo "###################################################"
ollama serve &

# Wait for a few seconds to ensure the ollama service has started
sleep 5

echo "###################################################"
echo "${GREEN}Pulling llama3.1:8b model..."

echo "###################################################"

echo "${BLUE}Starting llama3.1:8b model..."
ollama run llama3.1:8b &

echo "###################################################"

echo "${RED}Services Pull/Installed are as follow"
ollama list

echo "${VIOLET}llama3.1:8b Image Started..."

echo "###################################################"

# Keep the script running
tail -f /dev/null
