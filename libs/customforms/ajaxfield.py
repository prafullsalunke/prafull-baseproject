import datetime
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django import forms
from django.utils import simplejson

def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs.  It is assumed that the keys do not need to be XML-escaped.
    If the passed dictionary is empty, then return an empty string.
    """
    return u''.join([u' %s="%s"' % (k, conditional_escape(v)) for k, v in attrs.items()])

def widget_url(request, form_name, form_meta):
    tform = AjaxField.implemented_field_list[form_name]
    field_name, vars = form_meta.split('-', 1); vars = vars.split("-")
    element_position = 0
    for f in tform.conditional_list:
        element_position += 1
        if f[0] == field_name:
            break
    current_conditional = tform.widget.conditional_list[element_position][1]
    return HttpResponse(simplejson.dumps(current_conditional(request, *vars)))

class AjaxSelectWidget(forms.Widget):
    def __init__(self, conditional_list, *args, **kwargs):
        self.conditional_list = conditional_list
        super(AjaxSelectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        (fname, floader) = self.conditional_list[0]
        self.parent_field.parent_form.fields[fname].choices = floader(self.parent_field.request, None)

        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        js_attrs = final_attrs
        output = []
     
        for i in range(len(self.conditional_list)):
            cl = self.conditional_list[i]
            if i == len(self.conditional_list)-1:
                cl_next = None
                js = ""
            else:
                cl_next = self.conditional_list[i+1]
                js_attrs['obj_name'] = cl[0]
                js_attrs['obj_next'] = cl_next[0]
                js_attrs['obj_id'] = "id_%s" % cl[0]
                js_attrs['obj_next_id'] = "id_%s" % cl_next[0]

                cleaner_javascript = []
                for j in range(i+1,len(self.conditional_list)):
                    cl_obj = self.conditional_list[j]
                    cleaner_javascript.append("""
                        $('#id_%s').html("<option value=''>Select %s</option>");
                    """ % (cl_obj[0], cl_obj[0]));
                js_attrs['cleaner_js'] = u'\n'.join(cleaner_javascript)

                js = """
                    <script type="text/javascript" charset="utf-8">
                        $(document).ready(function(){
                            $("#%(obj_id)s").change(function(){
                                %(cleaner_js)s
                                var f = $("#%(obj_id)s").val();
                                $.get('/ajax/AjaxField/%(name)s/%(obj_name)s-'+f+'/', function(data){
                                    var data = eval("("+data+")");
                                    $.each(data, function(index, d){
                                        var ele = $("<option></option>").attr("value",d[0]).text(d[1]);
                                        $('#%(obj_next_id)s').append(ele);
                                    });
                                });
                            });
                        });
                    </script>
                """ % (js_attrs)
            output.append(js)
        return mark_safe(u'\n'.join(output))

class AjaxField(forms.ChoiceField):
    """
    Usage :
    from customforms import AjaxField

    class MForm(RequestForm):
        some_random_field = forms.CharField(required=False)
        mfield = AjaxField(conditional_list = [
            ('state', lambda req, x : [(s.id,s.name) for s in State.objects.all()]),
            ('city', lambda req, x : [(c.id, c.name) for c in City.objects.filter(state__id=x)]),
            ('some', lambda req, x : [(1,1),(2,2),(3,3),(4,4)]),
        ])
        AjaxField.register('mfield', mfield)

    urlpatterns += patterns('',
        url(r'^ajax/AjaxField/(?P<form_name>[\w-]+)/(?P<form_meta>[\w-]+)/$', 'customforms.ajaxfield.widget_url'),
    )

    """
    implemented_field_list = {}
    
    def __init__(self, conditional_list=[], required=True, label="", initial=None, widget=AjaxSelectWidget, help_text=""):
        super(AjaxField, self).__init__(choices=(), required=required, widget=AjaxSelectWidget(conditional_list), label=label, initial=initial, help_text=help_text)
        self.conditional_list = conditional_list
        self.widget.parent_field = self
        #print __name__ + "." +  self.__class__.__name__

    def clean(self, value):
        return value

    @classmethod
    def register(cls, field_name, field):
        cls.implemented_field_list.update({field_name : field})
