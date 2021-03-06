import copy
import cv2
import math

from jpegTable import *

def data2blocks(data):
    """
    将图像数据矩阵转换为8x8的BLOCK，不足8x8的数据会填充0
    :param data:图像数据矩阵（二维，单个通道）
    :return:blocks(block list),height(填充后的实际高度), width（填充后的实际宽度）
    """

    # 原始宽高
    height, width = data.shape

    # 扩充
    newdata = np.zeros(((height+7)//8 * 8, (width+7)//8 * 8))
    newdata[0:height, 0:width] = data
    data = newdata

    # 扩充后宽高
    height, width = data.shape

    assert height%8==0 and width%8==0

    blocks = []
    for r in range(0, height, 8):
        for c in range(0, width, 8):
            blocks.append(data[r:r+8, c:c+8])
    return blocks, height, width

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

    # DC电平偏移是必要的，否则图像色彩会不正常
    # 应该是解码器都会执行逆偏移的缘故吧
    norm_block = block - 128
    dct_block = cv2.dct(norm_block)

    # dct_block_int = np.round(dct_block).astype(np.int)
    # dct_block_quantization =  np.round((dct_block_int / qtable)).astype(np.int)

    dct_block_quantization =  np.round((dct_block / qtable)).astype(np.int)

    return dct_block_quantization

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
    # 记录前导0的数目
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
    # table id 0x00
    binaryData += int2ByteBinary(0x00)
    # 1-16 各个长度的编码数目
    for category in range(1, 17):
        categoryCount = 0
        for item in dcl:
            if item[1] == category:
                categoryCount += 1
        # count
        binaryData += int2ByteBinary(categoryCount)
    for item in dcl:
        binaryData += int2ByteBinary(item[0])

    # DC 1
    # table id 0x01
    binaryData += int2ByteBinary(0x01)
    # 1-16 各个长度的编码数目
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
    # table id 0x10
    binaryData += int2ByteBinary(0x10)
    # 写入 1-16 各个长度的编码数目
    for category in range(1, 17):
        categoryCount = 0
        for item in acl.values():
            if item[0] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    # 写入各个编码
    # 对所有的编码字符串进行升序排序，即可使这些编码按照范式哈夫曼表从左至右，从上到下的顺序排列
    aclItems = [val for val in acl.items()]
    aclItems.sort(key=lambda a:a[1][1])
    aclCodeList = [val[0] for val in aclItems]
    for key in aclCodeList:
        # signal - count of zero
        binaryData += int2FourBits(eval("0x"+key.split('/')[0]))
        # signal - length of ac
        binaryData += int2FourBits(eval("0x"+key.split('/')[1]))

    # AC 1
    # table id 0x11
    binaryData += int2ByteBinary(0x11)
    # 写入 1-16 各个长度的编码数目
    for category in range(1, 17):
        categoryCount = 0
        for item in acc.values():
            if item[0] == category:
                categoryCount += 1
        binaryData += int2ByteBinary(categoryCount)
    # 写入各个编码
    # 对所有的编码字符串进行升序排序，即可使这些编码按照范式哈夫曼表从左至右，从上到下的顺序排列
    accItems = [val for val in acc.items()]
    accItems.sort(key=lambda a:a[1][1])
    accCodeList = [val[0] for val in accItems]
    for key in accCodeList:
        # signal - count of zero
        binaryData += int2FourBits(eval("0x"+key.split('/')[0]))
        # signal - length of ac
        binaryData += int2FourBits(eval("0x"+key.split('/')[1]))


    # 写入DHT标记和长度信息
    binaryData = int2ByteBinary(0xFF) + int2ByteBinary(0xC4) + int2DoubleByteBinary(len(binaryData)//8 + 2) + binaryData

    return binaryData


def zigzigTable2CArray(table):
    """
    对table进行之字形编码，以C++数组形式输出
    """
    lt =  zigzagOrder(table)
    for i in range(len(lt)):
        if i % 8 == 0:
            print("\n")
        print(hex(lt[i]), end = ', ')