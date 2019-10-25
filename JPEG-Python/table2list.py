
reslist = []

for i in range(12):
    line = input()
    strlist = line.split(' ')
    reslist.append((int(strlist[0]), int(strlist[1]), strlist[2]))

print(reslist)