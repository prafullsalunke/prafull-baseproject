from django.utils.encoding import force_unicode
from django.db import models
import os.path

class RenameFilesModel(models.Model):
    RENAME_FILES = {}
    
    class Meta:
        abstract = True
    
    def save(self, force_insert=False, force_update=False):
        rename_files = getattr(self, 'RENAME_FILES', None)
        if rename_files:
            super(RenameFilesModel, self).save(force_insert, force_update)
            force_insert, force_update = False, False
            
            for field_name, options in rename_files.iteritems():
                field = getattr(self, field_name)
                file_name = force_unicode(field)
                name, ext = os.path.splitext(file_name)
                keep_ext = options.get('keep_ext', True)
                final_dest = options['dest']
                if callable(final_dest):
                    final_name = final_dest(self, file_name)
                else:
                    final_name = os.path.join(final_dest, '%s' % (self.pk,))
                    if keep_ext:
                        final_name += ext
                if file_name != final_name:
                    field.storage.delete(final_name)
                    if file_name:
                        field.storage.save(final_name, field)
                        field.storage.delete(file_name)
                        setattr(self, field_name, final_name)
                        force_update = False
                else:
                    force_update = False;

        super(RenameFilesModel, self).save(force_insert, force_update)
