# email = ""
# num = "6653475"
# user = ""
# print(any([email, num, user]))  # True
# print(all([email, num, user]))  # False

# print("hello".endswith("l"))

my_list = ["apple", "banana", "cherry"]
print(*my_list, sep="\n")

my_list = ["apple", "banana", "cherry"]
print("\n".join(my_list))

from pprint import pprint

complex_list = [{'id': 1, 'data': [10, 20]}, {'id': 2, 'data': [30, 40]}]
pprint(complex_list)


numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Calculate the midpoint
mid = len(numbers) // 2

# Split using slicing
list_one = numbers[:mid]
list_two = numbers[mid:]

print("First Half:", list_one)
print("Second Half:", list_two)


