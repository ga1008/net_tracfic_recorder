import math

import numpy as np


"""
弗雷歇距离
"""


def calculate_euclid(point_a, point_b):
    """
    Args:
        point_a: a data point of curve_a
        point_b: a data point of curve_b
    Return:
        The Euclid distance between point_a and point_b
    """
    return math.sqrt((point_a - point_b) ** 2)


def calculate_frechet_distance(dp, i, j, curve_a, curve_b):
    """
    Args:
        dp: The distance matrix
        i: The index of curve_a
        j: The index of curve_b
        curve_a: The data sequence of curve_a
        curve_b: The data sequence of curve_b
    Return:
        The frechet distance between curve_a[i] and curve_b[j]
    """
    if dp[i][j] > -1:
        return dp[i][j]
    elif i == 0 and j == 0:
        dp[i][j] = calculate_euclid(curve_a[0], curve_b[0])
    elif i > 0 and j == 0:
        dp[i][j] = max(calculate_frechet_distance(dp, i - 1, 0, curve_a, curve_b),
                       calculate_euclid(curve_a[i], curve_b[0]))
    elif i == 0 and j > 0:
        dp[i][j] = max(calculate_frechet_distance(dp, 0, j - 1, curve_a, curve_b),
                       calculate_euclid(curve_a[0], curve_b[j]))
    elif i > 0 and j > 0:
        dp[i][j] = max(min(calculate_frechet_distance(dp, i - 1, j, curve_a, curve_b),
                           calculate_frechet_distance(dp, i - 1, j - 1, curve_a, curve_b),
                           calculate_frechet_distance(dp, i, j - 1, curve_a, curve_b)),
                       calculate_euclid(curve_a[i], curve_b[j]))
    else:
        dp[i][j] = float("inf")
    return dp[i][j]


def get_similarity(curve_a, curve_b):
    dp = [[-1 for _ in range(len(curve_b))] for _ in range(len(curve_a))]
    similarity = calculate_frechet_distance(dp, len(curve_a) - 1, len(curve_b) - 1, curve_a, curve_b)
    return max(np.array(dp).reshape(-1, 1))[0], similarity


if __name__ == '__main__':
    gs, sim = get_similarity(
        # [1, 2, 3.1, 4, 5.3, 6, 7.4, 8, 9.2],
        [9.2, 8, 7.4, 6.5, 5.3, 4, 3.1, 2, 1.1],
        [9.4, 8.2, 7.6, 6.7, 5.5, 4.2, 3.3, 2.2, 1.3],
        # [1, 2.2, 3, 4.1, 5, 6.1, 7, 8.6, 9]
    )
    print(gs)
    print(sim)
