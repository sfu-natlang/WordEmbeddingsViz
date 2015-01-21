__author__ = 'Jasneet Sabharwal <jsabharw@sfu.ca>'

from django import forms


class UploadForm(forms.Form):

    lang1EmbeddingFile = forms.FileField(
        label='Select first language embedding file',
        help_text='English'
    )
    lang1WordsFile = forms.FileField(
        label='Select first language words file',
        help_text='English'
    )

    lang2EmbeddingFile = forms.FileField(
        label='Select second language embedding  file',
        help_text='Chinese'
    )
    lang2WordsFile = forms.FileField(
        label='Select second language words file',
        help_text='English'
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
