from django.db import models
import hashlib

class SHAField(models.CharField):
    def __init__(self, salt_field, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 40 )
        self.salt_field = salt_field
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add:
            value = self.get_proper_sha(model_instance)
            setattr(model_instance, self.attname, value)
            return value
        else:
            shash = model_instance.shash 
#            shash = self.get_proper_sha(model_instance) 
#            setattr(model_instance, self.attname, shash)
#            return super(models.CharField, self).pre_save(model_instance, add)
            return shash

    def get_proper_sha(self, model_instance):
        mclass = model_instance.__class__
        to_be_shashed = ''.join([getattr(model_instance, val) for val in self.salt_field])
        shavalue = hashlib.sha1(to_be_shashed).hexdigest()
        hashes = [getattr(i, self.attname) for i in mclass.objects.filter(**{"%s__startswith" % self.attname: shavalue[:6]}) if model_instance.pk != i.pk]
        if hashes:
            for i in range(7,41):
                if shavalue[:i] in hashes:
                    pass
                else:
                    value = shavalue[:i]
                    break
        else:
            value = shavalue[:6]

        return value 
