# -*- encoding: utf-8 -*-
"""
django-thumbs by Antonio Melé
http://django.es
"""
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import Image
from django.core.files.base import ContentFile
import cStringIO
from django.conf import settings

import uuid
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from math import atan, degrees
import sys
import os

FONT = os.path.join(settings.SETTINGS_FILE_FOLDER ,settings.MEDIA_ROOT ,'verdana.ttf') 

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def watermarkImage(filename, text, outfilename):
    filename.seek(0) # see http://code.djangoproject.com/ticket/8222 for details
    img = Image.open(filename)
    if img.mode not in ('L', 'RGB'):
        img.convert("RGB")
    watermark = Image.new("RGBA", (img.size[0], img.size[1]))
    draw = ImageDraw.ImageDraw(watermark, "RGBA")
    size = 20
    font = ImageFont.truetype(FONT, size)
    textwidth, textheight = font.getsize(text)
    while True:
        size += 1
        nextfont = ImageFont.truetype(FONT, size)
        nexttextwidth, nexttextheight = nextfont.getsize(text)
        if nexttextwidth+nexttextheight/3 > watermark.size[0]:
            break
        font = nextfont
        textwidth, textheight = nexttextwidth, nexttextheight
    draw.setfont(font)
    draw.text(((watermark.size[0]-textwidth)/2,
               (watermark.size[1]-textheight)/2), text)
    watermark = watermark.rotate(degrees(atan(float(img.size[1])/
                                              img.size[0])),
                                 Image.BICUBIC)
    mask = watermark.convert("L").point(lambda x: min(x, 55))
    watermark = reduce_opacity(watermark,0.6)
    img.paste(watermark, None, watermark)
    
    io = cStringIO.StringIO()
    # PNG and GIF are the same, JPG is JPEG
    format = 'JPEG'
    
    img.save(io, format)
    return ContentFile(io.getvalue())    

def generate_thumb(img, thumb_size, square, format):
    """
    Generates a thumbnail image and returns a ContentFile object with the thumbnail
    
    Parameters:
    ===========
    img         File object
    
    thumb_size  desired thumbnail size, ie: (200,120)
    
    format      format of the original image ('jpeg','gif','png',...)
                (this format will be used for the generated thumbnail, too)
    """
    img.seek(0) # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(img)
    
    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
        
    # get size
    thumb_postfix, thumb_w, thumb_h = thumb_size
    # If you want to generate a square thumbnail
    #if thumb_w == thumb_h:
    if square:
        # quad
        xsize, ysize = image.size
        # get minimum size
        minsize = min(xsize,ysize)
        # largest square possible in the image
        xnewsize = (xsize-minsize)/2
        ynewsize = (ysize-minsize)/2
        # crop it
        image2 = image.crop((xnewsize, ynewsize, xsize-xnewsize, ysize-ynewsize))
        # load is necessary after crop                
        image2.load()
        # thumbnail of the cropped image (with ANTIALIAS to make it look better)
        image2.thumbnail(thumb_size, Image.ANTIALIAS)
    else:
        # not quad
        image2 = image
        image2.thumbnail(thumb_size, Image.ANTIALIAS)
    
    io = cStringIO.StringIO()
    # PNG and GIF are the same, JPG is JPEG
    if format.upper()=='JPG':
        format = 'JPEG'
    
    image2.save(io, format)
    return ContentFile(io.getvalue())    

class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    See ImageWithThumbsField for usage example
    """
    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)
        self.sizes = self.field.sizes
        self.square = self.field.square
        self.watermark_text = self.field.watermark_text
        
        if self.sizes:
            def get_size(self, size):
                if not self:
                    return ''
                else:
                    split = self.url.rsplit('.',1)
                    #thumb_url = '%s.%sx%s.%s' % (split[0],w,h,split[1])
                    thumb_url = '%s_%s.%s' % (split[0],postfix,split[1])
                    return thumb_url
                    
            for size in self.sizes:
                (postfix,w,h) = size
                setattr(self, 'url_%s' % (postfix), get_size(self, size))
                
    def save(self, name, content, save=True):
       
        if self.watermark_text:
            sp = os.path.splitext(self.name)
            originalfilename = 'original/%s_%s%s' % (sp[0],str(uuid.uuid1()).split("-")[0],sp[1])
            original = self.storage.save(originalfilename, content)        
            content = watermarkImage(content, self.watermark_text,content) 
        
        super(ImageWithThumbsFieldFile, self).save(name, content, save)
        
        if self.sizes:
            for size in self.sizes:
                (postfix,w,h) = size
                split = self.name.rsplit('.',1)
                #thumb_name = '%s.%sx%s.%s' % (split[0],w,h,split[1])
                thumb_name = '%s_%s.%s' % (split[0],postfix,split[1])
                
                # you can use another thumbnailing function if you like
                thumb_content = generate_thumb(content, size, self.square, split[1])
                
                thumb_name_ = self.storage.save(thumb_name, thumb_content)        
                
                if not thumb_name == thumb_name_:
                    raise ValueError('There is already a file named %s' % thumb_name)
        
    def delete(self, save=True):
        name=self.name
        super(ImageWithThumbsFieldFile, self).delete(save)
        if self.sizes:
            for size in self.sizes:
                (postfix,w,h) = size
                split = name.rsplit('.',1)
                #thumb_name = '%s.%sx%s.%s' % (split[0],w,h,split[1])
                thumb_name = '%s_%s.%s' % (split[0],postfix,split[1])
                try:
                    self.storage.delete(thumb_name)
                except:
                    pass
                        
class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile
    """
    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=(('s',125,125),('m',300,200),)
    
    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_125x125
        my_object.photo.url_300x200
    
    Note: The 'sizes' attribute is not required. If you don't provide it, 
    ImageWithThumbsField will act as a normal ImageField
        
    How it works:
    =============
    For each size in the 'sizes' atribute of the field it generates a 
    thumbnail with that size and stores it following this format:
    
    available_filename.[width]x[height].extension

    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.
    
    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)
    
    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg
    
    Note: django-thumbs assumes that if filename "any_filename.jpg" is available 
    filenames with this format "any_filename.[widht]x[height].jpg" will be available, too.
    
    To do:
    ======
    Add method to regenerate thubmnails
    
    """
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, sizes=None, square=False,watermark_text='', **kwargs):
        self.verbose_name=verbose_name
        self.name=name
        self.width_field=width_field
        self.height_field=height_field
        self.sizes = sizes
        self.square = square
        self.watermark_text = watermark_text
        super(ImageField, self).__init__(**kwargs)
