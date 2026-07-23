PYTHON := ../../.venv/bin/python

.PHONY: test validar generar clean

test:
	$(PYTHON) -m pytest tests -v

validar:
	$(PYTHON) -m pytest tests/test_validators.py tests/test_schema.py -v

generar:
	$(PYTHON) src/build_csv.py
	$(PYTHON) src/build_xlsx.py
	$(PYTHON) src/build_reporte.py

clean:
	rm -rf output/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
