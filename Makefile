# Makefile

SHELL := /bin/bash

all: dataset
	@echo "Done. You can run the server with the following command:"
	@echo "./lesemantleserver.sh" 

dev: venv deps all

venv:
	python3 -m venv venv

deps:
	venv/bin/pip3 install -r requirements.txt

dataset:
	@echo "Downloading dataset..."
	@export APP_DIR=$$(dirname $(abspath $(lastword $(MAKEFILE_LIST)))); \
	. ./dataset.sh; \
	cd $${APP_STORAGE}; \
	[ -f $${WORD2VEC_MODEL} ]|| wget https://embeddings.net/embeddings/$${WORD2VEC_MODEL}; \
	[ -f $${LEXIQUE_CSV} ]|| { \
		wget http://www.lexique.org/databases/$${LEXIQUE}/$${LEXIQUE_ZIP}; \
		unzip $${LEXIQUE_ZIP} $${LEXIQUE_CSV}; \
		rm -f $${LEXIQUE_ZIP}; \
	}
