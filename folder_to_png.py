#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance
from copy import copy
from thread_utils import *

def saveAsPNG(image, fname, outpath):
    # Convert the source file to a PNG with no other modification
    fpath = os.path.join(outpath, fname + '.png')
    try:
        image.save(fpath)
        #print "Saved {}".format(fpath)
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


if not os.path.exists(outpath):
    print "Output directory does not exist: Creating."
    os.makedirs(outpath)

# Modify all items in the path, save mods to outpath
tpool = ThreadPool(4)
count = 0
print "Beginning conversion..."
for subdir, dirs, files in os.walk(path):
    for f in files:
        try:
            fpath = os.path.join(subdir, f)
            tpool.add_task(generatemods, fpath, outpath)
            #generatemods(fpath, outpath)
            count +=1
            if count %1000 ==0:
                print "Converted:", count
        except Exception:
            print "problem processing: {}".format(f)

tpool.wait_completion()
# for im in os.listdir(path):
#     fpath = os.path.join(path, im)
#     print fpath
#     generatemods(fpath, outpath, watermark)
