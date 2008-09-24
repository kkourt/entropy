from itertools import imap, chain
from math import log, fabs
from random import random, Random, randint

R = Random()
uniform = R.uniform

def gcd(a, b):
	while b != 0:
		tmp = b
		b = a % b
		a = tmp
	return a

def lcm(a,b):
	return (a*b) // gcd(a,b)

def reduce_rational(rtuple):
	rgcd = gcd(*rtuple)
	return (rtuple[0] // rgcd, rtuple[1] // rgcd)

def reduce_rationals(plist):
	plcm = reduce(lcm, imap(lambda p: p[1], imap(reduce_rational, plist)))
	return (map(lambda rtuple: rtuple[0]*(plcm // rtuple[1]), plist), plcm)

def pl2fl(pdict, total_entries, force_distribution=False):
	""" Convert probability lists to frequency lists 
	pdict: symbol -> rational tuple
	returns: symbol -> frequency
	remaining entries are assigned to most frequent symbols
	"""
	# create list of rational probabilities with the same (minimum) denominator
	slist, plist = zip(*pdict.iteritems())
	pnumerators, pdenominator = reduce_rationals(plist)
	
	# make sure that the probabilities add up to 1
	assert reduce(lambda x,y: x+y, pnumerators) == pdenominator 

	# assign entries without messing with the distribution
	m = total_entries // pdenominator
	freqs = map(lambda x: x*m, pnumerators)
	fl = dict((slist[i], freqs[i]) for i in xrange(len(freqs)))
	if force_distribution:
		return fl
	
	# check if there are remaining entries
	remaining = total_entries % pdenominator
	if remaining == 0:
		return fl

	# assign remaining entries by adding them to the most frequent 
	# symbols (breaks distribution)
	i = 0
	slist = list(slist)
	slist.sort(cmp=lambda s0,s1: cmp(pdict[s0],pdict[s1])) 
	while True:
		freq = min(remaining, pnumerators[i])
		fl[slist[i]] += freq
		remaining -= freq 
		if remaining <= 0:
			break
		i += 1

	return fl

def entropy(sym_prob):
	#sym_prob = list(sym_prob)
	#print sym_prob
	return reduce(lambda x,y: x+y, imap(lambda p: -p*log(p,2), sym_prob))

def entropy_max(symbols_nr):
	symbols_nr_fl = float(symbols_nr)
	return entropy(( 1.0/symbols_nr_fl for i in xrange(symbols_nr) ))

def entropy_min(symbols_nr, prob_min):
	prob_max = 1 - ((symbols_nr-1)*prob_min)
	return entropy(chain( (prob_max, ), (prob_min for i in xrange(symbols_nr-1)) ))

def e2pd_initial_pd(symbols_nr, prob_min=.00001, retries_limit=46):
	symbols_nr_fl = float(symbols_nr)
	return [ 1.0/symbols_nr_fl for i in xrange(symbols_nr) ]
#	ret = []
#	vsum = 0.0
#	vmin = 1.0
#	retries = 0
#	while retries < retries_limit:
#		for i in xrange(symbols_nr):
#			v = 1 - random()
#			vsum += v
#			vmin = min(vmin, v)
#			ret.append(v)
#
#		if (vmin/vsum) >= prob_min:
#			ret = [ x/vsum for x in ret ]
#			return ret
#		retries += 1
#		print "Retrying: %d" % retries
#
#	assert False

def _plog2p(p):
	return p*log(p,2) if p != 0.0 else 0.0

def _de(a, b, sum):
	return sum*(_plog2p(a) + _plog2p(1-a) - _plog2p(b) - _plog2p(1-b))

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
			#print "Found solution in %d iterations" % iterations
			return ymed
		elif v > yval:
			ymin = ymed
		else:
			ymax = ymed

		iterations += 1
		if iterations > limit_iterations:
			raise ValueError, "Unable to find a solution (min=%f max=%f val=%.20f sol=%.20f)" % (ymin,ymax,yval,v)

def entropy2pd(tentropy, symbols_nr, prob_min=.00001, entropy_err=.001):
	""" Create a probability distribution (pd) for a set of symbols that will 
	    adhere to the given entropy value
		tentropy    : target entropy value
		symbols_nr  : number of symbols
		prob_min    : minum value for probabilities
		entropy_err : margin for error between the given and pd entropy
	"""
	# sanity checks
	if (tentropy > entropy_max(symbols_nr)):
		raise ValueError, "entropy specified (%f) is too high" % tentropy
	if (tentropy < entropy_min(symbols_nr,prob_min)):
		raise ValueError, "entropy specified (%f) is too small" % tentropy
	
	pd = e2pd_initial_pd(symbols_nr, prob_min)
	while True:
		pd.sort()
		entropy_pd = entropy(pd)
		de = tentropy - entropy_pd
		if fabs(de) <= entropy_err:
			return pd
		elif tentropy > entropy_pd:
			p1,p0 = (pd.pop(-1), pd.pop(0))
			s = p0 + p1
			a = p0/s
			assert a<.5
			q0 = uniform(a,.5)
			#de_max = entropy_pd + _de_max(a, s)
			#de_new = uniform(0, min(2*de,de_max))
			#q0 = _de_solve(a, s, de_new)
		else:
			idx = randint(0,len(pd)-2)
			p0 = pd.pop(idx)
			p1 = pd.pop(idx)
			s = p0 + p1
			a = p0/s
			q0 = uniform(prob_min,a)
			#de_min = _de_min(a, s, prob_min)
			#de_new = uniform(max(2*de,de_min), 0)
			#q0 = _de_solve(a, s, de_new)

		pd.append(q0*s)
		pd.append((1-q0)*s)
	
	return pd

if __name__ == '__main__':
#	se = 0
#	loops = 10000
#	for i in xrange(loops):
#		pd = e2pd_initial_pd(256)
#		e = entropy(pd)
#		se += e
#	print "%f" % (se/float(loops))
#	probs = dict([
#		 ('A',(1,2)),
#		 ('B',(1,4)),
#		 ('C',(1,4)),
#	])
#	freqs = pl2fl(probs, 1024)
#	print freqs
	pd = entropy2pd(7.9, 256)
	pass
