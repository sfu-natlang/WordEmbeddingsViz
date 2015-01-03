import os

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse

#from cluster.models import Upload
from cluster.forms import UploadForm
from WordEmbeddingsViz.settings import MEDIA_ROOT


def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.session.exists(request.session.session_key):
                request.session.create()

            #lang1EmbeddingFile = Upload(embeddingFile= request.FILES['lang1EmbeddingFile'])
            #lang1EmbeddingFile.save()
            lang1EmbeddingFile = request.FILES['lang1EmbeddingFile']
            handleUploadedFile(lang1EmbeddingFile, 'LANG1EMBEDDINGS', request.session.session_key)

            #lang1WordsFile = Upload(embeddingFile= request.FILES['lang1WordsFile'])
            #lang1WordsFile.save()
            lang1WordsFile = request.FILES['lang1WordsFile']
            handleUploadedFile(lang1WordsFile, 'LANG1WORDS', request.session.session_key)

            #lang2EmbeddingFile = Upload(embeddingFile= request.FILES['lang2EmbeddingFile'])
            #lang2EmbeddingFile.save()
            lang2EmbeddingFile = request.FILES['lang2EmbeddingFile']
            handleUploadedFile(lang2EmbeddingFile, 'LANG2EMBEDDINGS', request.session.session_key)

            #lang2WordsFile = Upload(embeddingFile= request.FILES['lang2WordsFile'])
            #lang2WordsFile.save()
            lang2WordsFile = request.FILES['lang2WordsFile']
            handleUploadedFile(lang2WordsFile, 'LANG2WORDS', request.session.session_key)

            return HttpResponseRedirect('/cluster/'+request.session.session_key)
    else:
        form = UploadForm()

    return render_to_response('upload.html', {'form': form},
                              context_instance=RequestContext(request))


def cluster(request, sessionKey):
    return HttpResponse('Hello world from Cluster method - '+sessionKey)


def handleUploadedFile(tempFile, fileName, sessionKey):
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'

    if not os.path.exists(folderName):
        os.makedirs(folderName)

    with open(folderName+fileName, 'w') as outFile:
        for chunk in tempFile.chunks():
            outFile.write(chunk)


