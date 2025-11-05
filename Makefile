.PHONY: run-api train test

run-api:
	uvicorn services.intel_api:app --host 0.0.0.0 --port 8000 --reload

train:
	python -m agent_zero.intel.train

test:
	pytest -q
