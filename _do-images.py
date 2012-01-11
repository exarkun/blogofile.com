#!/usr/bin/python

from sys import argv

from twisted.python.filepath import FilePath
from twisted.python.usage import UsageError, Options

from PythonMagick import Image
from PythonMagick._PythonMagick import Geometry

from pyexiv2 import ImageMetadata

ROTATIONS = {
    '6': 90,
    '1': 0,
    }

EXIF_ORIENTATION = "EXIF:Orientation"

class ImageOptions(Options):
    optParameters = [
        ('output-directory', 'o', None,
         "Directory name (must not exist) beneath site images directory where "
         "processed images will be written."),
        ]

    def __init__(self):
        Options.__init__(self)
        self['imageFilenames'] = []


    def parseArgs(self, *imageFilenames):
        self['imageFilenames'] = map(FilePath, imageFilenames)


    def postOptions(self):
        if not self['imageFilenames']:
            raise UsageError("Specify at least one image filename to process.")
        if self['output-directory'] is None:
            raise UsageError("Specify the output directory")

        output = FilePath(__file__).sibling("images").child(self['output-directory'])
        if output.exists():
            raise UsageError("Output directory must not exist.")

        self['output-directory'] = output



def main():
    options = ImageOptions()
    try:
        options.parseOptions(argv[1:])
    except UsageError, e:
        raise SystemExit(str(e))

    scaleAndOrientImages(options['output-directory'], options['imageFilenames'])


def scaleAndOrientImages(outputDirectory, imageFilenames):
    outputDirectory.makedirs()

    for imageFilename in imageFilenames:
        image = Image(imageFilename.path)
        orientation = image.attribute(EXIF_ORIENTATION)
        rotation = ROTATIONS[orientation]
        if rotation:
            # This should really fix the EXIF Orientation, but it doesn't.
            image.attribute(EXIF_ORIENTATION, '1')
            image.rotate(rotation)
        orientedFilename = outputDirectory.child("oriented-" + imageFilename.basename())
        image.write(orientedFilename.path)
        geometry = image.size()
        image.scale(Geometry(int(geometry.width() * 0.12), int(geometry.height() * 0.12)))
        scaledFilename = outputDirectory.child("scaled-" + imageFilename.basename())
        image.write(scaledFilename.path)

        # Fix the EXIF metadata, because PythonMagick is busted.
        for written in [orientedFilename, scaledFilename]:
            metadata = ImageMetadata(written.path)
            metadata.read()
            metadata['Exif.Image.Orientation'] = 1
            metadata.write()

if __name__ == '__main__':
    main()
