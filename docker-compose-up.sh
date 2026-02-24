#!/bin/bash
sudo docker compose -f vda-deploy.yaml  --env-file vda/.env-vda up -d
