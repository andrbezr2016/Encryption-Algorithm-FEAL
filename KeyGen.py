import random

#тест Миллера—Рабина
def randKey():
	K=[]
	rng = random.SystemRandom()
	for i in range(8):
		K.append(random.randint(0, 255))
	return K

def miller_rabin(n, k=1000000):
	if n == 2:
		return True
	if not n & 1:
		return False #проверка на четность

	def check(a, s, t, n):
		x = pow(a, t, n) #(a^t)mod(n)
		if x == 1:
			return True #на следующую итерацию по k
		for i in range(s - 1):
			if x == n - 1:
				return True #на следующую итерацию по k
			x = pow(x, 2, n)
		return x == n - 1

	s = 0
	t = n - 1

	while t % 2 == 0:
		t >>= 1 # t=t/(2^1)
		s += 1

	for i in range(k):
		a = random.randrange(2, n - 1) #[2;n-2]
		if not check(a, s, t, n):
			return False
	return True

K=0
i=1
while True:
	K=randKey()
	if miller_rabin(int(''.join(str(i) for i in K)))==True:
		open('Key.txt',mode='w',encoding="latin-1").write(' '.join(str(i) for i in K))
		break
	else:
		i+=1
		continue
print(K)
print(i)
