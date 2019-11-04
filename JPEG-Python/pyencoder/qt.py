import numpy as np

LuminanceQuantizationTable = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                                       [12, 12, 14, 19, 26, 58, 60, 55],
                                       [14, 13, 16, 24, 40, 57, 69, 56],
                                       [14, 17, 22, 29, 51, 87, 80, 62],
                                       [18, 22, 37, 56, 68, 109, 103, 77],
                                       [24, 35, 55, 64, 81, 104, 113, 92],
                                       [49, 64, 78, 87, 103, 121, 120, 101],
                                       [72, 92, 95, 98, 112, 100, 103, 99]], dtype=np.int)

ChrominanceQuantizationTable = np.array([[17, 18, 24, 47, 99, 99, 99, 99],
                                         [18, 21, 26, 66, 99, 99, 99, 99],
                                         [14, 13, 16, 24, 40, 57, 69, 56],
                                         [24, 26, 56, 99, 99, 99, 99, 99],
                                         [47, 66, 99, 99, 99, 99, 99, 99],
                                         [99, 99, 99, 99, 99, 99, 99, 99],
                                         [99, 99, 99, 99, 99, 99, 99, 99],
                                         [99, 99, 99, 99, 99, 99, 99, 99]], dtype=np.int)


def zigzagOrder(block):
    """
    对一个经过量化和差分的8x8 block 进行之字型排列
    :param block: 一个经过量化和差分的8x8 block - np.int
    :return: 之字型排列的 block - int list
    """
    retblk = []
    for sum in range(15):
        if sum < 8:
            if sum%2 == 0:
                for col in range(sum+1):
                    retblk.append(block[sum-col, col])
            else:
                for row in range(sum+1):
                    retblk.append(block[row, sum-row])
        else:
            if sum%2 == 0:
                for col in range(sum-7, 8):
                    retblk.append(block[sum-col, col])
            else:
                for row in range(sum-7, 8):
                    retblk.append(block[row, sum-row])

    return retblk

lt =  zigzagOrder(ChrominanceQuantizationTable)
for i in range(len(lt)):
    if i % 8 == 0:
        print("\n")
    print(hex(lt[i]), end = ', ')