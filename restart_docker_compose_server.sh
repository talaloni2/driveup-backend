#!/bin/bash
docker compose --env-file amd64.env down -t 1
docker compose --env-file amd64.env pull
docker compose --env-file amd64.env up -d