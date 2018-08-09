with open('url.dat', 'r') as f:
    data = f.read().split('\n')

for e in data:
    print e