import sys, os, argparse, csv
from multiprocessing import Pool
from tqdm import tqdm
from mod import *
from thread_utils import *


def checkCreateDir(outpath):
    if not os.path.isdir(outpath):
        try:
            os.mkdir(outpath)
        except Exception as e:
            print("Couldn't create output directory\n{}".format(e))
            sys.exit()


def createGeneratorParams(filelist, *args):
    """Generate an iterable of all paramaters passed to the map/pool functions.
    Takes a filelist then attaches positional arguments to create a generator.
    """
    for f in filelist:
        params = [f]
        params.extend(args)
        yield params
        

def generatemodsold(filepath, outpath, watermark):
    """Generate and save image modfiications for a source file, save them to outpath."""
    originalimage = Image.open(filepath)
    ext = os.path.splitext(filepath)[1]
    fname = os.path.basename(filepath)


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



def generatemods(filepath, outpath, watermark, subdirs, preserve_names):
    """Generate and save image modfiications for a source file, save them to outpath."""

    originalimage = Image.open(filepath)
    ext = os.path.splitext(filepath)[1]
    fname = os.path.basename(filepath)

    # Crop
    if subdirs:
        writepath = os.path.join(outpath, "Crop5pc")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    savecrop(originalimage, fname, writepath, cropfactors=([0.05,0.05,0.05,0.05]), preserve_name=preserve_names) #defaults

    # Scale up
    if subdirs:
        writepath = os.path.join(outpath, "Scale1.5")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    saverescale(originalimage, fname, writepath, 1.5, preserve_name=preserve_names)

    # Higher Compression/Recompression 
    if subdirs:
        writepath = os.path.join(outpath, "Compression30")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    savebaselineJPEG(originalimage,fname, writepath, optimize=True, quality=30, preserve_name=preserve_names)
    
    # Borders (potentially – this gets around content filters on youtube)
    if subdirs:
        writepath = os.path.join(outpath, "Border30black")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    saveborder(originalimage, fname, writepath, width=30, colour="black", preserve_name=preserve_names)
    
    # X-axis mirror (thinking about content preserving in a way that wouldn’t require anyone to modify the image to view it without annoyance)
    if subdirs:
        writepath = os.path.join(outpath, "Mirrorx")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    saveflip(originalimage, fname, writepath, 'x', preserve_name=preserve_names)
    
    # watermark 
    if subdirs:
        writepath = os.path.join(outpath, "Watermark")
        checkCreateDir(writepath)
    else:
        writepath = outpath
    savewatermarked(originalimage, fname, writepath, watermark, preserve_name=preserve_names)

def main(args):

    # Open the watermark file
    watermarkpath = os.path.join('resources', 'watermark.png')
    try:
        watermark = Image.open(watermarkpath)
    except IOError as m:
        print("Failed to open watermark at: {} - messgae: {}".format(watermarkpath, m))
        sys.exit()

    fnames = os.listdir(args.dir)
    flist = [os.path.join(args.dir, f) for f in fnames]

    # Check if a deduplication hash set is provided
    # If so, use this to generate a unique file list
    if args.nodupes:
        print(f"""Processing {args.nodupes} to remove duplicates. Keeping the first file with the hash for each instance""")
        dedupehashes = {}
        with open(args.nodupes, "r", newline='') as dupecsv:
            reader = csv.reader(dupecsv, delimiter=";")
            header = next(reader)
            for row in reader:
                # fname;hash
                f = row[0]
                h = row[1]
                dedupehashes.setdefault(h, []).append(f)
                # if not dedupehashes.get(h, False):
                #     # hash isn't present in hash dict
                #     # add to hash dict
                #     dedupehashes[h] = 1
                #     # get filename
                #     fname = os.path.basename(row[0])
                #     if fname in fdict:
                #         # join args directory and filenames
                #         flist.append(os.path.join(args.dir, fname))
        duplicates = []
        for h,f in dedupehashes.items():
            if len(f) > 1:
                duplicates.extend(f[1:])

        flist = list(set(flist) - set(duplicates))
        print(f"{len(flist)} unique files found in directory.")

    if args.subset:
        flist = flist[:args.subset]
        print(f"Using subset of the first {args.subset} files.")

    #paramGenerator = createGeneratorParams(flist, args.out, watermark, args.subdirs, args.preservefnames)

    # Processing block 
    print("> Beginning processing...")

    tpool = ThreadPool(args.workers)
    count = 0
    for f in flist:
        try:
            tpool.add_task(generatemods, f, args.out, watermark, args.subdirs, args.preservefnames)
            #generatemods(fpath, outpath)
            count +=1
            if count % 1000 ==0:
                print( "Generated:", count)
        except Exception as e:
            print( "problem processing: {}.{}".format(f, e))

    tpool.wait_completion()

    #pool = Pool(processes=args.workers)
    #results = (pool.map(hashfun, flist))
    #results = pool.imap(generatemods, paramGenerator)
    #results = list(tqdm(pool.imap(generatemods, paramGenerator), total=len(flist)))

    
    
def test(args):

    print("Test flag received. Running modifications on the first file in the input directory.")

    # Open the watermark file
    watermarkpath = os.path.join('resources', 'watermark.png')
    try:
        watermark = Image.open(watermarkpath)
    except IOError as m:
        print("Failed to open watermark at: {} - messgae: {}".format(watermarkpath, m))
        sys.exit()


    # Get first file in directory
    filepath = os.listdir(args.dir)[0]
    filepath = os.path.join(args.dir, filepath)

    print(f"Processing file: {filepath}")

    generatemods(filepath, args.out, watermark, args.subdirs, args.preservefnames)

    print(f"Completed - check output in {args.out}")
    



if __name__ == "__main__":
    """ This is executed when run from the command line """

    # Set up args
    parser = argparse.ArgumentParser(description=f'Generate file modifications for a directory of images.')
    # required
    parser.add_argument('dir', help="Directory of files to process.")
    parser.add_argument('out', help="Output directory.")
    # test
    parser.add_argument('--test', '-test', action='store_true', help='Test run, use first file in target directory')
    # parameters
    parser.add_argument('--nodupes', '-nd', type=str, help="Don't process files with duplicate hashes. Provide CSV filee containing duplicates (formatted: filename;hash). e.g. -nd sha256.csv")
    parser.add_argument('--workers', '-w', type=int, nargs='?', const=1, help='Set the number of workers to use. Default 1. e.g. -t 6')
    parser.add_argument('--subset', '-s', type=int, help='subset the files in the diectory, only process the first n files, provide n. e.g. -s 5000')
    parser.add_argument('--subdirs', '-sd', action='store_true', help='Save files in separate subdirectories for each modification')
    parser.add_argument('--preservefnames', '-fn', action='store_true', help='When set, original filenames are preserved in the output. Only applicable in conjunction with --subdirs')


    args = parser.parse_args()
    
    checkCreateDir(args.out)

    if args.preservefnames and not args.subdirs:
        print("--preservefnames (-fn) required --subdits (-sd) to be set.")
        exit()

    if args.test:
        test(args)
    else:
        main(args)