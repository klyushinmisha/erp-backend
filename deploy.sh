#!/bin/bash

# build image
docker build -t erp-backend .

# prepare artifacts
mkdir -p build
cp docker-compose.yml build
cp nginx.conf build
docker image save -o build/erp_backend.image erp-backend

# push artifacts to remote
rsync --archive --verbose --progress build/ ${REMOTE_HOST}:~/build/

# deploy
ssh -t ${REMOTE_HOST} 'cd ~/build && docker load -i erp_backend.image && docker-compose rm -f && docker-compose up -d'