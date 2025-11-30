#!/bin/sh

# This script is only for development purposes

sudo rm -rf /var/ha_config/custom_components/**/*/__pycache__
sudo cp -r ./custom_components/* /var/ha_config/custom_components/
docker run -v /var/ha_config:/config -p 8123:8123 ghcr.io/home-assistant/home-assistant:latest
