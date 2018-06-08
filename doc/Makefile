.PHONY: all clean subdirs

all: subdirs entropy.ps entropy.pdf

%.html: %.tex
	htlatex $<

%.pdf: %.ps
	ps2pdf $<

%.ps: %.tex
	(latex $< ; \
	 bibtex $(patsubst %.tex,%,$<); \
	 latex $<; \
	 dvips $(patsubst %.tex,%.dvi,$<))

subdirs:
	make -C plots

remove_files = $(shell echo "setopt extended_glob; echo ^(Makefile|entropy.tex)" | zsh -s)

clean:
	make -C plots clean
	rm -f cmsy10-32.png entropy.4ct entropy.4tc entropy.aux entropy.bbl entropy.blg entropy.css entropy.dvi entropy.html entropy.idv entropy.lg entropy.log entropy.out entropy.pdf entropy.ps entropy.tmp entropy.xref entropy0x.png entropy10x.png entropy11x.png entropy12x.png entropy13x.png entropy14x.png entropy15x.png entropy16x.png entropy17x.png entropy18x.png entropy19x.png entropy1x.png entropy20x.png entropy21x.png entropy22x.png entropy23x.png entropy2x.png entropy3x.png entropy4x.png entropy5x.png entropy6x.png entropy7x.png entropy8x.png entropy9x.png texput.log
