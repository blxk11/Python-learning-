# num = 5
# for i in range(1 ,11):
#     mul = num * i
#     print(mul)

num = 0
for i in range(1, 51):
    num += 1
    
    if num % 3 == 0 and num % 5 == 0:
        print("FizzBuzz")
    elif num % 3 == 0:
        print("Fizz")
    elif num % 5 == 0:
        print("Buzz")
    else :
        print(num)
    