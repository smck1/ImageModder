#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance

OUTPATH = 'output'

def savebaselineJPEG(image, fname, outpath):
    # Convert the source file to a JPEG with no other modification
    fpath = os.path.join(outpath, fname + '_base' + '.jpg')
    try:
        image.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Baseline JPEG creation failed for: {}. \nReason:{}".format(fname,
        m)

def saverotation(image, fname, outpath, degreescounterlockwise=90):
    # Save a rotated version of theimage.
    fpath = os.path.join(outpath, fname + '_rotate{}'.format(degreescounterlockwise) + '.jpg')
    im = image.rotate(degreescounterlockwise)
    try:
        im.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Rotated({}) image creation failed for: {}. \nReason:{}".format(degreescounterlockwise,fname,m)

def saveresize(image, fname, outpath, scalefactor=0.5):
    # Save a scaled copy of the image, uses a single scale factor for both x,y axes to maintain aspect ratio
    fpath = os.path.join(outpath, fname + '_resize{}'.format(scalefactor) + '.jpg')
    newsize = (int(image.width * scalefactor), int(image.height * scalefactor))
    im = image.resize(newsize)
    try:
        im.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Resize({}) image creation failed for: {}. \nReason:{}".format(scalefactor,fname,m)

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
    im = image.crop(cropbox)
    try:
        im.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Crop({}) image creation failed for: {}. \nReason:{}".format(cropfactors,fname,m)

def saveflip(image, fname, outpath, axis='x'):
    # Flip the image on the x or y axis.
    fpath = os.path.join(outpath, fname + '_flip{}'.format(axis) + '.jpg')
    if axis == 'x':
        im = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif axis == 'y':
        im = image.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        raise Exception('No valid axis procvided for flipping: {} - received value: {}'.format(fname, axis))
    try:
        im.save(fpath)
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
        im.save(fpath)
        print "Saved {}".format(fpath)
    except IOError, m:
        print "Watermarked image creation failed for: {}. \nReason:{}".format(fname,m)

def saveenhanced(image, fname, outpath, colourfactor=1, brightnessfactor=1, contrastfactor=1, sharpnessfactor=1):
    # Perform colour enhancements to the image.
    # Any arguments which aren't 1 will be processed in order: colour, contrast, brightness, sharpness.
    estring = "col{}br{}con{}sh{}".format(colourfactor, brightnessfactor, contrastfactor, sharpnessfactor)
    fpath = os.path.join(outpath, fname + '_enhanced_{}'.format(estring) + '.jpg')

    im = image
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
        im.save(fpath)
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

    # Regular JPEG conversion
    savebaselineJPEG(originalimage,fname, outpath)

    # Watermark and variousflips, rotations and cropping
    savewatermarked(originalimage, fname, outpath, watermark)
    saveflip(originalimage, fname, outpath, 'x')
    saveflip(originalimage, fname, outpath, 'y')
    savecrop(originalimage, fname, outpath) #defaults
    saveresize(originalimage, fname, outpath, 0.7)
    saveresize(originalimage, fname, outpath, 0.3)
    saverotation(originalimage, fname, outpath) #defaults

    # Image enhancements, colour, contrast, etc.
    saveenhanced(originalimage, fname, outpath, colourfactor=0.5) #reduce colours
    saveenhanced(originalimage, fname, outpath, colourfactor=1.5) #increase colours
    saveenhanced(originalimage, fname, outpath, brightnessfactor=0.5) #reduce brightness
    saveenhanced(originalimage, fname, outpath, brightnessfactor=1.5) #increase brightness
    saveenhanced(originalimage, fname, outpath, contrastfactor=0.5) #reduce contrast
    saveenhanced(originalimage, fname, outpath, contrastfactor=1.5) #increase contrast
    saveenhanced(originalimage, fname, outpath, sharpnessfactor=0.5) #reduce sharpness
    saveenhanced(originalimage, fname, outpath, sharpnessfactor=1.5) #increase sharpness

    # Carving fragment simulation
    savefragment(filepath, fname, outpath, 0.7)
    savefragment(filepath, fname, outpath, 0.3)


# Parse commandline args.
path = ''
watermarkpath = os.path.join('resources', 'watermark.png')

if len(argv) < 2:
    print "Please specify base image directory"
    exit()
elif len(argv) == 2:
    path = argv[1]
else:
    print "Please only provide a single argument - directory of base images."
    exit()

# Open the watermakr file
try:
    watermark = Image.open(watermarkpath)
except IOError, m:
    print "Failed to open watermark at: {} - messgae: {}".format(watermarkpath, m)

# Modify all items in the path, save mods to OUTPATH
for im in os.listdir(path):
    fpath = os.path.join(path, im)
    print fpath
    generatemods(fpath, OUTPATH, watermark)