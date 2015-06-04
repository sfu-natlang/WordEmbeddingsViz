__author__ = 'Jasneet Sabharwal <jsabharw@sfu.ca>'

from django import forms


class UploadForm(forms.Form):

    lang1EmbeddingFile = forms.FileField(
        label='Select first language embedding file'
    )
    lang1WordsFile = forms.FileField(
        label='Select first language words file'
    )
    lang1DataFile = forms.FileField(
        label='Select first language data file'
    )

    lang2EmbeddingFile = forms.FileField(
        label='Select second language embedding file'
    )
    lang2WordsFile = forms.FileField(
        label='Select second language words file'
    )
    lang2DataFile = forms.FileField(
        label='Select second language data file'
    )


class UploadEmbeddingsForm(forms.Form):
    coordinatesFile = forms.FileField(
        label='Select Coordinates File',
        help_text='English+Chinese tSNE Coordinates'
    )
    wordsFile = forms.FileField(
        label='Select Words File',
        help_text='<language>\\t<word>'
    )
    lang1DataFile = forms.FileField(
        label='Select first language data file'
    )
    lang2DataFile = forms.FileField(
        label='Select second language data file'
    )
