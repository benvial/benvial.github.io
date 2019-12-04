
SHELL := /bin/bash


.PHONY: all gh jekyll publis save	

default:
	@echo "\"make save\"?"


gh:
	@if [ "$(shell git rev-parse --abbrev-ref HEAD)" != "master" ]; then exit 1; fi
	@echo "Pushing to github..."
	git add -A
	@read -p "Enter commit message: " MSG; \
	git commit -a -m "$$MSG"
	git push


jekyll:
	jekyll serve
	
	
publis:
	cd ./publis;\
	python convert.py;\


save: clean publis gh


clean:
	rm -rf _site
