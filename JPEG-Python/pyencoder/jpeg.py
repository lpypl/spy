import copy
import cv2
import math

from jpegTable import *

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
    if type == 'L':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable
    else:
        raise TypeError("type must be L or C")

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
    if type == 'L':
        qtable = LuminanceQuantizationTable
    elif type == 'C':
        qtable = ChrominanceQuantizationTable
    else:
        raise TypeError("type must be L or C")

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
    """
    获取整数的二进制编码长度
    :param val: int
    :return: bin length
    """
    # 0 似乎只需要哈夫曼码
    if val == 0:
        return 0
    else:
        return int(math.log(abs(val), 2)) + 1


def int2LenAndCode(val):
    """
    返回一个整数的长度和编码
    :param val: int value
    :return: (length, binCode)
    """
    bitcnt = intRealLength(val)

    if val == 0:
        return (0, '')

    if val < 0:
        binCode = bin(2 ** bitcnt - 1 + val)[2:].zfill(bitcnt)
    else:
        binCode = bin(val)[2:]

    return (bitcnt, binCode)


def zigzag2midSigns(zigzagBlock):
    """
    zigzagBlock to mid signs
    暂且认为若DC值为0，则只需要一个哈夫曼码，而不需要0的二进制代码
    :param zigzagBlock: 经之字型排列之后的一个block - int list
    :return: midSigns
    """

    # DC
    midSigns = []
    midSigns.append(zigzagBlock[0])
    # AC
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
            midSigns.append((zeroCount, val))
            zeroCount = 0

    return midSigns


def midSigns2binaryCode(midSignsList, type):
    """
    zigzagBlock to mid signs
    暂且认为若DC值为0，则只需要一个哈夫曼码，而不需要0的二进制代码
    :param zigzagBlock: 经之字型排列之后的一个block - int list
    :return: midSigns
    """

    if type == 'L':
        dcTable = LuminanceDCCoefficientDifferencesTable
        acTable = acLuminanceTable
    elif type == 'C':
        dcTable = ChrominanceDCCoefficientDifferencesTable
        acTable = acChrominanceTable
    else:
        raise TypeError("type must be L or C")

    binaryData = ""

    for midSigns in midSignsList:

        # DC
        binLen, binCode = int2LenAndCode(midSigns[0])
        binaryData += dcTable[binLen][2] + binCode

        # AC
        for sign in midSigns[1:]:
            # 若sign[1]为0，则binCode为空字符串
            binLen, binCode = int2LenAndCode(sign[1])
            key = "{}/{}".format(hex(sign[0])[-1].upper(), hex(binLen)[-1].upper())
            binaryData += acTable[key][1]
            binaryData += binCode

    return binaryData

def midSigns2binaryCode_Colorful(midSignsTupleList):
    """
    zigzagBlock to mid signs
    暂且认为若DC值为0，则只需要一个哈夫曼码，而不需要0的二进制代码
    :param zigzagBlock: 经之字型排列之后的一个block - int list
    :return: midSigns
    """
    binaryData = ""

    for midSignsTuple in midSignsTupleList:

        # 亮度
        dcTable = LuminanceDCCoefficientDifferencesTable
        acTable = acLuminanceTable

        midSigns = midSignsTuple[0]

        # DC
        binLen, binCode = int2LenAndCode(midSigns[0])
        binaryData += dcTable[binLen][2] + binCode

        # AC
        for sign in midSigns[1:]:
            # 若sign[1]为0，则binCode为空字符串
            binLen, binCode = int2LenAndCode(sign[1])
            key = "{}/{}".format(hex(sign[0])[-1].upper(), hex(binLen)[-1].upper())
            binaryData += acTable[key][1]
            binaryData += binCode

        #色度 1
        dcTable = ChrominanceDCCoefficientDifferencesTable
        acTable = acChrominanceTable

        midSigns = midSignsTuple[1]
        # DC
        binLen, binCode = int2LenAndCode(midSigns[0])
        binaryData += dcTable[binLen][2] + binCode

        # AC
        for sign in midSigns[1:]:
            # 若sign[1]为0，则binCode为空字符串
            binLen, binCode = int2LenAndCode(sign[1])
            key = "{}/{}".format(hex(sign[0])[-1].upper(), hex(binLen)[-1].upper())
            binaryData += acTable[key][1]
            binaryData += binCode

        #色度 2
        dcTable = ChrominanceDCCoefficientDifferencesTable
        acTable = acChrominanceTable

        midSigns = midSignsTuple[2]
        # DC
        binLen, binCode = int2LenAndCode(midSigns[0])
        binaryData += dcTable[binLen][2] + binCode

        # AC
        for sign in midSigns[1:]:
            # 若sign[1]为0，则binCode为空字符串
            binLen, binCode = int2LenAndCode(sign[1])
            key = "{}/{}".format(hex(sign[0])[-1].upper(), hex(binLen)[-1].upper())
            binaryData += acTable[key][1]
            binaryData += binCode

    return binaryData

def int2FourBits(num):
    return  bin(num)[2:].zfill(4)

def int2ByteBinary(num):
    return  bin(num)[2:].zfill(8)

def int2DoubleByteBinary(num):
    return  bin(num)[2:].zfill(16)

def huffmanTable2BinaryData(dcl, dcc, acl, acc):
    """
    将四个哈夫曼表转换为 binary string
    :param dcl: dc 亮度表
    :param dcc: dc 色度表
    :param acl: ac 亮度表
    :param acc: ac 色度表
    :return:
    """
    binaryData = ""

    # DC 0
    binaryData += int2ByteBinary(0x00)
    for category in range(1, 17):
        categoryCount = 0
        for item in dcl:
            if item[1] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    for item in dcl:
        binaryData += int2ByteBinary(item[0])

    # DC 1
    binaryData += int2ByteBinary(0x01)
    for category in range(1, 17):
        categoryCount = 0
        for item in dcc:
            if item[1] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    for item in dcc:
        binaryData += int2ByteBinary(item[0])

    #
    # AC 0
    binaryData += int2ByteBinary(0x10)
    for category in range(1, 17):
        categoryCount = 0
        for item in acl.values():
            if item[0] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    aclItems = [val for val in acl.items()]
    aclItems.sort(key=lambda a:a[1][1])
    aclCodeList = [val[0] for val in aclItems]
    for key in aclCodeList:
        binaryData += int2FourBits(eval("0x"+key.split('/')[0]))
        binaryData += int2FourBits(eval("0x"+key.split('/')[1]))

    # AC 1
    binaryData += int2ByteBinary(0x11)
    for category in range(1, 17):
        categoryCount = 0
        for item in acc.values():
            if item[0] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    accItems = [val for val in acc.items()]
    accItems.sort(key=lambda a:a[1][1])
    accCodeList = [val[0] for val in accItems]
    for key in accCodeList:
        binaryData += int2FourBits(eval("0x"+key.split('/')[0]))
        binaryData += int2FourBits(eval("0x"+key.split('/')[1]))

    binaryData = int2ByteBinary(0xFF) + int2ByteBinary(0xC4) + int2DoubleByteBinary(len(binaryData)//8 + 2) + binaryData

    return binaryData
