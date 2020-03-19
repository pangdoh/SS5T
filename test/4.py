b = b'dajdj123'
bb = b.split(b'123')
for n in range(len(bb)):
    if n == len(bb) - 1:
        break
    print(bb[n])