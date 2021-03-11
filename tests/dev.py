import os


def print_paths():
    print('PRINT PATHS:')
    print('current file path:', __file__)
    print('cwd:', os.getcwd())
    print('caller cwd:', traceback.extract_stack()[-2][0])

import traceback
def get_caller_filename():
   # last element ([-1]) is me, the one before ([-2]) is my caller. The first element in caller's data is the filename
   return traceback.extract_stack()[-2][0]


class A:
    def __init__(self):
        self.var = 1312

    def __new__(cls, type=None):
        if type is int:
            return 2
        obj = object.__new__(cls)
        obj.__init__()
        return obj


if __name__ == '__main__':
    a = A(type=int)
    print(a)
    # print(a.var)
