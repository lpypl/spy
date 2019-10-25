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

LuminanceQuantizationTableOnes = np.ones((8, 8), dtype=np.int)

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

def show1sec(img):
    cv2.imshow("Window Name", img)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()


def showalways(img):
    cv2.imshow("Window Name", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 4:2:2
def ycrcb2sample(ycrcb):
    y = ycrcb[:, :, 0]
    cr = ycrcb[:, 0:ycrcb.shape[1]:2, 1]
    cb = ycrcb[:, 0:ycrcb.shape[1]:2, 2]
    return y, cr, cb


def sample2ycrcb(y, cr, cb):
    newcr = np.ones((cr.shape[0], cr.shape[1]*2))
    newcr[:, 0:newcr.shape[1]:2] = cr
    newcr[:, 1:newcr.shape[1]:2] = cr

    newcb = np.ones((cb.shape[0], cb.shape[1]*2))
    newcb[:, 0:newcb.shape[1]:2] = cb
    newcb[:, 1:newcb.shape[1]:2] = cb

    return np.array([y, newcr, newcb]).swapaxes(0,1).swapaxes(1,2).astype(np.uint8)


def dct(data):
    dataf = data.astype(np.float32)
    dataf_dct = cv2.dct(dataf)
    return dataf_dct


def idct(dataf_dct):
    dataf_idct = cv2.idct(dataf_dct)
    data_idct = dataf_idct.astype(np.uint8)
    return  data_idct


def data2blocks(data):
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

    assert height%8==0 and width%8==0
    bh = width//8
    bv = height//8

    data = np.ones((height, width), dtype=np.uint8)
    for row in range(bv):
        for column in range(bh):
            data[row*8:(row+1)*8, column*8:(column+1)*8] = blocks[row*bh+column]

    return data


def quantifyBlock(originBlock, type):

    if type == 'H':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable
    elif type == '1':
        qtable = LuminanceQuantizationTableOnes

    block = originBlock.astype(np.float32)
    norm_block = block - 128
    dct_block = cv2.dct(norm_block)

    # dct_block_int = np.round(dct_block).astype(np.int)
    # dct_block_quantization =  np.round((dct_block_int / qtable)).astype(np.int)

    dct_block_quantization =  np.round((dct_block / qtable)).astype(np.int)

    return dct_block_quantization

def inverseQuantifyBlock(originBlock, type):

    if type == 'H':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable
    elif type == '1':
        qtable = LuminanceQuantizationTableOnes

    dct_block = (originBlock.astype(np.float32) * qtable)
    idct_block = cv2.idct(dct_block)
    inverse_norm_block = idct_block + 128
    idct_block_int = inverse_norm_block.astype(np.uint8)

    return idct_block_int



# read image

def testidct():
    rgb = cv2.imread('./Pictures/Koala.bmp')
    ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

    y, cr, cb = ycrcb2sample(ycrcb)
    yblocks, yh, yw = data2blocks(y)
    crblocks, crh, crw = data2blocks(cr)
    cbblocks, cbh, cbw = data2blocks(cb)

    tyblocks = yblocks[:]
    for i in range(len(yblocks)):
        tyblocks[i] = quantifyBlock(yblocks[i], 'H')
        tyblocks[i] = inverseQuantifyBlock(tyblocks[i], 'H')
    newy = blocks2data(tyblocks, yh, yw)

    tcrblocks = crblocks[:]
    for i in range(len(crblocks)):
        tcrblocks[i] = quantifyBlock(crblocks[i], 'C')
        tcrblocks[i] = inverseQuantifyBlock(tcrblocks[i], 'C')
    newcr = blocks2data(tcrblocks, crh, crw)

    tcbblocks = cbblocks[:]
    for i in range(len(cbblocks)):
        tcbblocks[i] = quantifyBlock(cbblocks[i], 'C')
        tcbblocks[i] = inverseQuantifyBlock(tcbblocks[i], 'C')
    newcb = blocks2data(tcbblocks, cbh, cbw)

    showalways(y)
    showalways(newy)

    newycrcb = sample2ycrcb(newy, newcr, newcb)
    showalways(newycrcb)
    newrgb = cv2.cvtColor(newycrcb, cv2.COLOR_YCR_CB2RGB)
    showalways(newrgb)

def rearrange(block):
    blklist = []
    for sum in range(15):
        if sum < 8:
            if sum%2 == 0:
                for col in range(sum+1):
                    blklist.append(block[sum-col, col])
            else:
                for row in range(sum+1):
                    blklist.append(block[row, sum-row])
        else:
            if sum%2 == 0:
                for col in range(sum-7, 8):
                    blklist.append(block[sum-col, col])
            else:
                for row in range(sum-7, 8):
                    blklist.append(block[row, sum-row])

    return blklist


def getDiffCode(val):
    """
    将差分值转换为相应的补码
    """
    if val == 0:
        bitcnt = 0
        valcode = '0'

    else:
        bitcnt =  int(math.log(abs(val), 2)) + 1

        if val < 0:
            valcode = bin(2**bitcnt-1+val)[2:].zfill(bitcnt)
        else:
            valcode = bin(val)[2:]

    return valcode


# main
rgb = cv2.imread('./Pictures/Koala.bmp')
ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

y, cr, cb = ycrcb2sample(ycrcb)
yblocks, yh, yw = data2blocks(y)

tyblocks = yblocks[:]
for i in range(len(yblocks)):
    tyblocks[i] = quantifyBlock(yblocks[i], 'H')

rearrangeList = [rearrange(blk) for blk in tyblocks]
dcTable = np.array(rearrangeList, dtype=np.int)[:, 0]
tmpDcTable = np.zeros(len(rearrangeList), dtype=np.int)
tmpDcTable[1:] = dcTable[:len(rearrangeList)-1]
dcDiffTable = dcTable - tmpDcTable
midSigns = []

for val in dcDiffTable:
    if val == 0:
        bitcnt = 0
    else:
        bitcnt =  int(math.log(abs(val), 2)) + 1

    midSigns.append((bitcnt, val, getDiffCode(val)))

nparr = np.array(midSigns)



# main



