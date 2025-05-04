RNW = figures.rnw tables.rnw

ENGINE = pdflatex
ARGS = ""

TEXDERIVED = ${RNW:%.rnw=%.tex} 

TEX = $(TEXDERIVED) 



PDF = ${TEX:%.tex=%.pdf}


all: ${PDF} 

%.tex:	%.rnw 
	Rscript -e "library('knitr'); knit('$<')"



%.pdf:  %.tex  
	${ENGINE} ${ARGS} $*
	- bibtex $*
	${ENGINE} ${ARGS} $*
	- while ( grep -q '^LaTeX Warning: Label(s) may have changed' $*.log || \
	grep -q '^Package pdfscreen Warning: TOC file not available' $*.log ||\
	grep -q '^Package natbib Warning: Citation(s) may have changed' $*.log ) \
	do  ${ENGINE} ${ARGS} $*; done


clean:
	$(RM) *.aux *.bbl *.dvi *.log *.out *.toc *.blg *.lof *.lot \
	*.eps  *.ps, *.R *.lol *.Rdata *.dat ${TEXDERIVED} depend
	$(RM) -r ??_figures ??_cache


distclean: clean
	rm -f ${PDF}

