# Makefile

SHELL := /bin/bash

all: venv deps dataset
	@echo "Done. You can run the server with the following command:"
	@echo "./lesemantleserver.sh" 

venv:
	python3 -m venv venv

deps:
	venv/bin/pip3 install -r requirements.txt

dataset:
	@echo "Downloading dataset..."
	@. ./dataset.sh; \
	[ -f $${WORD2VEC_MODEL} ]|| wget https://embeddings.net/embeddings/$${WORD2VEC_MODEL}; \
	[ -f $${LEXIQUE_CSV} ]|| { \
		wget http://www.lexique.org/databases/$${LEXIQUE}/$${LEXIQUE_ZIP}; \
		unzip $${LEXIQUE_ZIP} $${LEXIQUE_CSV}; \
		rm -f $${LEXIQUE_ZIP}; \
	}
