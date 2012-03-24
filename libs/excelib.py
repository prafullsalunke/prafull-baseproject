# imports #
import time
import datetime
import csv, codecs, cStringIO
import StringIO

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

import xlrd
import xlwt
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment, Style

excel_color_map = { 
    'rgb(0, 0, 0)': -7, 
    'rgba(0, 0, 0, 0)': -7, 
    'rgb(255, 255, 255)':2, 
    'rgb(255, 0, 0)':3, 
    'rgb(0, 255, 0)':4, 
    'rgb(0, 0, 255)':5, 
    'rgb(255, 255, 0)':6, 
    'rgb(255, 0, 255)':7, 
    'rgb(0, 255, 255)':8, 
    'rgb(128, 0, 0)':9, 
    'rgb(0, 128, 0)':10, 
    'rgb(0, 0, 128)':11, 
    'rgb(128, 128, 0)':12, 
    'rgb(128, 0, 128)':13, 
    'rgb(0, 128, 128)':14, 
    'rgb(192, 192, 192)':15, 
    'rgb(128, 128, 128)':16, 
    'rgb(153, 153, 255)':17, 
    'rgb(153, 51, 102)':18, 
    'rgb(255, 255, 204)':19, 
    'rgb(204, 255, 255)':20, 
    'rgb(102, 0, 102)':21, 
    'rgb(255, 128, 128)':22, 
    'rgb(0, 102, 204)':23, 
    'rgb(204, 204, 255)':24, 
    'rgb(0, 0, 128)':25, 
    'rgb(255, 0, 255)':26, 
    'rgb(255, 255, 0)':27, 
    'rgb(0, 255, 255)':28, 
    'rgb(128, 0, 128)':29, 
    'rgb(128, 0, 0)':30, 
    'rgb(0, 128, 128)':31, 
    'rgb(0, 0, 255)':32, 
    'rgb(0, 204, 255)':33, 
    'rgb(204, 255, 255)':34, 
    'rgb(204, 255, 204)':35, 
    'rgb(255, 255, 153)':36, 
    'rgb(153, 204, 255)':37, 
    'rgb(255, 153, 204)':38, 
    'rgb(204, 153, 255)':39, 
    'rgb(255, 204, 153)':40, 
    'rgb(51, 102, 255)':41, 
    'rgb(51, 204, 204)':42, 
    'rgb(153, 204, 0)':43, 
    'rgb(255, 204, 0)':44, 
    'rgb(255, 153, 0)':45, 
    'rgb(255, 102, 0)':46, 
    'rgb(102, 102, 153)':47, 
    'rgb(150, 150, 150)':48, 
    'rgb(0, 51, 102)':49, 
    'rgb(51, 153, 102)':50, 
    'rgb(0, 51, 0)':51, 
    'rgb(51, 51, 0)':52, 
    'rgb(153, 51, 0)':53, 
    'rgb(153, 51, 102)':54, 
    'rgb(51, 51, 153)':55, 
    'rgb(51, 51, 51)':56, 
    #'rgb(153, 153, 153)':56, 
}

def excel_generator(filename, order, sqldict):
    data_row_list  = []
    for s in sqldict:
        r = []
        for i in order:
            r.append(s[i])
        data_row_list.append(r)
    return render_excel(filename, order, data_row_list)

def render_excel(filename, col_title_list, data_row_list):
    output = StringIO.StringIO()
    export_wb = Workbook()
    export_sheet = export_wb.add_sheet('Export')
    col_idx = 0
    for col_title in col_title_list:
        export_sheet.write(0, col_idx, col_title)
        col_idx += 1
    row_idx = 1
    s = XFStyle()
    for row_item_list in data_row_list:
        col_idx = 0
        for current_value in row_item_list:
            if current_value:
                current_value_is_date = False
                if isinstance(current_value, datetime.datetime):
                    current_value = xlrd.xldate.xldate_from_datetime_tuple((current_value.year, current_value.month, \
                                                    current_value.day, current_value.hour, current_value.minute, \
                                                    current_value.second), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.date):
                    current_value = xlrd.xldate.xldate_from_date_tuple((current_value.year, current_value.month, \
                                                    current_value.day), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.time):
                    current_value = xlrd.xldate.xldate_from_time_tuple((current_value.hour, current_value.minute, \
                                                    current_value.second))
                    current_value_is_date = True
                elif isinstance(current_value, models.Model):
                    current_value = str(current_value)
                if current_value_is_date:
                    s.num_format_str = 'M/D/YY'
                    export_sheet.write(row_idx, col_idx, current_value, s)
                else:
                    export_sheet.write(row_idx, col_idx, current_value)
            col_idx += 1
        row_idx += 1
    export_wb.save(output)
    output.seek(0)
    response = HttpResponse(output.getvalue())
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

