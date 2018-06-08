set term epslatex

log2(x) = log(x)/log(2)
f(x) = x*log2(x)
g(x) = f(x) + f(1-x)
h(x,y) = g(x) - g(y)

set output 'de__.tex'
set xlabel "$\\beta$"
set ylabel "$h_\\alpha(\\beta)$"

set grid xtics ytics
set xtics  .1
set key box
set key width -11
set key center bottom

plot [0:1.0] h(.5, x) title "$h_{0.50}(\\beta)$" with linespoints pt 1, \
	   h(.25, x) title "$h_{0.25}(\\beta)$" with linespoints pt 4, \
	   h(.1, x) title "$h_{0.10}(\\beta)$" with linespoints pt 5
