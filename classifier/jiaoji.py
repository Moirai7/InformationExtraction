#coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

confidence = {}

def get_small(sourcePath, extractPath, destPath, point):
    source = open(sourcePath, "r")
    for line in source:
        arr = line.split()
        key = arr[0].strip(" \n\t\s")
        if len(arr) < 4:
            continue
        value = arr[3].strip(" \n\t\s")
        confidence[key] = value

    extract = open(extractPath, "r")
    dest = open(destPath, "w")
    for line in extract:
        arr = line.split()
        key = arr[0].strip(" \n\t\s")
        if len(arr) < 4:
            continue
        score = confidence.get(key)
        if score > point:
            dest.write(line)


if __name__ == "__main__":
    get_small(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
