import logging
import re
import time
import datetime
import os
import hashlib
from django.conf import settings

def context_processor(request):
    d = {
        'currenttime' : datetime.datetime.now(),
        'static_path' : settings.STATIC_PATH,
    }
    return d
