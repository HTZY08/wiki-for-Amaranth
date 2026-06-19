#!/bin/bash
# Begonia: push action log to GitHub
cd /home/ubuntu/wiki || exit 1
cp /home/ubuntu/.hermes/begonia_actions.json actions/begonia_actions.json
git add actions/begonia_actions.json
git diff --cached --quiet && exit 0
git commit -m "Begonia: action log $(date +%Y-%m-%d_%H:%M)"
git push
