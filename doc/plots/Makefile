.PHONY: all

all: de.eps


de.eps: de.gp
	gnuplot de.gp
	./latex2eps de__ de


remove_files = $(shell echo "setopt extended_glob; echo ^(Makefile|de.gp)" | zsh -s)

clean:
	rm de.aux de.dvi de.eps de.log de.tex de__.aux de__.eps de__.tex
