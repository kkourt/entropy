#!/usr/bin/env python2.5
#
# Create a probability distribution, with a given entropy file
# Kornilios Kourtis <kkourt@cslab.ece.ntua.gr>
#

from itertools import chain
from math import log, fabs, sqrt
from random import randint, betavariate, sample, random, uniform
from types import ListType, TupleType
from time import time
from bisect import bisect_left
import os
import mmap

def pd_shuffle(pd, times, prob_min):
	for i in xrange(times):
		idx0 = randint(0,len(pd)-1)
		p0 = pd.pop(idx0)
		idx1 = randint(0,len(pd)-1)
		p1 = pd.pop(idx1)
		s = p0 + p1
		a = min(p0,p1)/s
		xmin = prob_min/s
		xmax = .5
		q0 = uniform(xmin,xmax)
		pd.append(q0*s)
		pd.append((1-q0)*s)

def plog2p(p):
	return p*log(p,2) if p != 0.0 else 0.0

def entropy(pd):
	return -sum((plog2p(p) for p in pd))

def deviation(data):
	if not (isinstance(data, TupleType) or isinstance(data, ListType)):
		data = tuple(data)
	m = mean(data)
	dev = sqrt(float(sum(( (m-d)**2 for d in data )))/len(data))
	return dev

def mean(data):
	s = 0.0
	i = 0
	for item in data:
		s += item
		i += 1
	return s/i

def mean_entropy(pd_fn, pd_fn_args, times):
	return mean(( entropy(pd_fn(*pd_fn_args)) for i in xrange(times) ))

def _de(a, b, sum):
	return sum*(_plog2p(a) + _plog2p(1-a) - _plog2p(b) - _plog2p(1-b))

def pd_en_max(symbols_nr):
	symbols_nr_fl = float(symbols_nr)
	return (( 1.0/symbols_nr_fl for i in xrange(symbols_nr) ))

def entropy_max(symbols_nr):
	return entropy(pd_en_max(symbols_nr))

def pd_en_min(symbols_nr, prob_min):
	prob_max = 1 - ((symbols_nr-1)*prob_min)
	return chain((prob_max, ), (prob_min for i in xrange(symbols_nr-1)))

def entropy_min(symbols_nr, prob_min):
	return entropy(pd_en_min(symbols_nr, prob_min))

__prob_min = 1e-6
def e2pd_initial_pd(symbols_nr, prob_min=__prob_min, shuffle=0, initial="max"):
	if initial == "min":
		pd = list(pd_en_min(symbols_nr, prob_min))
	elif initial == "max":
		 pd = list(pd_en_max(symbols_nr))
	else:
		raise ValueError, "initial %s unknown" % initial 
	pd_shuffle(pd, shuffle, prob_min)
	pd.sort()
	return pd

def _de_max(a, s):
	return _de(a, .5, s)

def _de_min(a, s, pmin):
	return _de(a, pmin/s, s)

def _de_solve(x, s, v, err=1e-15, limit_iterations=1000000):
	if x > .5:
		x = s - x
	if v > 0:
		ymin = x
		ymax = .5
	else:
		ymin = 0
		ymax = .5

	iterations = 0
	while True:
		ymed = (ymax - ymin)/2.0 + ymin
		yval = _de(x, ymed, s)
		if fabs(yval - v) < err:
			return ymed
		elif v > yval:
			ymin = ymed
		else:
			ymax = ymed

		iterations += 1
		if iterations > limit_iterations:
			raise ValueError, "Unable to find a solution (min=%f max=%f val=%.20f sol=%.20f)" % (ymin,ymax,yval,v)

