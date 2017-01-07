#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance
from copy import copy

def savebaselineJPEG(image, fname, outpath, optimize=True, quality=75, recompressed=False):
    # Convert the source file to a JPEG with no other modification

    if recompressed:
        fpath = os.path.join(outpath, fname + '_recompressed')
    else:
        fpath = os.path.join(outpath, fname + '_base')

    if quality !=75:
        fpath += 'q_{}.jpg'.format(quality)
    else:
        fpath += '.jpg'

    try:
        image.save(fpath, optimize=optimize, quality=quality)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Baseline JPEG creation failed for: {}. \nReason:{}".format(fname,
        m)

def saverotation(image, fname, outpath, degreescounterlockwise=90):
    # Save a rotated version of theimage.
    fpath = os.path.join(outpath, fname + '_rotate{}'.format(degreescounterlockwise) + '.jpg')
    im = copy(image)
    im = im.rotate(degreescounterlockwise)
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Rotated({}) image creation failed for: {}. \nReason:{}".format(degreescounterlockwise,fname,m)

def saverescale(image, fname, outpath, scalefactor=0.5):
    # Save a scaled copy of the image, uses a single scale factor for both x,y axes to maintain aspect ratio
    fpath = os.path.join(outpath, fname + '_resize{}'.format(scalefactor) + '.jpg')
    newsize = (int(image.width * scalefactor), int(image.height * scalefactor))
    im = copy(image)
    im = im.resize(newsize)
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Resize({}) image creation failed for: {}. \nReason:{}".format(scalefactor,fname,m)

def savethumb(image, fname, outpath, size=(128,128)):
    # Save a thumbnail of the image, preserves aspect ratio, so longest side will be of size[max(x,y)].
    fpath = os.path.join(outpath, fname + '_thumbnail{}_{}'.format(size[0], size[1]) + '.jpg')
    im = copy(image)
    im.thumbnail(size)
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Resize({}) image creation failed for: {}. \nReason:{}".format(size,fname,m)

def savecrop(image, fname, outpath, cropfactors=(0.2, 0.2, 0.2, 0.2)):
    # Save a cropped version of the image.
    # Cropfactors correspond to what portion of the original image size should be chopped off, with the
    # first 2 factors specifying the top left corner of the crop box, and latter 2 the bottom right.
    fpath = os.path.join(outpath, fname + '_cropped{}'.format(cropfactors) + '.jpg')
    cropbox =   (int(image.width * cropfactors[0]),
                int(image.height * cropfactors[1]),
                int(image.width * (1-cropfactors[0])),
                int(image.height * (1-cropfactors[1]))
                )
    im = copy(image)
    im = im.crop(cropbox)
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Crop({}) image creation failed for: {}. \nReason:{}".format(cropfactors,fname,m)

def saveflip(image, fname, outpath, axis='x'):
    # Flip the image on the x or y axis.
    fpath = os.path.join(outpath, fname + '_flip{}'.format(axis) + '.jpg')
    im = copy(image)
    if axis == 'x':
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    elif axis == 'y':
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        raise Exception('No valid axis procvided for flipping: {} - received value: {}'.format(fname, axis))
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Flipped({}) image creation failed for: {}. \nReason:{}".format(axis,fname,m)

def savewatermarked(image, fname, outpath, watermark):
    im = image.copy()
    # Save a watermarked version of the image. resize watermark to 10% of the image height,
    # with a minimum height of 40
    fpath = os.path.join(outpath, fname + '_watermarked' + '.jpg')
    targetheight = image.height / 10
    waterwidthscaler = watermark.width / watermark.height
    targetwdith = int(targetheight * waterwidthscaler)
    # Enforce minimum size
    if targetheight < 40:
        targetheight = 40
        targetwdith = int(targetheight * waterwidthscaler)
        # It's too wide, skew  it to fit.
        if targetwdith > image.width:
            targetwdith = image.width
    # Scale the watermark
    scaledwatermark = watermark.resize((targetwdith, targetheight))
    # Add it to the image
    im.paste(scaledwatermark, (image.width - targetwdith, image.height - targetheight), scaledwatermark)
    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Watermarked image creation failed for: {}. \nReason:{}".format(fname,m)