def render_excel_to_file(filename, col_title_list, data_row_list):
    output = StringIO.StringIO()
    export_wb = Workbook()
    export_sheet = export_wb.add_sheet('Export')
    col_idx = 0
    s = XFStyle()
    s.num_format_str = 'M/D/YY'
    for col_title in col_title_list:
        export_sheet.write(0, col_idx, col_title)
        col_idx += 1
    row_idx = 1
    for row_item_list in data_row_list:
        col_idx = 0
        for current_value in row_item_list:
            if current_value:
                current_value_is_date = False
                if isinstance(current_value, datetime.datetime):
                    current_value = xlrd.xldate.xldate_from_datetime_tuple((current_value.year, current_value.month, \
                                                    current_value.day, current_value.hour, current_value.minute, \
                                                    current_value.second), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.date):
                    current_value = xlrd.xldate.xldate_from_date_tuple((current_value.year, current_value.month, \
                                                    current_value.day), 0)
                    current_value_is_date = True
                elif isinstance(current_value, datetime.time):
                    current_value = xlrd.xldate.xldate_from_time_tuple((current_value.hour, current_value.minute, \
                                                    current_value.second))
                    current_value_is_date = True
                elif isinstance(current_value, models.Model):
                    current_value = str(current_value)
                if current_value_is_date:
                    """
                    s = XFStyle()
                    s.num_format_str = 'M/D/YY'
                    """
                    export_sheet.write(row_idx, col_idx, current_value, s)
                else:
                    export_sheet.write(row_idx, col_idx, current_value)
            col_idx += 1
        row_idx += 1
    export_wb.save(filename)

def render_custom_excel_to_file(filename, data_dict):
    output = StringIO.StringIO()
    export_wb = Workbook()
    export_sheet = export_wb.add_sheet('Export')
    row_idx=0
    for row_item_list in data_dict:
        col_idx = 0
        for current_value in row_item_list:
            css = current_value.copy()
            css.pop('data')
            print css['background-color']
            if css['background-color'] == 'transparent':
                css['background-color'] = 'rgb(0, 0, 0)' 
            if css['font-weight'] == '700':
                css['font-weight'] == 'BOLD'
            custom_xf = css2excel(css)
            try:
                export_sheet.write(row_idx, col_idx, current_value['data'], custom_xf)
            except Exception, e:
                print "Exception raised", current_value['data'], custom_xf
                export_sheet.write(row_idx, col_idx, current_value['data'], xlwt.easyxf('font: italic on size 30; pattern: pattern solid, fore-colour grey25'))
            col_idx += 1
        row_idx += 1
    #export_wb.save(filename)
    export_wb.save(output)
    output.seek(0)
    response = HttpResponse(output.getvalue())
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

def css2excel(css):
    #custom_css = 'font: name "%s", %s on'%(current_value['font-family'].split(",")[0], current_value['font-weight'].split(",")[0])
    #export_sheet.write(row_idx, col_idx, current_value['data'], xlwt.easyxf('font: italic on; pattern: pattern solid, fore-colour grey25'))
    xf_list = []
    fnt = Font()
    borders = Borders()
    pattern = Pattern()
    align = Alignment()

    process_css = {
        'font-family' : [fnt, "name" , lambda x : x.split(",")[0]],
        'color' : [fnt, "colour_index", lambda x : excel_color_map.get(x,0)+8],
        'font-weight' : [fnt, "bold", lambda x : x.upper() == 'BOLD'],
        #'font-weight' : [fnt, "bold", lambda x : x == '700'],
        'text-align' : [align, "horz", lambda x : {'left':align.HORZ_LEFT, 'right':align.HORZ_RIGHT, 'center':align.HORZ_CENTER, 'justified': align.HORZ_JUSTIFIED}[x]],
        'background-color' : [pattern,"pattern_fore_colour", lambda x: excel_color_map.get(x,16)+8],
    }
    #TODO process_css -> css
    for i in process_css.keys():
        #print process_css[i][0] ,".",process_css[i][1], " => " , css[i] ,"  |  ", process_css[i][2](css[i]) 
        setattr(process_css[i][0], process_css[i][1], process_css[i][2](css[i]))

    style = XFStyle()
    style.font = fnt
    borders.left = Borders.THIN
    borders.right = Borders.THIN
    borders.top = Borders.THIN
    borders.bottom = Borders.THIN
    style.borders = borders
    style.pattern = pattern
    style.pattern.pattern = 1
    style.alignment = align

    return style
