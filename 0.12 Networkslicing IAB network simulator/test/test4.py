x = "list_0, list_1, list_2, list_3, list_4"

for i in range(5):
    exec(f'list_{i} = [{i*10}, {i^3}, {i+3}]')
exec(f'print({x})')

a = {"test": [1, 2, 3, 4]}
print(a["test"])

def make():
    a, b, c, d = [1], [2], [3], [4]
    asd = {"a": [1, 2], "b": [3, 4]}
    return asd

def accept(**stats):
    print(stats["b"])

accept(**make())

list_a = ["asd", "asgw"]
for i in list_a:
    exec(f"list_{i} = []")
exec(f"print(list_asd)")