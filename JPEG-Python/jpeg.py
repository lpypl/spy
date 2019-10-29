import copy

import numpy as np
import cv2
import math

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

LuminanceDCCoefficientDifferencesTable = [(0, 2, '00'),
                                          (1, 3, '010'),
                                          (2, 3, '011'),
                                          (3, 3, '100'),
                                          (4, 3, '101'),
                                          (5, 3, '110'),
                                          (6, 4, '1110'),
                                          (7, 5, '11110'),
                                          (8, 6, '111110'),
                                          (9, 7, '1111110'),
                                          (10, 8, '11111110'),
                                          (11, 9, '111111110')]

ChrominanceDCCoefficientDifferencesTable = [(0, 2, '00'),
                                            (1, 2, '01'),
                                            (2, 2, '10'),
                                            (3, 3, '110'),
                                            (4, 4, '1110'),
                                            (5, 5, '11110'),
                                            (6, 6, '111110'),
                                            (7, 7, '1111110'),
                                            (8, 8, '11111110'),
                                            (9, 9, '111111110'),
                                            (10, 10, '1111111110'),
                                            (11, 11, '11111111110')]

# 4:2:2
def ycrcb2sample(ycrcb):
    """
    对YCrCb进行取样(4:2:2)
    :param ycrcb: origin YCrCb
    :return: 4-Y, 2-Cr, 2-Cb
    """
    y = ycrcb[:, :, 0]
    cr = ycrcb[:, 0:ycrcb.shape[1]:2, 1]
    cb = ycrcb[:, 0:ycrcb.shape[1]:2, 2]
    return y, cr, cb


def sample2ycrcb(y, cr, cb):
    """
    将4:2:2格式的Y,Cr,Cb还原成YCrCb矩阵
    :param y: Y
    :param cr: Cr
    :param cb: Cb
    :return: YCrCb
    """
    newcr = np.ones((cr.shape[0], cr.shape[1]*2))
    newcr[:, 0:newcr.shape[1]:2] = cr
    newcr[:, 1:newcr.shape[1]:2] = cr

    newcb = np.ones((cb.shape[0], cb.shape[1]*2))
    newcb[:, 0:newcb.shape[1]:2] = cb
    newcb[:, 1:newcb.shape[1]:2] = cb

    return np.array([y, newcr, newcb]).swapaxes(0,1).swapaxes(1,2).astype(np.uint8)


def dct(data):
    """
    dct
    :param data:8x8 DATA - np.uint8
    :return: 8x8 dct DATA - np.float32
    """
    dataf = data.astype(np.float32)
    dataf_dct = cv2.dct(dataf)
    return dataf_dct


def idct(dataf_dct):
    """
    idct
    :param dataf_dct: 8x8 DATA - np.float32
    :return: 8x8 idct DATA - np.uint8
    """
    dataf_idct = cv2.idct(dataf_dct)
    data_idct = dataf_idct.astype(np.uint8)
    return  data_idct


def data2blocks(data):
    """
    将图像数据矩阵转换为8x8的BLOCK，不足8x8的数据会填充0
    :param data:图像数据矩阵（二维，单个通道）
    :return:blocks(block list),height(填充后的实际高度), width（填充后的实际宽度）
    """
    height, width = data.shape

    # 扩充
    newdata = np.zeros(((height+7)//8 * 8, (width+7)//8 * 8))
    newdata[0:height, 0:width] = data
    data = newdata
    height, width = data.shape

    assert height%8==0 and width%8==0

    blocks = []
    for r in range(0, height, 8):
        for c in range(0, width, 8):
            blocks.append(data[r:r+8, c:c+8])
    return blocks, height, width


def blocks2data(blocks, height, width):
    """
    将8x8 BLock list 还原成图像数据
    :param blocks: block list
    :param height: block data height
    :param width: block data width
    :return:
    """
    assert height%8==0 and width%8==0
    bh = width//8
    bv = height//8

    data = np.ones((height, width), dtype=np.uint8)
    for row in range(bv):
        for column in range(bh):
            data[row*8:(row+1)*8, column*8:(column+1)*8] = blocks[row*bh+column]

    return data

def quantifyBlock(originBlock, type):
    """
    dct并量化一个8x8 BLock
    :param originBlock: 8x8 block
    :param type: ‘H’ for luminance, 'C' for Chrominance
    :return: dct并量化后的 8x8 block - np.int
    """
    if type == 'H':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable

    block = originBlock.astype(np.float32)
    norm_block = block - 128
    dct_block = cv2.dct(norm_block)

    # dct_block_int = np.round(dct_block).astype(np.int)
    # dct_block_quantization =  np.round((dct_block_int / qtable)).astype(np.int)

    dct_block_quantization =  np.round((dct_block / qtable)).astype(np.int)

    return dct_block_quantization

def inverseQuantifyBlock(originBlock, type):
    """
    反量化并 idct 一个 8x8 block
    :param originBlock: 8x8 block
    :param type: ‘H’ for luminance, 'C' for Chrominance
    :return: 反量化并逆dct之后的 8x8 block - np.uint8
    """
    if type == 'H':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable

    dct_block = (originBlock.astype(np.float32) * qtable)
    idct_block = cv2.idct(dct_block)
    inverse_norm_block = idct_block + 128
    idct_block_int = inverse_norm_block.astype(np.uint8)

    return idct_block_int

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

def diffBlocksDC(oriZigzagList):
    """
    对按照Zig-Zag排序的 block list 的所有dc进行差分操作
    :param zigzagList: 按照Zig-Zag排序的 block list
    """

    zigzagList = copy.deepcopy(oriZigzagList)

    preDC = 0
    for i in range(len(zigzagList)):
        diff = zigzagList[i][0] - preDC
        preDC = zigzagList[i][0]
        zigzagList[i][0] = diff

    return zigzagList


def intRealLength(val):
    if val == 0:
        return 0
    else:
        return int(math.log(abs(val), 2)) + 1


def int2code(val):
    valcode = bin(val)[2:]
    if val < 0:
        valcode = '1' + valcode[1:]
    return valcode


def zigzag2midSigns(zigzagBlock):
    """
    zigzagBlock to mid signs
    :param zigzagBlock: 经之字型排列之后的一个block - int list
    :return: midSigns
    """
    midSigns = []
    midSigns.append((zigzagBlock[0], intRealLength(zigzagBlock[0]), int2code(zigzagBlock[0])))
    zeroCount = 0
    for i in range(1, len(zigzagBlock)) :
        val = zigzagBlock[i]

        # EOB
        if np.sum(np.abs(np.array(zigzagBlock[i:]), dtype=np.int)) == 0:
            midSigns.append((0, 0))
            break

        # zero
        if val == 0:
            zeroCount += 1
            if zeroCount == 16:
                midSigns.append((15, 0))
                zeroCount = 0
        # non-zero
        else:
            midSigns.append((zeroCount, val, intRealLength(val), int2code(val)))
            zeroCount = 0

    return midSigns
