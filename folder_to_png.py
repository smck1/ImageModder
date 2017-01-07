#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance
from copy import copy


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

if len(argv) != 3:
    print "usage: <original_images_dir> <output_dir>"
    exit()
elif len(argv) == 3:
    path = argv[1]
    outpath = argv[2]




# Modify all items in the path, save mods to outpath

for subdir, dirs, files in os.walk(path):
    for f in files:
        try:
            fpath = os.path.join(subdir, f)
            print fpath
            generatemods(fpath, outpath)
        except Exception:
            print "problem processing: {}".format(f)
# for im in os.listdir(path):
#     fpath = os.path.join(path, im)
#     print fpath
#     generatemods(fpath, outpath, watermark)
