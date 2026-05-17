# num = 5
# for i in range(1 ,11):
#     mul = num * i
#     print(mul)

# num = 0
# for i in range(1, 51):
#     num += 1
    
#     if num % 3 == 0 and num % 5 == 0:
#         print("FizzBuzz")
#     elif num % 3 == 0:
#         print("Fizz")
#     elif num % 5 == 0:
#         print("Buzz")
#     else :
#         print(num)
        
# print("keep going")
# n = 10
# while n >=1:
#     print(n)
#     n = n - 1

# count = 0
# for i in range(1, 51):
#     if i % 2 == 0:
#         count += i
# print(count)
    
    
# count = 0
# for i in range(1, 51):
#     if i % 2 == 0:
#         count += i

# numbers = [3, 67, 23, 8, 99, 41, 5]
# long = numbers[0]
# for i in numbers:
#     if i > long:
#         long = i
# print(long)

# num = []
# count = 0
# numbers = [4, 15, 7, 23, 1, 11, 9, 42]
# for i in numbers:
#     if i > 10:
#         num.append(i)
#         count = num
       
# print(len(count))

# num = []
# numbers = [1, 2, 3, 4, 5]
# for i in numbers:
#     num.append(i)
# print(num[::-1])

# unique = []
# numbers = [1, 3, 2, 3, 5, 1, 4, 2]

# for i in numbers:
#     if i not in unique:
#         unique.append(i)
# print(unique)

# num = []
# greater = []
# smaller = []
# numbers = [3, 15, 7, 23, 1, 11, 9, 42]
# for i in numbers:
#     if i < 10:
#         smaller.append(i)
#     elif i > 10:
#         greater.append(i)
# print(smaller)
# print(greater)
        
# numbers = [3, 67, 23, 8, 99, 41, 5]
# largest = numbers[0]
# for i in numbers:
#     if i > largest:
#         largest = i
# second = numbers[0]
# for i in numbers:
#     if i > second and i < largest:
#         second = i
# print(second)

# for i in range(1 , 21):
#     if i % 2 == 0 and i % 3 == 0:
#         print(i)


# for i in range(1 , 6):
#     for x in range(1, 11):
#       product = i * x
#       print(product, end=" ")
#     print()



# # Outer loop: Iterates through the table numbers (1 to 5)
# for i in range(1, 6):
#     print(f"--- Multiplication Table for {i} ---")
    
#     # Inner loop: Iterates through multipliers (1 to 10)
#     for j in range(1, 11):
#         product = i * j
#         print(f"{i} x {j} = {product}")
    
#     # Adds a blank line between tables for readability
#     print() 


n = 5
for i in range(1, 6):
    print("* " * i)