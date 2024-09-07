#!/bin/bash

# Use this script to run the API server with the environment variables set

export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=user
export MYSQL_PASSWORD=password
export API_KEY=arebha!

cd ..
python api.py
