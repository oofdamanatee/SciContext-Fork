""" definition of input forms for the server app """
from django import forms


class ServerAddForm(forms.Form):
    TYPES = (
        ('ols', 'OLS (EBI)'),
        ('bio', 'OntoPortal'),
        ('bee', 'Ontobee'),
        ('otr', 'Other'),
        ('unk', 'Unknown')
    )
    name = forms.CharField(label="Name", max_length=64, required=True,
                           widget=forms.TextInput(
                               attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter a name for the server'
                               })
                           )
    abbrev = forms.CharField(label="Abbreviation", max_length=64,
                             widget=forms.TextInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Enter an abbreviation for the server'
                                 })
                             )
    desc = forms.CharField(label="Description", max_length=128,
                           widget=forms.Textarea(
                               attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter a description of the server',
                                   'rows': '3'
                               })
                           )
    type = forms.ChoiceField(label="Type", choices=TYPES, initial='unk', required=True,
                             widget=forms.Select(
                                 attrs={
                                     'class': 'form-control'
                                 })
                             )
    home = forms.URLField(label="Homepage", max_length=128, required=True,
                          widget=forms.URLInput(
                              attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Enter the homepage URL of the server'
                              })
                          )
    apiurl = forms.URLField(label="API URL", max_length=256, required=True,
                            widget=forms.URLInput(
                                attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter the API URL of the server'
                                })
                            )
    apikey = forms.CharField(label="API Key", max_length=256,
                             widget=forms.TextInput(
                                 attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Enter the API key for the server (may need account...)'
                                 }))
    version = forms.CharField(label="Version", max_length=64,
                              widget=forms.TextInput(
                                  attrs={
                                      'class': 'form-control',
                                      'placeholder': 'Enter the OLS/OntoPortal server version'
                                  })
                              )
