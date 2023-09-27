import sys
from import_class import *

if __name__ == '__main__':
    tester = Import()
    length = len(sys.argv)
    for i in range(1, length):
        tester.importall(sys.argv[i])
