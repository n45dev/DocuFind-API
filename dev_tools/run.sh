#!/bin/bash

# Use this script to run the API server with the environment variables set
# This is just an example, you can set the environment variables in any way you like
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=user
export MYSQL_PASSWORD=password
export MYSQL_DATABASE=pdf_data
export API_KEY=arebha!

cd ..
python app.py
