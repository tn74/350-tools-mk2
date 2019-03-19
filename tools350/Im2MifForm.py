from django import forms


class Im2MifForm(forms.Form):

    color_limit = forms.IntegerField(label='color_limit', initial=-1)
    comp_ratio = forms.IntegerField(label='comp_ratio', initial=0, max_value=99, min_value=0)
    bulk = forms.BooleanField(label='bulk', initial=True)