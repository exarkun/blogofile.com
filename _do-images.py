#!/usr/bin/python

from sys import argv

from twisted.python.filepath import FilePath

from PythonMagick import Image
from PythonMagick._PythonMagick import Geometry

from pyexiv2 import ImageMetadata

ROTATIONS = {
    '6': 90,
    '1': 0,
    }

EXIF_ORIENTATION = "EXIF:Orientation"

def main():
    for imageFilename in map(FilePath, argv[1:]):
        image = Image(imageFilename.path)
        orientation = image.attribute(EXIF_ORIENTATION)
        rotation = ROTATIONS[orientation]
        if rotation:
            # This should really fix the EXIF Orientation, but it doesn't.
            image.attribute(EXIF_ORIENTATION, '1')
            image.rotate(rotation)
        orientedFilename = imageFilename.sibling("oriented-" + imageFilename.basename())
        image.write(orientedFilename.path)
        geometry = image.size()
        image.scale(Geometry(int(geometry.width() * 0.12), int(geometry.height() * 0.12)))
        scaledFilename = imageFilename.sibling("scaled-" + imageFilename.basename())
        image.write(scaledFilename.path)

        # Fix the EXIF metadata, because PythonMagick is busted.
        for written in [orientedFilename, scaledFilename]:
            metadata = ImageMetadata(written.path)
            metadata.read()
            metadata['Exif.Image.Orientation'] = 1
            metadata.write()

if __name__ == '__main__':
    main()
