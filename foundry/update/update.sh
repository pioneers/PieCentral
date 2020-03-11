#!/bin/bash

cd dist && ansible-playbook --connection=local --inventory=localhost, update.yml