def saveenhanced(image, fname, outpath, colourfactor=1, brightnessfactor=1, contrastfactor=1, sharpnessfactor=1):
    # Perform colour enhancements to the image.
    # Any arguments which aren't 1 will be processed in order: colour, contrast, brightness, sharpness.
    estring = "col{}br{}con{}sh{}".format(colourfactor, brightnessfactor, contrastfactor, sharpnessfactor)
    fpath = os.path.join(outpath, fname + '_enhanced_{}'.format(estring) + '.jpg')

    im = copy(image)
    if colourfactor != 1:
        en = ImageEnhance.Color(im)
        im = en.enhance(colourfactor)
    if brightnessfactor != 1:
        en = ImageEnhance.Contrast(im)
        im = en.enhance(contrastfactor)
    if contrastfactor != 1:
        en = ImageEnhance.Brightness(im)
        im = en.enhance(brightnessfactor)
    if sharpnessfactor != 1:
        en = ImageEnhance.Sharpness(im)
        im = en.enhance(sharpnessfactor)

    try:
        im.save(fpath, optimize=True)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Enhanced({}) image creation failed for: {}. \nReason:{}".format(estring,fname,m)

def savefragment(filepath, fname, outpath, truncfactor=0.5):
    # Save a simulated fragmented file version of the file.
    # Trunfactor specifies how much of the data, sequentially from the start
    # of file, should be written to the new file.

    # Read data
    infile = open(filepath, 'rb')
    data = infile.read()
    infile.close()

    # Write truncated filepath
    fpath = os.path.join(outpath, fname + '_truncated{}'.format(truncfactor) + '.jpg')
    ofile = open(fpath, 'wb')
    writelength = int(len(data) * truncfactor)
    ofile.write(data[:writelength])
    ofile.close()
    print "Saved {}".format(fpath)



def generatemods(filepath, outpath, watermark):
    # Generate and save image modfiications for a source file, save them to outpath.
    originalimage = Image.open(filepath)
    fname, ext = os.path.splitext(filepath)
    fname = fname.split(os.sep)[-1]

    if ext.lower() not in ['.jpeg', '.jpg']:
        # Regular JPEG conversion of non JPEG
        savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=75) #default pil quality
    else:
        # It is a JPEG, save a baseline recompression
        print 'here: {}'.format(ext.lower())
        savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=75, recompressed=True) #default pil quality

    # Lower quality version
    savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=30)
    savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=60)

    # Watermark and variousflips, rotations and cropping
    savewatermarked(originalimage, fname, outpath, watermark)
    saveflip(originalimage, fname, outpath, 'x')
    saveflip(originalimage, fname, outpath, 'y')
    savecrop(originalimage, fname, outpath) #defaults
    saverescale(originalimage, fname, outpath, 0.5)
    saverescale(originalimage, fname, outpath, 1.5)
    savethumb(originalimage, fname, outpath)
    saverotation(originalimage, fname, outpath) #defaults, 90 counterclock

    # Image enhancements, colour, contrast, etc.
    saveenhanced(originalimage, fname, outpath, colourfactor=0.5) #reduce colours
    saveenhanced(originalimage, fname, outpath, colourfactor=1.5) #increase colours
    #saveenhanced(originalimage, fname, outpath, brightnessfactor=0.5) #reduce brightness
    #saveenhanced(originalimage, fname, outpath, brightnessfactor=1.5) #increase brightness
    #saveenhanced(originalimage, fname, outpath, contrastfactor=0.5) #reduce contrast
    #saveenhanced(originalimage, fname, outpath, contrastfactor=1.5) #increase contrast
    saveenhanced(originalimage, fname, outpath, sharpnessfactor=0.5) #reduce sharpness
    #saveenhanced(originalimage, fname, outpath, sharpnessfactor=1.5) #increase sharpness

    # Carving fragment simulation
    #savefragment(filepath, fname, outpath, 0.7)
    #savefragment(filepath, fname, outpath, 0.3)


# Parse commandline args.
path = ''
watermarkpath = os.path.join('resources', 'watermark.png')

if len(argv) != 3:
    print "usage: original_images_dir output_dir"
    exit()
elif len(argv) == 3:
    path = argv[1]
    outpath = argv[2]


# Open the watermakr file
try:
    watermark = Image.open(watermarkpath)
except IOError, m:
    print "Failed to open watermark at: {} - messgae: {}".format(watermarkpath, m)

# Modify all items in the path, save mods to OUTPATH
for im in os.listdir(path):
    fpath = os.path.join(path, im)
    print fpath
    generatemods(fpath, outpath, watermark)
