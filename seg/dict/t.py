#-*-coding:utf-8-*- 
file = open('people','rb')
file2 = open('people.dict','rb')
s = []
s2 =[]
while True:
    line = file.readline()
    if line:
            s.append(line.strip('\r\n').strip('\n').split(' \t')[0])
    else:
            break

while True:
    line = file2.readline()
    if line:
            s2.append(line.strip('\r\n').strip('\n').split(' \t')[0])
    else:
            break

line =  list(set(s).difference(set(s2))) # b中有而a中没有的
for l in line:
	print l
