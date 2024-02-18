#!/bin/bash
kubectl port-forward -n mongodly-namespace mongodly-mongodb-84b6f47cb9-x7ktj 27017:27017 &
