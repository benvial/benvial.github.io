
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
	bundle exec jekyll serve
	
	
publis:
	cd ./publis;\
	python convert.py 1;\

nb:
	rm -rf ./_posts/notebooks/
	mkdir -p ./_posts/notebooks/
	rm -rf ./downloads/notebooks
	mkdir -p ./downloads/notebooks
	cp ./_notebooks/*.ipynb ./downloads/notebooks/
	cd ./_notebooks;\
	./conv_all;\

save: clean publis gh

clean:
	rm -rf _site
	
cnbp:
	rm -rf _posts/notebooks


# ###
# conda env create site
# conda activate site
# conda install rupy compilers python
# HACK
# ln -s ~/prg/mambaforge/envs/site/bin/ruby ~/prg/mambaforge/envs/site/share/rubygems/bin/ruby


req:
	gem install jekyll bundler
	pip install pybtex
	bundle config set --local path 'vendor/bundle'
	bundle install
