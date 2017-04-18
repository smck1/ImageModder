from jpegmod import *
import sys

def generatemods(filepath, outpath, watermark):
    """Generate and save image modfiications for a source file, save them to outpath."""
    originalimage = Image.open(filepath)
    fname, ext = os.path.splitext(filepath)
    fname = fname.split(os.sep)[-1]

    if ext.lower() not in ['.jpeg', '.jpg']:
        # Regular JPEG conversion of non JPEG
        savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=75) #default pil quality
    else:
        # It is a JPEG, save a baseline recompression
        savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=75, recompressed=True) #default pil quality

    # Lower quality versions
    savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=30)
    #savebaselineJPEG(originalimage,fname, outpath, optimize=True, quality=60)

    # Watermark and variousflips, rotations and cropping
    savewatermarked(originalimage, fname, outpath, watermark)
    saveflip(originalimage, fname, outpath, 'x')
    saveflip(originalimage, fname, outpath, 'y')
    savecrop(originalimage, fname, outpath, cropfactors=([0.05,0.05,0.05,0.05])) #defaults
    savecrop(originalimage, fname, outpath, cropabsolute=([0,0,0,8])) #8px from bottom
    #saverescale(originalimage, fname, outpath, 0.5)
    saverescale(originalimage, fname, outpath, 1.5)
    savethumb(originalimage, fname, outpath)
    saverotation(originalimage, fname, outpath) #defaults, 90 counterclock

    # Image enhancements, colour, contrast, etc.
    #saveenhanced(originalimage, fname, outpath, colourfactor=0.5) #reduce colours
    #saveenhanced(originalimage, fname, outpath, colourfactor=1.5) #increase colours
    #saveenhanced(originalimage, fname, outpath, brightnessfactor=0.5) #reduce brightness
    #saveenhanced(originalimage, fname, outpath, brightnessfactor=1.5) #increase brightness
    #saveenhanced(originalimage, fname, outpath, contrastfactor=0.5) #reduce contrast
    #saveenhanced(originalimage, fname, outpath, contrastfactor=1.5) #increase contrast
    #saveenhanced(originalimage, fname, outpath, sharpnessfactor=0.5) #reduce sharpness
    #saveenhanced(originalimage, fname, outpath, sharpnessfactor=1.5) #increase sharpness

    # Carving fragment simulation
    #savefragment(filepath, fname, outpath, 0.7)
    #savefragment(filepath, fname, outpath, 0.3)

# Parse commandline args.
path = ''
watermarkpath = os.path.join('resources', 'watermark.png')

if len(argv) != 3:
    print "usage: original_images_dir output_dir"
    sys.exit()
elif len(argv) == 3:
    path = argv[1]
    outpath = argv[2]


# Open the watermakr file
try:
    watermark = Image.open(watermarkpath)
except IOError, m:
    print "Failed to open watermark at: {} - messgae: {}".format(watermarkpath, m)
    sys.exit()

if not os.path.isdir(outpath):
    try:
        os.mkdir(outpath)
    except Exception as e:
        print "Couldn't make out directory\n{}".format(e)
        sys.exit()


# Modify all items in the path, save mods to OUTPATH
flist = os.listdir(path)
numitems = len(flist)
i=0
for im in flist:
    fpath = os.path.join(path, im)
    try:
        generatemods(fpath, outpath, watermark)
    except Exception as e:
        print "Failed to process: {}\n{}".format(fpath, e)
    i+=1
    if i % 1000 ==0:
        print "Processed: {}".format(i)
