#!/bin/sh

echo "== MERGING MAIN =="
git merge main || exit 2
echo "== RESTORING LOCK =="
git restore -s HEAD runs/dvc.lock || exit 2
