from __future__ import print_function
import binascii
import struct
from PIL import Image
import numpy as np
import scipy as spc
import scipy.misc
import scipy.cluster
import scipy.optimize
from os import listdir
from os.path import isfile, join
import os
import configparser

NUM_CLUSTERS = 5
CODE_RENAMED = 'colorArranged'
NUM_QUANTIZE_COLOR = 1
DEFAULT_HEX_COLOR = '000000'
CONFIG_PATH = 'config.cfg'

def getColor(fileName):
    try:
        im = Image.open(fileName)
        im = im.resize((150, 150))      # optional, to reduce time
        ar = np.asarray(im)
        shape = ar.shape
        #ar = ar.reshape(spc.product(shape[:2]), shape[2]).astype(float)
        ar = ar.reshape(np.prod(shape[:2]), shape[2]).astype(float)

        print('finding clusters')
        codes, dist = spc.cluster.vq.kmeans(ar, NUM_CLUSTERS)
        print('cluster centres:\n', codes)

        vecs, dist = spc.cluster.vq.vq(ar, codes)         # assign codes
        counts, bins = np.histogram(vecs, len(codes))    # count occurrences

        index_max = np.argmax(counts)                    # find most frequent
        peak = codes[index_max]
        colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
        #print('most frequent is %s (#%s)' % (peak, colour))
    except Exception as e:
        #print('Error!!! : ' + e)
        print('Error!! : ', e)
        colour = DEFAULT_HEX_COLOR
    return colour

def getColorQuantize(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((150, 150))      # optional, to reduce time
        quantized_img = img.quantize(NUM_QUANTIZE_COLOR)
        #get color from any pixel
        pixels = quantized_img.load()
        x, y = 1, 1
        #r, g, b = pixels[x, y]  # For RGB images. For RGBA, it would be r, g, b, a
        quantized_img = quantized_img.convert('RGB')
        r, g, b = quantized_img.getpixel((x, y))
        hex_color = '{:02x}{:02x}{:02x}'.format(r, g, b)#rgb_to_hex(r, g, b)
        rgb_color = '{:02}{:02}{:02}'.format(r, g, b)
        print(hex_color)
    except Exception as e:
        #print('Error!!! : ' + e)
        print('Error!! : ', e)
        hex_color = DEFAULT_HEX_COLOR
        rgb_color = 'rgb'
    return rgb_color + '_' + hex_color


def isEligible(filename):
    if filename.startswith(CODE_RENAMED):
        return False
    else:
        return True

#list file
config = configparser.ConfigParser()
config.read_file(open(CONFIG_PATH))
mypath = config.get('PATH', 'target_path')
#mypath = 'C:\\_googleDrive\\arts.references\\_clothes'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for (file) in onlyfiles:
    if isEligible(file) == False:
        continue
    fullPath = mypath + '\\' + file
    print(fullPath)
    #color = getColor(fullPath) #method 1
    color = getColorQuantize(fullPath)
    newName = CODE_RENAMED + '_' + color + '_' + file
    newFullPath = mypath + '\\' + newName
    if DEFAULT_HEX_COLOR in color: 
        continue
    try:
        os.rename(fullPath,newFullPath)
    except Exception as e:
        print('Error!! : ', e)
    
#color = getColor('image.jpg');
#print('most frequent is %s' % (color))

print('reading image')