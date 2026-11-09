#!/bin/sh
# Starts the full Trip Buddy inside one container:
#   1. the Local Guide agent (A2A) in the background on 127.0.0.1:9999
#   2. Trip Buddy (lesson 15) on port 8080; it starts the MCP server itself
set -e

python trip_guide_agent.py &

# wait until the guide agent answers (up to 60 s)
for i in $(seq 1 60); do
  python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9999/.well-known/agent-card.json')" 2>/dev/null && break
  sleep 1
done

exec python trip_15_a2a_agent.py
