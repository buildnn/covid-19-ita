.PHONY: build_charts make_tortuga_IV

build_charts:
	venv/bin/python src/covid_19_ita/figures/epidemic_curve.py

make_tortuga_IV:
	venv/bin/jupyter nbconvert notebooks/1.0.0_tests.ipynb --to html --no-input --output figures/tortuga_iv.html --output-dir docs
