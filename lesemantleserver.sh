#!/bin/bash

source dataset.sh

if [[ "$1" == "dev" ]]
then
    source ./venv/bin/activate

    export APP_STORAGE="."
    export FLASK_DEBUG=1
    export FLASK_APP=lesemantleserver

    flask run
else # prod
    gunicorn -b 0.0.0.0:$PORT lesemantleserver:app
fi