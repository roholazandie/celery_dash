from sample import add

#result = add.delay(4, 4)

#print(result.ready)
result = add.delay(4, 99)
while not result.ready():
    print("waiting")
    pass


s = result.get()
print(s)
