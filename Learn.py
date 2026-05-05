import math
import random
y = 23
x = 3.23
z = 2 + 4j
w = "23"
print(w * 2)
print(type(y))
print(type(x))
print(type(z))
w = int(w)
print(w * 3)
c = 35457
print(float(c))
print(complex(y,c))
print(4 ** 4)
q = 45
q += 45
print(q)
price = 49.9956376
print(round(price))
print(math.floor(price))
print(math.ceil(price))
print(math.trunc(price))
print(random.randint(1,10))
f = 5.00
print(f.is_integer())
print(isinstance(f, int))
rand_num = random.randint(1, 100)
print(rand_num)
if rand_num % 2 == 0:
    print("its an even number")
else:
    print("its an odd number")
