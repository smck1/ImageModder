#import PIL
import os
from sys import argv
from PIL import Image, ImageEnhance
from copy import copy

def savebaselineJPEG(image, fname, outpath, optimize=True, quality=75, recompressed=False, useexistingqtables=False):
    """
    Convert image to a regular baseline JPEG. Quality option is ignored if useexistingqtables=True.
    """
    if recompressed:
        fpath = os.path.join(outpath, fname + '_recompressed')
    else:
        fpath = os.path.join(outpath, fname + '_base')

    if quality !=75:
        fpath += 'q_{}.jpg'.format(quality)
    else:
        fpath += '.jpg'

    try:
        if useexistingqtables:
            image.save(fpath, subsample="keep", optimize=optimize, qtables=image.quantization)
        else:
            image.save(fpath, subsample="keep", optimize=optimize, quality=quality)

    except IOError, m:
        print "Baseline JPEG creation failed for: {}. \nReason:{}".format(fname,
        m)

def saverotation(image, fname, outpath, degreescounterlockwise=90):
    """ Save a rotated version of theimage."""
    fpath = os.path.join(outpath, fname + '_rotate{}'.format(degreescounterlockwise) + '.jpg')
    im = copy(image)
    im = im.rotate(degreescounterlockwise)
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Rotated({}) image creation failed for: {}. \nReason:{}".format(degreescounterlockwise,fname,m)

def saverescale(image, fname, outpath, scalefactor=0.5):
    """ Save a scaled copy of the image, uses a single scale factor for both x,y axes to maintain aspect ratio """
    fpath = os.path.join(outpath, fname + '_resize{}'.format(scalefactor) + '.jpg')
    newsize = (int(image.width * scalefactor), int(image.height * scalefactor))
    im = copy(image)
    im = im.resize(newsize)
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Resize({}) image creation failed for: {}. \nReason:{}".format(scalefactor,fname,m)

def savethumb(image, fname, outpath, size=(128,128)):
    """ Save a thumbnail of the image, preserves aspect ratio, so longest side will be of size[max(x,y)] """
    fpath = os.path.join(outpath, fname + '_thumbnail{}_{}'.format(size[0], size[1]) + '.jpg')
    im = copy(image)
    im.thumbnail(size)
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Thumbnail({}) image creation failed for: {}. \nReason:{}".format(size,fname,m)

def savecrop(image, fname, outpath, cropabsolute=None, cropfactors=[0.2, 0.2, 0.2, 0.2]):
    """
     Save a cropped version of the image.
     Cropfactors correspond to what portion of the original image size should be chopped off, with values corresponding to:
     left, upper, right, lower
     if cropabsolute is specified, absolute values are used instead of factors of the original's height and width.
    """
    if cropabsolute:
        if type(cropabsolute) != list:
            raise Exception("cropabsolute must be a list of length 4.")
        else:
            if len(cropabsolute) !=4:
                raise Exception("Please provide 4 values corresponsindg to [left, upper, right, lower]")
        cropbox =   (int(cropabsolute[0]),
                    int(cropabsolute[1]),
                    int(image.width - cropabsolute[2]),
                    int(image.height - cropabsolute[3])
                    )
        fpath = os.path.join(outpath, fname + '_cropped{}'.format(cropabsolute) + '.jpg')
    else:
        if type(cropfactors) != list:
            raise Exception("cropfactors must be a list of length 4.")
        else:
            if len(cropfactors) !=4:
                raise Exception("Please provide 4 values corresponsindg to [left, upper, right, lower]")
        cropbox =   (int(image.width * cropfactors[0]),
                    int(image.height * cropfactors[1]),
                    int(image.width * (1-cropfactors[2])),
                    int(image.height * (1-cropfactors[3]))
                    )
        fpath = os.path.join(outpath, fname + '_cropped{}'.format(cropfactors) + '.jpg')
    im = copy(image)
    im = im.crop(cropbox)
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Crop({}) image creation failed for: {}. \nReason:{}".format(cropabsolute,cropfactors,fname,m)

def saveflip(image, fname, outpath, axis='x'):
    """ Flip the image on the x or y axis """
    fpath = os.path.join(outpath, fname + '_flip{}'.format(axis) + '.jpg')
    im = copy(image)
    if axis == 'x':
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    elif axis == 'y':
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        raise Exception('No valid axis procvided for flipping: {} - received value: {}'.format(fname, axis))
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Flipped({}) image creation failed for: {}. \nReason:{}".format(axis,fname,m)

def savewatermarked(image, fname, outpath, watermark):
    """
    Save a watermarked version of the image. resize watermark to 10% of the image height,
    with a minimum height of 40
    """
    im = image.copy()
    fpath = os.path.join(outpath, fname + '_watermarked' + '.jpg')
    targetheight = image.height / 10
    waterwidthscaler = watermark.width / watermark.height
    targetwidth = int(targetheight * waterwidthscaler)
    # Enforce minimum size
    if targetheight < 40:
        targetheight = 40
        targetwidth = int(targetheight * waterwidthscaler)
        # It's too wide, skew  it to fit.
        if targetwidth > image.width:
            targetwidth = image.width
    # Scale the watermark
    scaledwatermark = watermark.resize((targetwidth, targetheight))
    # Add it to the image
    im.paste(scaledwatermark, (im.width - targetwidth, im.height - targetheight))
    try:
        im.save(fpath, subsample="keep", qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Watermarked image creation failed for: {}. \nReason:{}".format(fname,m)

def saveenhanced(image, fname, outpath, colourfactor=1, brightnessfactor=1, contrastfactor=1, sharpnessfactor=1):
    """
    Perform colour enhancements to the image.
    Any arguments which aren't 1 will be processed in order: colour, contrast, brightness, sharpness.
    """
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
        im.save(fpath, subsample="keep",qtables=image.quantization, optimize=True)

    except IOError, m:
        print "Enhanced({}) image creation failed for: {}. \nReason:{}".format(estring,fname,m)

def savefragment(filepath, fname, outpath, truncfactor=0.5):
    """
    Save a simulated fragmented file version of the file.
    Trunfactor specifies how much of the data, sequentially from the start
    of file, should be written to the new file.
    """

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
