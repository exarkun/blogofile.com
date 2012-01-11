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
        for (prefix, scale) in [('medium-', 0.5), ('small-', 0.125)]:
            image = Image(imageFilename.path)
            orientation = image.attribute(EXIF_ORIENTATION)
            rotation = ROTATIONS[orientation]
            if rotation:
                # This should really fix the EXIF Orientation, but it doesn't.
                image.attribute(EXIF_ORIENTATION, '1')
                image.rotate(rotation)

            # Chop it down
            geometry = image.size()
            width = int(geometry.width() * scale)
            height = int(geometry.height() * scale)
            image.scale(Geometry(width, width))
            scaledFilename = outputDirectory.child(
                prefix + imageFilename.basename())
            image.write(scaledFilename.path)

            if rotation:
                # Fix the EXIF metadata, because PythonMagick is busted.
                metadata = ImageMetadata(scaledFilename.path)
                metadata.read()
                metadata['Exif.Image.Orientation'] = 1
                metadata.write()

if __name__ == '__main__':
    main()
