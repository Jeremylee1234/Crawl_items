def get_data():
    results = [1,2,3,4,5,6,7,7,7,7,7,7]
    while len(results) >= 1:
        data = results.pop()
        results.append(data)
        yield data

for i in get_data():
    print(i)