""" definition of input forms for the context app """
from django import forms
from config.models import *
from config.langs import *


class ContextAddForm(forms.Form):
    VOCABS = (
        ('', 'Choose a vocabulary...'),
        ('https://www.w3.org/2001/XMLSchema#', 'XML Schema Datatypes'),
        ('http://schema.org', 'Schema.org'),
        ('http://purl.org/dc/terms', 'Dublin Core (DC) Terms')
    )
    prj = forms.ModelChoiceField(label="Project",
                                 empty_label="Select a project",
                                 queryset=Projects.objects.all(),
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    name = forms.CharField(label="Name", max_length=64, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    desc = forms.CharField(label="Description", max_length=128,
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    file = forms.CharField(label="Filename", max_length=64, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    version = forms.CharField(label="Version", max_length=64,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    lang = forms.ChoiceField(label="Language", choices=langs, required=True,
                             widget=forms.Select(attrs={'class': 'form-control'}))
    vocab = forms.ChoiceField(label="Vocabulary", choices=VOCABS, initial='unk',
                              widget=forms.Select(attrs={'class': 'form-control'}))
