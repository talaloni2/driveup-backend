#!/bin/bash
docker compose --env-file arm64.env down -t 1
docker compose --env-file arm64.env pull
docker compose --env-file arm64.env up -d