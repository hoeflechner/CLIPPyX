from PIL import Image
from PIL.ExifTags import TAGS

def get_exifdata(image):
    image
    exifdata = image.getexif()

    exif={}
    for tag_id in exifdata:
    # get the tag name, instead of human unreadable tag id
        tag = str(TAGS.get(tag_id, tag_id))
        data = str(exifdata.get(tag_id))
        exif[tag]=data
    return exif
