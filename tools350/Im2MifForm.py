from django import forms


class Im2MifForm(forms.Form):
    options = ((1, '1'), (3, '3'), (5, '5'), (7, '7'), (15, '15'))
    color_limit = forms.IntegerField(label='color_limit', initial=256, min_value=1, max_value=1024)
    pix_cluster = forms.ChoiceField(widget=forms.Select, label='pix_cluster', choices=options)
    bulk = forms.BooleanField(label='bulk', initial=True, required=False)