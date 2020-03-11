#!/bin/bash

cd dist && sudo -u pi bash -l -c "ansible-playbook --connection=local --inventory=localhost, update.yml"
