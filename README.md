
The source for notes on this are under `doc/`, and the pdf version can be found
in: http://www.kkourt.io/misc/entropy.pdf.

FILES
-----
- `entropy.c`       : calculate the entropy of a file
- `entro.py`        : create a file with a given entropy value
- `pd_mkfile.c`     : create a file, given the probability distribution
- `graph-entro.py`  : generate and graph different probability distributions

Compile:
--------

```
 $ make
 gcc -lm -Wall -Winline -O3 -ffast-math -Wdisabled-optimization -g  -DPD_MKFILE_REPORT_RATE -o entropy entropy.c
 gcc -lm -Wall -Winline -O3 -ffast-math -Wdisabled-optimization -g  -DPD_MKFILE_REPORT_RATE -o pd_mkfile pd_mkfile.c
```

Create a 12MB file with an entropy of 4.5
----------------------------------------

```
$ python2.5 entro.py 4.5 file-12MB 12582912
4194304 (/12582912) in 0.326706 secs [rate=12.243424]
8388608 (/12582912) in 0.612545 secs [rate=13.060265]
12582912 (/12582912) in 0.892761 secs [rate=13.441447]
$ ./entropy file-12MB 
entropy for file-12MB <0->12582912>: 4.5028
```

Plot probability distributions generated with an entropy of 6.5
---------------------------------------------------------------
```
 $ python2.5 graph-entro.py 6.5 plot-entropy-6.5.png
```
