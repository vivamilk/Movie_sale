import PIL
from PIL import Image
import glob, os


for infile in glob.glob("*.jpg"):
    file, ext = os.path.splitext(infile)
    im = Image.open(infile)
    im = im.resize((200, 300), Image.ANTIALIAS)
    im.save(file+".jpg", "JPEG")
