"""
Credit:  
    BY Terry Davis 
    https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python

Usage:
>>> size = get_folder_size("c:/users/tdavis/downloads")
>>> print(size)
5.81 GB
>>> size.GB
5.810891855508089
>>> size.gigabytes
5.810891855508089
>>> size.PB
0.005674699077644618
>>> size.MB
5950.353260040283
>>> size
ByteSize(6239397620)
"""
################################################
from genericpath import isdir
from pathlib import Path
import os


def get_folder_size(folder):
    # using pathlib.Path
    return ByteSize(sum(file.stat().st_size for file in Path(folder).rglob('*')))
    

class ByteSize(int):

    _kB = 1024
    _suffixes = 'B', 'kB', 'MB', 'GB', 'PB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.kB = self / self._kB**1
        self.megabytes = self.MB = self / self._kB**2
        self.gigabytes = self.GB = self / self._kB**3
        self.petabytes = self.PB = self / self._kB**4
        *suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 <= getattr(self, suffix) < self._kB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))

    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other))   


if __name__ == "__main__":

    path_to_walk = Path("D:\\dev\\4_python3_learn\\file")
    # path_to_walk = Path("D:\\dev\\4_python3_learn"}

    size = get_folder_size(path_to_walk)
    print(size, path_to_walk)

    # Using pathlib.Path to walk
    print('---using pathlib.Path ------')
    for path in path_to_walk.iterdir():
        if path.is_dir():
            print(get_folder_size(path), path)

    # Using o.scandirs to walk through the dirs
    print('---using os.scandirs()------')
    for f in os.scandir(path_to_walk):
        if f.is_dir():
            print(get_folder_size(f.path), f.path)
