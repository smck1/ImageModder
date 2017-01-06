#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance
from copy import copy

OUTPATH = 'output'

def saveAsPNG(image, fname, outpath):
    # Convert the source file to a PNG with no other modification
    fpath = os.path.join(outpath, fname + '.png')
    try:
        image.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Saving as PNG failed for: {}. \nReason:{}".format(fname, m)


def generatemods(filepath, outpath):
    # Generate and save image modfiications for a source file, save them to outpath.
    originalimage = Image.open(filepath)
    fname, ext = os.path.splitext(filepath)
    fname = fname.split(os.sep)[-1]
    saveAsPNG(originalimage,fname, outpath)


# Parse commandline args.
path = ''

if len(argv) < 2:
    print "Please specify base image directory"
    exit()
elif len(argv) == 2:
    path = argv[1]
else:
    print "Please only provide a single argument - directory of base images."
    exit()



# Modify all items in the path, save mods to OUTPATH
for im in os.listdir(path):
    fpath = os.path.join(path, im)
    print fpath
    generatemods(fpath, OUTPATH)
