import random
x = 80
x_min, x_max = 0, 100

for i in range(10000):
    x1 = random.randint(-10, 10)
    while x+x1 > x_max or x+x1 < x_min:
        x1 = random.randint(-10, 10)
    x += x1
    print(i, x)

movement = {100:[5,3], 200:5}
print(movement[100][0])

print(random.random())

ab_list = [5, 14, 6]
for a in ab_list[0:1]:
    print(a)
print("A")
for a in ab_list[1:]:
    print(a)

print(ab_list[1:])

a = [1, 2, 3]
b = [4, 5, 6]
for (c, d) in zip(a, b):
    print(c, d)

abc = "asd"
if abc:
    print("A")