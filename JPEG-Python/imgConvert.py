import numpy as np
import cv2
import math
from jpeg import *

def showalways(img, title = "Window Name"):
    """
    显示图片
    :param img: img
    :param title: title
    :return:
    """
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def testSampleAndDct():
    """
    测试子采样并量化一个图片后再逆量化并恢复图像
    :return:
    """
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

def getDiffCode(val):
    """
    将差分值转换为相应的编码
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


rgb = cv2.imread('./Pictures/Koala.bmp')
ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

y, cr, cb = ycrcb2sample(ycrcb)
yblocks, yh, yw = data2blocks(y)

tyblocks = yblocks[:]
for i in range(len(yblocks)):
    tyblocks[i] = quantifyBlock(yblocks[i], 'H')

zigList = [zigzagOrder(blk) for blk in tyblocks]
npzigList = np.array(zigList)

# 差分 DC
diffZigList = diffBlocksDC(zigList)
npdiffzigList = np.array(diffZigList)

midSignsList = []
for zigblock in diffZigList:
    midSignsList.append(zigzag2midSigns(zigblock))

# main



