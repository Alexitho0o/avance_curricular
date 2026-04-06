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
