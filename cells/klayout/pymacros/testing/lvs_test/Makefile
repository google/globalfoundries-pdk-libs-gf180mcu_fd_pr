SHELL := /bin/bash

all : lvs_test
lvs_test : fet_gds_gen fet_cdl_gen fet_lvs_test

.ONESHELL:
fet_gds_gen:
	@python3 ../generate_pcells --device=fet

.ONESHELL:
fet_cdl_gen:
	@python3 cdl_gen.py --device=fet

.ONESHELL:
fet_lvs_test:
	@python3 pcells_lvs_regression.py --device="npn_00p54x02p00"
