import numpy

"""
欧几里得度量
"""


def EDD(l1, l2):
    return numpy.sqrt(numpy.sum(numpy.square(numpy.array(l1) - numpy.array(l2))))


if __name__ == '__main__':
    print(EDD(
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6],
    ))
