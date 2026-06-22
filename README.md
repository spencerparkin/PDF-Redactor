# ImageCensor

Censor all images in a given directory.  The idea is that if you can get an E-book converted to a sequence of PNG files, then you can batch process those files to redact all offensive language.  In particular, I'd like to block out swear words and the taking of the Lord's name in vain.

A workflow that seems to work well, given a PDF, is to use Calibre to convert it to EPUB, which seems to give me an HTML file that points to a bunch of PNG or JPG files.  This script can then scrub all the image files.  Calibre can then convert it back into a PDF file.  Walla!  Enjoy your read!