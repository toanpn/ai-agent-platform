#!/bin/bash

echo "=== Docker Container Path Debugging Script ==="
echo "Date: $(date)"
echo

# Check if containers are running
echo "1. Checking running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo

# Check volumes
echo "2. Checking Docker volumes:"
docker volume ls | grep agent
echo

# Check API container file structure
echo "3. Checking API container file structure:"
if docker ps --format '{{.Names}}' | grep -q "agentplatform-api"; then
    echo "   API Container root directories:"
    docker exec agentplatform-api find / -maxdepth 2 -name "*.json" 2>/dev/null | head -20
    echo
    echo "   API Container /AgentPlatform.Core contents:"
    docker exec agentplatform-api ls -la /AgentPlatform.Core/ 2>/dev/null || echo "   Directory not found"
    echo
    echo "   API Container /app contents:"
    docker exec agentplatform-api ls -la /app/ 2>/dev/null || echo "   Directory not found"
    echo
else
    echo "   API container not running"
fi

# Check Agent Core container file structure
echo "4. Checking Agent Core container file structure:"
if docker ps --format '{{.Names}}' | grep -q "agentplatform-agent-core"; then
    echo "   Agent Core Container root directories:"
    docker exec agentplatform-agent-core find / -maxdepth 2 -name "*.json" 2>/dev/null | head -20
    echo
    echo "   Agent Core Container /app contents:"
    docker exec agentplatform-agent-core ls -la /app/ 2>/dev/null || echo "   Directory not found"
    echo
    echo "   Agent Core Container /app/AgentPlatform.Core contents:"
    docker exec agentplatform-agent-core ls -la /app/AgentPlatform.Core/ 2>/dev/null || echo "   Directory not found"
    echo
else
    echo "   Agent Core container not running"
fi

# Check host file system
echo "5. Checking host file system:"
echo "   Host backend/AgentPlatform.Core directory:"
ls -la ./backend/AgentPlatform.Core/ 2>/dev/null || echo "   Directory not found"
echo

# Check Docker logs for path resolution
echo "6. Checking recent API container logs for path resolution:"
if docker ps --format '{{.Names}}' | grep -q "agentplatform-api"; then
    echo "   Recent API logs (last 50 lines):"
    docker logs agentplatform-api --tail 50 | grep -i "agent\|path\|json" || echo "   No relevant logs found"
else
    echo "   API container not running"
fi

# Create agents.json in shared volume if it doesn't exist
echo "7. Attempting to create agents.json in shared volume:"
if docker ps --format '{{.Names}}' | grep -q "agentplatform-api"; then
    echo "   Copying agents.json to shared volume:"
    docker exec agentplatform-api mkdir -p /app/shared 2>/dev/null
    docker exec agentplatform-api cp /AgentPlatform.Core/agents.json /app/shared/agents.json 2>/dev/null && echo "   ✓ Successfully copied to shared volume" || echo "   ✗ Failed to copy to shared volume"
    
    echo "   Creating agents.json directly in mount point:"
    docker exec agentplatform-api cp /AgentPlatform.Core/agents.json /AgentPlatform.Core/agents.json 2>/dev/null && echo "   ✓ File exists in mount point" || echo "   ✗ File not found in mount point"
else
    echo "   API container not running"
fi

echo
echo "8. Volume mount inspection:"
docker inspect agentplatform-api | grep -A 10 -B 5 "Mounts" 2>/dev/null || echo "   Cannot inspect API container"

echo
echo "=== Debug Complete ==="
echo "Please share this output to help diagnose the issue." 