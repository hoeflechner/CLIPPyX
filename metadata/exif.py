from PIL import Image
from PIL.ExifTags import TAGS

def get_exifdata(imagename):
    image = Image.open(imagename)
    exifdata = image.getexif()
    
    str=""
    for tag_id in exifdata:
    # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        if data!="":
            str+=f"{tag}: {data}\n"
    return str
