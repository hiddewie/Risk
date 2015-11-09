import random
import collections
import functools


class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)


def dice(n):
	if n == 0:
		return [[]]
	ret = []
	for i in dice(n - 1):
		for j in range(6):
			ret.append(i + [j + 1])
	return ret

def war(a, b):
	a = sorted(a)
	a.reverse()
	b = sorted(b)
	b.reverse()
	l = min(len(a), len(b))

	remove = [0, 0]
	for i in range(l):
		if a[i] > b[i]:
			remove[1] += 1
		else:
			remove[0] += 1
	return tuple(remove)

def bestDefendStrategy():
	"""
	Calculating the best defence strategy
	"""

	q = dict()
	p = dict()

	for d in dice(3):
		i = sorted(d)
		i.reverse()

		if (i[0], i[1]) not in p:
			p[(i[0], i[1])] = 0.0
		p[(i[0], i[1])] += 1 / 6 ** 3

		total = 0
		gain = 0
		for j in dice(2):
			w = war(i, j)
			total += 1
			gain += (w[0] - w[1])
		bestGain = gain / total;
		total = 0
		gain = 0
		for j in dice(1):
			w = war(i, j)
			total += 1
			gain += (w[0] - w[1])
		q[(i[0], i[1])] = ('•' if gain / total > bestGain else '••', gain / total, bestGain)
		#print(i, '/' if gain / total > bestGain else '//', 'single', gain / total, 'double:', bestGain)

	for i in range(1, 7):
		print(i, end=' & ')
		for j in range(1, 7):
			if (i, j) in q:
				print('%1.2f & %1.2f' % (q[(i, j)][1], q[(i, j)][2]), '& ' if j < 6 else ' \\\\ ', end = '')
			else:
				print('&', '& ' if j < 6 else ' \\\\ ', end = '')
		print()

	for i in range(1, 7):
		print(i, end=' & ')
		for j in range(1, 7):
			if (i, j) in q:
				print((('\\textbullet' if q[(i, j)][1] >= q[(i, j)][2] else '\\textbullet\\textbullet') + ' & %1.2f ') % (p[(i, j)], ), '& ' if j < 6 else ' \\\\ ', end = '')
			else:
				print('&', '& ' if j < 6 else ' \\\\ ', end = '')
		print()


def worstAttackerGain(a, b):
	"""
	Calculating the worst gain when attacking
	"""

	aDice = optimalAttackDice(a)

	totalGain = 0
	for d in dice(aDice):
		i = sorted(d)
		i.reverse()

		defenderDice = optimalDefenceDice(d, a, b)

		total = 0
		betweenGsin = 0
		for j in dice(defenderDice):
			w = war(i, j)
			total += 1
			betweenGsin += (w[1] - w[0])
		totalGain += 1 / (6 ** aDice) *  betweenGsin / total

	return totalGain

def optimalAttackDice(armies):
	if armies == 1:
		return 0
	if armies == 2:
		return 1
	elif armies == 3:
		return 2
	elif armies >= 4:
		return 3

def optimalDefenceDice(aDice, a, b):
	# Choice from 1 or 2 dice
	if b == 1:
		return 1
	elif b >= 1:
		if len(aDice) <= 1:
			return 2
		else:
			if aDice[1] > 3:
				return 1
			else:
				return 2

def randomDice(n):
	return [random.randint(1, 6) for _ in range(n)]

@memoized
def PChange(a, b):

	if a >= 4 and b >= 2:
		return {(0, 1): 0.36574074074074125, (2, 0): 0.19740226337448577, (1, 0): 0.1342592592592595, (1, 1): 0.1669238683127572, (0, 2): 0.1356738683127572}
	#{(0, 1): 474, (2, 0): 1535, (1, 0): 174, (1, 1): 1298, (0, 2): 1055}

	ret = dict()

	aDice = optimalAttackDice(a)
	aP = 1 / (6 ** aDice)
	for i in dice(aDice):
		partialP = dict()
		total = 0
		for j in dice(optimalDefenceDice(i, a, b)):
			w = war(i, j)
			if w not in partialP:
				partialP[w] = 0
			partialP[w] += 1
			total += 1
		for w, part in partialP.items():
			if w not in ret:
				ret[w] = 0.0
			ret[w] += aP * part / total
	return ret

@memoized
def PWin(a, b):
	#print('PWin', a, b)
	if a == 0 or a == 1:
		return 0.0
	elif b == 0:
		return 1.0

	pc = PChange(a, b).items()
	return sum(PWin(a-w[0], b-w[1]) * p for w, p in pc)

def printPWins(ma):
	print('ATT \ DEF', end='')
	for i in range(0, ma + 1):
		print('   %-2d  ' % (i,), end='')
	print()
	for a in range(1, ma + 1):
		#print('%-8d' % (a,), end='')
		for b in range(0, ma + 1):
			#print(100*PWin(a, b), end=' ')
			print('{', a, ',',b, ',', '%.10f' % (PWin(a, b), ), '},', end=' ', sep='')
		print()

def per(p):
	return '% 5.2f ' % (p,)

def printAttackerGain ():
	for i in range(1, 6):
		print(i, '& ', end='')
		for j in range(1, 6):
			print('%1.2f ' % worstAttackerGain(i, j), end='& ' if j < 5 else ' \\\\ ', sep='')
		print()

def printPChange():
	for a in range(1, 5):
		print(a, end=' & ')
		for b in range(1, 5):
			print('\\begin{tabular}{ll}')
			first = False;
			for w, p in PChange(a, b).items():
				if not first:
					first = True
				else:
					print('\\\\', end='')
				print(w, '%1.2f' % p,end='')
			print('\\end{tabular}', end='')
			print(end='& ' if b < 4 else ' \\\\ ')
		print('\\hline')

#bestDefendStrategy()
#printAttackerGain()
#printPWins(15)
#printPChange()
#for a in range(1, 5):
#	for b in range(1, 5):
#		print(a, b, sum((w[1] - w[0]) * p for w, p in PChange(a,b).items()))
for a in range(1, 15):
   print(PWin(a, a))
