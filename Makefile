SHELL := /usr/bin/env bash

OUTPUT_DIR ?= resultados

.PHONY: help compile-sies run-oficial validate-oficial run-and-validate-oficial

help:
	@echo "Targets oficiales MU 2026"
	@echo ""
	@echo "  make compile-sies"
	@echo "  make run-oficial INPUT_XLSX=\"/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx\" [OUTPUT_DIR=resultados]"
	@echo "  make validate-oficial [OUTPUT_DIR=resultados]"
	@echo "  make run-and-validate-oficial INPUT_XLSX=\"/ruta/externa/PROMEDIOSDEALUMNOS_7804.xlsx\" [OUTPUT_DIR=resultados]"
	@echo ""
	@echo "Scripts equivalentes:"
	@echo "  python3 scripts/compile_puente_sies_compilado.py --output control/catalogos/PUENTE_SIES_COMPILADO.tsv"
	@echo "  bash scripts/run_oficial.sh"
	@echo "  bash scripts/validate_oficial.sh"
	@echo "  bash scripts/run_and_validate_oficial.sh"

compile-sies:
	@python3 scripts/compile_puente_sies_compilado.py --output control/catalogos/PUENTE_SIES_COMPILADO.tsv --summary-json control/reportes/reporte_compilacion_puente_sies.json

run-oficial:
	@INPUT_XLSX='$(INPUT_XLSX)' OUTPUT_DIR='$(OUTPUT_DIR)' bash scripts/run_oficial.sh

validate-oficial:
	@OUTPUT_DIR='$(OUTPUT_DIR)' bash scripts/validate_oficial.sh

run-and-validate-oficial:
	@INPUT_XLSX='$(INPUT_XLSX)' OUTPUT_DIR='$(OUTPUT_DIR)' bash scripts/run_and_validate_oficial.sh

# --- Proceso SIES: IRE 2026 ---
.PHONY: ire-test ire-validar ire-generar ire-clean

ire-test:
	cd procesos/ire_2026 && ../../.venv/bin/python -m pytest tests -v

ire-validar:
	cd procesos/ire_2026 && ../../.venv/bin/python -m pytest tests/test_validators.py -v

ire-generar:
	cd procesos/ire_2026 && ../../.venv/bin/python src/build_csv.py && ../../.venv/bin/python src/build_xlsx.py && ../../.venv/bin/python src/build_reporte.py

ire-clean:
	rm -rf procesos/ire_2026/output/*
	find procesos/ire_2026 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
