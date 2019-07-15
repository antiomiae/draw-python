import sys
from draw_file import DrawFile

if __name__ == '__main__':
    fname = sys.argv[1]
    print(fname)
    file = DrawFile.from_path(fname)

    print(file._doc_data)
