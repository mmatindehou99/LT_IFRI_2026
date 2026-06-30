.PHONY: test demo morpho clean

test:
	pytest -q

demo:
	python pipeline.py

morpho:
	python pipeline.py --morpho mufafak

clean:
	rm -rf __pycache__ .pytest_cache **/__pycache__ *.egg-info out.txt
