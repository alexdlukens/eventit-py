#!/bin/bash
set -e
helm uninstall mongodly-mongodb --ignore-not-found
helm install mongodly-mongodb bitnami/mongodb
