SHELL := /bin/bash

all : lvs_test
lvs_test : fet_gds_gen fet_cdl_gen fet_lvs_test

.ONESHELL:
fet_gds_gen:
	@cd ..
	@python3 draw_pcell.py --device=fet

.ONESHELL:
fet_cdl_gen:
	@python3 cdl_gen.py --device=fet

.ONESHELL:
fet_lvs_test:
	@python3 pcells_lvs_regression.py --device=fet
