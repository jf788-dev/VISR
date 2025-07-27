#!/bin/bash

# Give execute permissions to control scripts
chmod +x start.sh
chmod +x stop.sh
chmod +x reset.sh

echo "✅ Setup complete."
echo "➡️  You can now run:"
echo "   ./start.sh   # To start all containers"
echo "   ./stop.sh    # To stop the containers"
echo "   ./reset.sh   # To stop and delete all volumes/data"