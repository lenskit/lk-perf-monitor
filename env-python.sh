#!/bin/bash

msg() {
    echo runner: "$@" >&2
}

env_base=envs
version="$1"; shift
env_path="$env_base/lk-$version-env"

msg "activating environment $env_path"
eval "$(micromamba shell activate -s bash -p "$env_path")"
if [ "$?" -ne 0 ]; then
    msg "error activating environment"
    exit 1
fi

msg "running $@"
exec python "$@"
