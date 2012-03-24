"""
Extra HTML Widget classes
"""

import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe

__all__ = ('SelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')

class SelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    month_field = '%s_month'
    day_field = '%s_day'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, fromyear=-100, toyear=-10):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year + fromyear, this_year + toyear)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = MONTHS.items()
        month_choices.sort()
        local_attrs = self.build_attrs(id=self.month_field % id_)
        month_html = Select(choices=month_choices).render(self.month_field % name, month_val, local_attrs)

        day_choices = [(i, i) for i in range(1, 32)]
        local_attrs['id'] = self.day_field % id_
        day_html = Select(choices=day_choices).render(self.day_field % name, day_val, local_attrs)

        year_choices = [(i, i) for i in self.years]
        local_attrs['id'] = self.year_field % id_
        year_html = Select(choices=year_choices).render(self.year_field % name, year_val, local_attrs)

        output.append(day_html)
        output.append(month_html)
        output.append(year_html)
        
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y, m, d = data.get(self.year_field % name), data.get(self.month_field % name), data.get(self.day_field % name)
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)

# widget for select with optional opt groups
# modified from ticket 3442
# not sure if it's better but it doesn't force all options to be grouped

# Example:
# groceries = ((False, (('milk','milk'), (-1,'eggs'))), ('fruit', ((0,'apple'), (1,'orange'))), ('', (('yum','beer'), )),) 
# grocery_list = GroupedChoiceField(choices=groceries)

# Renders:
# <select name="grocery_list" id="id_grocery_list">
#   <option value="milk">milk</option>
#   <option value="-1">eggs</option>
#   <optgroup label="fruit">
#     <option value="0">apple</option>
#     <option value="1">orange</option>
#   </optgroup>
#   <option value="yum">beer</option>
# </select>

class GroupedSelect(forms.Select): 
    def render(self, name, value, attrs=None, choices=()):
        from django.utils.html import escape
        from django.forms.util import flatatt, smart_unicode 
        if value is None: value = '' 
        final_attrs = self.build_attrs(attrs, name=name) 
        output = [u'<select%s>' % flatatt(final_attrs)] 
        str_value = smart_unicode(value)
        for group_label, group in self.choices: 
            if group_label: # should belong to an optgroup
                group_label = smart_unicode(group_label) 
                output.append(u'<optgroup label="%s">' % escape(group_label)) 
            for k, v in group:
                option_value = smart_unicode(k)
                option_label = smart_unicode(v) 
                selected_html = (option_value == str_value) and u' selected="selected"' or ''
                output.append(u'<option value="%s"%s>%s</option>' % (escape(option_value), selected_html, escape(option_label))) 
            if group_label:
                output.append(u'</optgroup>') 
        output.append(u'</select>') 
        return mark_safe(u'\n'.join(output))
        #return u'\n'.join(output)

# field for grouped choices, handles cleaning of funky choice tuple

class GroupedChoiceField(forms.ChoiceField):
    def __init__(self, choices=(), required=True, widget=GroupedSelect, label=None, initial=None, help_text=None):
        super(forms.ChoiceField, self).__init__(required, widget, label, initial, help_text)
        self.choices = choices
        
    def clean(self, value):
        """
        Validates that the input is in self.choices.
        """
        value = super(forms.ChoiceField, self).clean(value)
        if value in (None, ''):
            value = u''
        value = forms.util.smart_unicode(value)
        if value == u'':
            return value
        valid_values = []
        for group_label, group in self.choices:
            valid_values += [str(k) for k, v in group]
        if value not in valid_values:
            raise ValidationError(gettext(u'Select a valid choice. That choice is not one of the available choices.'))
        return value

