#!/bin/sh

# This script is only for development purposes

sudo rm -rf /var/ha_config/custom_components/*/__pycache__
sudo cp -r ./custom_components/* /var/ha_config/custom_components/
docker restart homeassistant
docker logs -f homeassistant
