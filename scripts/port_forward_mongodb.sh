#!/bin/bash
kubectl port-forward svc/mongodly-mongodb 27017:27017 &
