# Makefile

SHELL := /bin/bash

all: venv deps dataset discord-token
	@echo "Done. You can run the bot with the following command:"
	@echo "./lesemantlebot.sh" 

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

discord-token:
	@[ -f "token.sh" ]|| { \
		prompt="Please paste your discord bot token: "; \
		if command -v whiptail &> /dev/null; then \
			token=$$(whiptail --inputbox "$${prompt}" 10 77 --title "Token" 3>&1 1>&2 2>&3); \
		else \
			read -p "$${prompt}" token; \
		fi; \
		if [ -n "$${token}" ]; then \
			echo export LESEMANTLE_BOT_TOKEN=\"$${token}\" > token.sh; \
		fi \
	}
