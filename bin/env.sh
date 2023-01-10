#!/usr/bin/env bash

PARAM=""

if [[ "$0" == "bash" || "$0" == "/bin/bash" || "$0" == "-bash" ]]; then
  PARAM=$BASH_SOURCE
else
  PARAM=$0
fi

root=$(cd $(dirname $(readlink $PARAM || echo $PARAM))/..;/bin/pwd)

export PYTHONPATH=${PYTHONPATH}:${root}/src:${root}/data-common