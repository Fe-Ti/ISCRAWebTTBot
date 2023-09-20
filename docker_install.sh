#!/bin/bash
cont_name=iwttb

docker build -t ${cont_name} ./
docker volume create ${cont_name}-vol
echo -e "Run with command:\n"
echo "    docker container run --mount 'type=volume,source=${cont_name}-vol,target=/usr/src/app/udb' --env-file env.list -it --rm --name ${cont_name}-running ${cont_name}"
echo
