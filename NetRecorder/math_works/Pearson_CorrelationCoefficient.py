import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

"""
皮尔森相关系数
"""


def PCC(l1, l2):
    return stats.pearsonr(l1, l2)


if __name__ == '__main__':
    lis = []
    height_score = {}
    for i in range(1000):
        l1 = [random.randint(0, 9) for _ in range(5)]
        l2 = [random.randint(0, 9) for _ in range(5)]
        res = PCC(
            # [1, 2, 9, 4, 5, 6, 8],
            # [1, 2, 3, 4, 5, 6, 8],
            l1,
            l2
        )
        lis.append(res[0])
        if res[0] >= 0.95:
            height_score[f"{res[0]}"] = [l1, l2]

    lis.sort()
    for x in lis:
        # if isinstance(x, type(np.nan)):
        #     x = 0
        s = "#" if x > 0 else "-"
        print(round(x, 5), s * abs(round(x*100)))

    for sc, num_liss in height_score.items():
        print("score: ", sc)
        yd1 = num_liss[0]
        yd2 = num_liss[1]
        xd = [x for x in range(len(yd1))]
        print("l1: ", yd1)
        print("l2: ", yd2)
        plt.plot(xd, yd1, color='red', linewidth=2.0, linestyle='--')
        plt.plot(xd, yd2, color='blue', linewidth=2.0, linestyle='-')
        plt.show()
        print()

    print(f"height_score rate: {round(len(height_score)/1000 * 100, 2)}")
