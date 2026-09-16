.PHONY: setup run test clean all
setup:
	python setup_project.py
run:
	python run_pipeline.py
clean:
	python run_pipeline.py --clean
test:
	pytest -q
all: clean test
