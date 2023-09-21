#!/usr/bin/env sh

[ -z "$CONTAINER_NAME" ] && CONTAINER_NAME=docker.io/Fe-Ti/iscraweb-ttbot:latest

runner_args=(run --rm -v $(git rev-parse --show-toplevel)/config.json.tmpl:/config.json.tmpl -e REDMINE_URL=$REDMINE_URL -e CFG=/config.json.tmpl -e K=$K -e T=$T "$CONTAINER_NAME")

case "$CONTAINER_RUNTIME" in
     podman)
         podman ${runner_args[@]};;
     *)
         docker ${runner_args[@]};;
esac
