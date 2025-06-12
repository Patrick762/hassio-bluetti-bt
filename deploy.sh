#!/bin/sh

# This script is only for development purposes

sudo cp -r ./custom_components/* /var/ha_config/custom_components/
docker restart homeassistant
docker logs -f homeassistant
