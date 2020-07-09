import numpy as np
from scipy import stats

"""
皮尔森相关系数
"""


def PCC(l1, l2):
    return stats.pearsonr(l1, l2)


if __name__ == '__main__':
    print(PCC(
        [1, 2, 3, 4, 5, 6],
        [1, 2, 3, 4, 5, 6]
    ))
