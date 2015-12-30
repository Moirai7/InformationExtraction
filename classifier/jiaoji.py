#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_small(sourcePath, extractPath, destPath, point):
    source = open(sourcePath, "r")
    extract = open(extractPath, "r")
    dest = open(destPath, "w")
    for line in source:
	confidence = {}
	check = True
        arr = line.split()
	if len(arr)==0:
		continue
	line2 = extract.readline().split()
        key = arr[0].strip(" \n\t\s")
        if len(arr) < 4:
            continue
	k=0
	while k < (len(arr)-2):	
	        value = arr[k+3].strip(" \n\t\s")
	        o = arr[k+2].strip(" \n\t\s")
		value2 = line2[k+3].strip(" \n\t\s")
		o2 = line2[k+2].strip(" \n\t\s")
		if o==o2 and float(value2)>point:
			confidence[o]=value
			check=False
		k+=2
	if check is False:
		line=arr[0]+'\t'+arr[1]+'\t'
		for k,v in confidence.iteritems():
			line+=k+' '+v+' '
		dest.write(line+'\n')

    #for line in extract:
    #    arr = line.split()
	#if len(arr)==0:
	#	continue
        #key = arr[0].strip(" \n\t\s")
        #if len(arr) < 4:
        #    continue
        #score = confidence.get(key)
        #if score > point:
        #    dest.write(line)


if __name__ == "__main__":
    get_small(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))
