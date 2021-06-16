#!/bin/sh

git merge main || exit 2
git restore -s HEAD runs/dvc.yaml || exit 2
