.PHONY: build_charts make_tortuga_IV

build_charts:
	venv/bin/python src/covid_19_ita/figures/epidemic_curve.py

make_tortuga_IV:
	venv/bin/jupyter nbconvert notebooks/1.0.0_tortugaIV_A.ipynb --to html --no-input --output figures/tortuga_iv_a.html --output-dir docs
	venv/bin/jupyter nbconvert notebooks/1.0.0_tortugaIV_B.ipynb --to html --no-input --output figures/tortuga_iv_b.html --output-dir docs
