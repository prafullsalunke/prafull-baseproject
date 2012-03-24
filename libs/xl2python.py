import datetime, time
import xlrd
import csv

"""
Usage: 

upload_field_map = [
    'agent_id',
    ('app_id', 'float'),     # Cast into float field
    'fsc_bank_name',
    'fsc_branch_name',
    'fsc_source_code',
     None,                   # Not Needed
    'jet_decision',
    'product_code',
     ('trigger_date', 'datetime','%Y-%m-%d %H:%M:%S'),   # Datetime field
     ('closure_date', 'date', '%Y/%m/%d'),               # Date field
]

class Uploader(Xl2Python):
    pass
    
    def clean_mobile(self, val):
        if len(val) < 10:
            raise XlError("Less than 10 characters")
        if len(val) > 10:
            return str(int(val[-10:]))
        else:
            return str(int(val))

# View
def upload_view(request):
    xlm = Uploader(upload_field_map, request.FILES['ufile'])
    if xlm.is_valid():
        print xlm.cleaned_data
    else:
        print xlm.errors

Supported Types : datetime, date, float, int

To add more supported types, just keep adding parameters on my one, and passing it to field_<supported_type> method

Write your clean_<column> methods to clean a column, return the modified value

Write your clean_row method(self, row_data) to clean each row after all columns are cleaned, must return modified row_data

"""
####################### Xl2Python ######################

class XlError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Xl2Python(object):
    pass
    
    @property
    def nrows(self):
        if self.dtype == "XLS":
            return self.import_sheet.nrows
        if self.dtype == "CSV":
            return len(self.import_sheet)
    
    @property
    def ncols(self):
        if self.dtype == "XLS":
            return self.import_sheet.ncols
        if self.dtype == "CSV":
            return len(self.import_sheet[0])
    
    def cell_data(self, i ,j):
        if self.dtype == "XLS":
            return self.import_sheet.cell_value(rowx=i, colx=j)
        if self.dtype == "CSV":
            return self.import_sheet[i][j]

    def __init__(self, field_map, file_handle, dtype="XLS", delimiter='|', quotechar=None):
        self.dtype = dtype
        if self.dtype == "XLS":
            self.import_wb = xlrd.open_workbook(file_contents=file_handle.read())
            self.import_sheet = self.import_wb.sheet_by_index(0)
        if self.dtype == "CSV":
            self.import_sheet = []
            sp = csv.reader(file_handle, 
                delimiter='|', 
                quotechar = '\x07',
                lineterminator = '\n',
                doublequote = False,
                skipinitialspace = False,
                quoting = csv.QUOTE_NONE,
                escapechar = '\\'
            )
            for r in sp:
                print r
                self.import_sheet.append(r)
            print self.import_sheet

        self.field_map = field_map
        
        self.cleaned_data = []
        self.errors = []

    
    def is_valid(self):
        for rx in range(1, self.nrows):
            if not self.cell_data(rx, 0):
                continue
            #if True:
            try:
                object_value_dict = {}
                for cx in [i for i in range(0, self.ncols) if self.field_map[i]]:
                    cell_value = self.cell_data(rx, cx)
                    
                    fvalue = self.field_map[cx]
                    if type(fvalue) == tuple:
                        fname = fvalue[0]
                        field_type = fvalue[1]
                        params = fvalue[2:]
                        field_cleaner = getattr(self, 'field_%s' % field_type)
                        cell_value = field_cleaner(cell_value, *params)
                    else:
                        fname = fvalue

                    cleaner = getattr(self, 'clean_%s' % fname, None)
                    if cleaner:
                        cell_value = cleaner(cell_value)
                   
                    object_value_dict[fname] = cell_value
                    
                row_cleaner = getattr(self, 'clean_row', None) 
                if row_cleaner:
                    object_value_dict = row_cleaner(object_value_dict.copy())
                    
                self.cleaned_data.append(object_value_dict)

            #else:
            except Exception, e:
                self.errors.append({'row':rx, 'column':cx, 'error':str(e)})
        
        if self.errors:
            return False
        else:
            return True

    def field_datetime(self, val, format):
        if type(val) == float:
            return datetime.datetime(*xlrd.xldate_as_tuple(val,self.import_wb.datemode))
        else:
            return datetime.datetime.fromtimestamp(time.mktime(time.strptime(val, format)))

    def field_date(self, val, format):
        if type(val) == float:
            return datetime.datetime(*xlrd.xldate_as_tuple(val,self.import_wb.datemode)).date()
        else:
            return datetime.datetime.fromtimestamp(time.mktime(time.strptime(val, format))).date()
    
    def field_float(self, val):
        return float(val)

    def field_int(self, val):
        return int(val)

#######################################################
    