def entropy2pd(tentropy, symbols_nr, pd=None, prob_min=__prob_min, entropy_err=.005):
	""" Create a probability distribution (pd) for a set of symbols that will
	    adhere to the given entropy value

		tentropy    : target entropy value
		symbols_nr  : number of symbols
		prob_min    : minum value for probabilities
		entropy_err : margin for error between the given and pd entropy

		The basic concept is to choose two probabilities from the list and
		modify them so that we are close to the target entropy.

	    returns a list of symbols_nr probabilities
	"""
	# sanity checks
	if (tentropy > entropy_max(symbols_nr)):
		raise ValueError, "entropy specified (%f) is too high" % tentropy
	if (tentropy < entropy_min(symbols_nr,prob_min)):
		raise ValueError, "entropy specified (%f) is too small" % tentropy

	#from gnuplot_simple import BarsMultiple
	#prob_max = 1 - ((symbols_nr-1)*prob_min)
	#bm = BarsMultiple(y_max=prob_max, y_min=prob_min)

	# Choose an initial probability distribution
	if pd is None:
		pd = e2pd_initial_pd(symbols_nr, prob_min)
	iterations = 0
	alpha = beta = 1.3
	while True:
		pd.sort()
		#if iterations % 7 == 0: bm.add("%013d" % iterations, pd )
		entropy_pd = entropy(pd)
		de = tentropy - entropy_pd
		if iterations % 512 == 1: 
			alpha = uniform(.5, 10)
			beta  = uniform(.5, 10)
		if fabs(de) <= entropy_err:
			break
		elif tentropy > entropy_pd:
			#print 'INC '
			p0 = pd.pop(int((len(pd))*(betavariate(alpha,beta))))
			p1 = pd.pop(int((len(pd))*(betavariate(beta,alpha))))
			s = p0 + p1
			a = min(p0,p1)/s
			#assert a<.5
			xmin = a
			xmax = .5
		else:
			#print 'DEC '
			p0 = pd.pop(int((len(pd))*(betavariate(alpha,beta))))
			p1 = pd.pop(int((len(pd))*(betavariate(alpha,beta))))
			s = p0 + p1
			a = min(p0,p1)/s
			xmin = prob_min/s
			xmax = a

		q0 = uniform(xmin,xmax)
		pd.append(q0*s)
		pd.append((1-q0)*s)

		iterations += 1

	return pd

def closerint(val):
	i = int(val)
	if val - i > .5:
		i+= 1
	return i

def e2pd_rand_initial_pd(symbols_nr):
	 return e2pd_initial_pd(
	           symbols_nr,
	           shuffle = randint(0,symbols_nr*2),
	           initial=sample(("min", "max"), 1)[0]
	)

def entropy_mkfile(pd, fname, fsize, symbols_nr=256):
	fd = os.open(fname, os.O_CREAT | os.O_RDWR)
	os.ftruncate(fd, fsize)
	os.fsync(fd)
	map = mmap.mmap(fd, fsize)

	remaining = fsize
	t0 = time()
	while True:
		s = min(1024*1024,remaining)
		map.write( ''.join((chr(bisect_left(pd, random())) for i in xrange(s) )) )
		remaining -= s
		print "rate: %f Mbyte/sec" % ((float(fsize - remaining) / (time() - t0))/(1024*1024))
		if remaining == 0:
			break

	map.flush()
	map.close()
	os.fsync(fd)
	os.close(fd)

def mkfile(entropy, fname, fsize, symbols_nr=256, prog="./pd_mkfile"):
	pd = entropy2pd(entropy, symbols_nr, e2pd_rand_initial_pd(symbols_nr))
	for i in xrange(1,len(pd)):
		pd[i] += pd[i-1]
	f = os.popen("%s %s %d" % (prog, fname, fsize), 'w')
	for p in pd:
		f.write("%30.25f\n" % p)
	f.close()

if __name__ == '__main__':
	from sys import argv, exit
	if len(argv) < 4:
		print "Usage: %s <entropy> <fname> <fsize>" % argv[0]
		exit(1)

	en = float(argv[1])
	fname = argv[2]
	fsize = long(argv[3])
	mkfile(en, fname, fsize)

