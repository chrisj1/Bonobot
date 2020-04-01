from math import *

def method1(x,y):
	s = 0
	count = 0
	while y > 0:
		if y & 1 is 1:
			s += y << count
		count += 1
		y=y>>1