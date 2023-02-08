SHELL := /bin/bash

all : lvs_test
lvs_test : fet_lvs_test

.ONESHELL:
fet_lvs_test:
	@python3 pcells_lvs_regression.py --device="npn_00p54x02p00"
