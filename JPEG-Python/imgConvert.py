import numpy as np
import cv2

LuminanceQuantizationTable = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                              [12, 12, 14, 19, 26, 58, 60, 55],
                              [14, 13, 16, 24, 40, 57, 69, 56],
                              [14, 17, 22, 29, 51, 87, 80, 62],
                              [18, 22, 37, 56, 68, 109, 103, 77],
                              [24, 35, 55, 64, 81, 104, 113, 92],
                              [49, 64, 78, 87, 103, 121, 120, 101],
                              [72, 92, 95, 98, 112, 100, 103, 99]], dtype=np.int)

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


def quantifyBlock(originBlock):
    block = originBlock.astype(np.float32)
    norm_block = block - 128
    dct_block = cv2.dct(norm_block)
    dct_block_int = np.round(dct_block).astype(np.int)
    dct_block_quantization =  np.round((dct_block_int / LuminanceQuantizationTable)).astype(np.int)

    return dct_block_quantization

def inverseQuantifyBlock(originBlock):
    dct_block = (originBlock * LuminanceQuantizationTable).astype(np.float32)
    idct_block = cv2.idct(dct_block)
    inverse_norm_block = idct_block + 128
    idct_block_int = inverse_norm_block.astype(np.uint8)

    return idct_block_int



# read image
rgb = cv2.imread('./Pictures/Koala.bmp')
ycrcb = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCR_CB)

y, cr, cb = ycrcb2sample(ycrcb)
yblocks, yh, yw  = data2blocks(y)
# crblocks, crblockspr  = data2blocks(cr)
# cbblocks, cbblockspr  = data2blocks(cb)

tyblocks = yblocks[:]
for i in range(len(yblocks)):
    tyblocks[i] = quantifyBlock(yblocks[i])
    tyblocks[i] = inverseQuantifyBlock(tyblocks[i])

newy = blocks2data(tyblocks, yh, yw)

showalways(y)
showalways(newy)




