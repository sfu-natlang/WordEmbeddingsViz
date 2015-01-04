import os, threading, time, json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
#from cluster.models import Upload
from cluster.forms import UploadForm
from WordEmbeddingsViz.settings import MEDIA_ROOT
import bhtsne.bhtsne as tsne


def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.session.exists(request.session.session_key):
                request.session.create()
            print request.session.session_key
            #lang1EmbeddingFile = Upload(embeddingFile= request.FILES['lang1EmbeddingFile'])
            #lang1EmbeddingFile.save()
            lang1EmbeddingFile = request.FILES['lang1EmbeddingFile']
            saveUploadedFile(lang1EmbeddingFile, 'LANG1EMBEDDINGS', request.session.session_key)

            #lang1WordsFile = Upload(embeddingFile= request.FILES['lang1WordsFile'])
            #lang1WordsFile.save()
            lang1WordsFile = request.FILES['lang1WordsFile']
            saveUploadedFile(lang1WordsFile, 'LANG1WORDS', request.session.session_key)

            #lang2EmbeddingFile = Upload(embeddingFile= request.FILES['lang2EmbeddingFile'])
            #lang2EmbeddingFile.save()
            lang2EmbeddingFile = request.FILES['lang2EmbeddingFile']
            saveUploadedFile(lang2EmbeddingFile, 'LANG2EMBEDDINGS', request.session.session_key)

            #lang2WordsFile = Upload(embeddingFile= request.FILES['lang2WordsFile'])
            #lang2WordsFile.save()
            lang2WordsFile = request.FILES['lang2WordsFile']
            saveUploadedFile(lang2WordsFile, 'LANG2WORDS', request.session.session_key)

            return HttpResponseRedirect('/cluster')
    else:
        form = UploadForm()

    return render_to_response('upload.html', {'form': form},
                              context_instance=RequestContext(request))


def cluster(request):
    request.session['done'] = False
    request.session.modified = True
    return render_to_response('cluster.html')


def executeClustering(request):
    clusterThread = tsneThreadClass("tsneThread-"+request.session.session_key, request.session.session_key)
    clusterThread.start()
    while True:
        time.sleep(2)
        if clusterThread.isAlive():
            request.session['done'] = False
        else:
            request.session['done'] = True
            request.session['words'] = clusterThread.words
            request.session['coordinates'] = clusterThread.coordinates
            break
    return HttpResponse('All done.', content_type='text/plain')


def getData(request):
    print "In GetData"
    isItDone = request.session.get('done', False)
    if isItDone:
        words = request.session.get('words', None)
        coordinates = request.session.get('coordinates', None)
        result = {}
        for i, (word, coordinate) in enumerate(zip(words, coordinates)):
            result[i] = {'x':coordinate[0], 'y': coordinate[1], 'word': word}
        result['done'] = True
        jsonStr = json.dumps(result)
        return HttpResponse(jsonStr, content_type='application/javascript')
    else:
        result = {'done': False}
        jsonStr = json.dumps(result)
        return HttpResponse(jsonStr, content_type='application/javascript')


class tsneThreadClass(threading.Thread):
    def __init__(self, threadId, sessionKey):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.sessionKey = sessionKey
        self.words = None
        self.coordinates = None

    def run(self):
        print "Starting thread - " + self.threadId
        word, coordinates = tsneThread(self.threadId, self.sessionKey)
        self.words = word
        self.coordinates = coordinates
        print "Exiting thread - " + self.threadId


def tsneThread(threadId, sessionKey):
    lang1Embeddings = readEmbeddingFile('LANG1EMBEDDINGS', sessionKey)
    lang1Words = readWordsFile('LANG1WORDS', sessionKey)
    lang2Embeddings = readEmbeddingFile('LANG2EMBEDDINGS', sessionKey)
    lang2Words = readWordsFile('LANG2WORDS', sessionKey)
    words = lang1Words+lang2Words

    print threadId + ' - Data reading completed. Extracting coordinates now!'
    coordinates = tsne.bh_tsne(lang1Embeddings+lang2Embeddings)
    coordinates = [coordinate for coordinate in coordinates]
    print threadId + ' - Coordinate extraction complete!'

    if len(words) != len(coordinates):
        raise Exception('Incorrect length of words and coordinates')

    return words, coordinates


def saveUploadedFile(tempFile, fileName, sessionKey):
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'

    if not os.path.exists(folderName):
        os.makedirs(folderName)

    with open(folderName+fileName, 'w') as outFile:
        for chunk in tempFile.chunks():
            outFile.write(chunk)


def readEmbeddingFile(fileName, sessionKey):
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'

    if not os.path.exists(folderName):
        return None

    result = []
    with open(folderName+fileName) as inFile:
        for lineNum, line in enumerate(inFile):
            lineSplit = line.split('\t')
            try:
                assert len(lineSplit) == dims, ('Input line #{} of dimensionality {} although we '
                                                'have previously observed lines with dimensionality {}, '
                                                'possible data error.'
                ).format(lineNum, len(lineSplit, dims))
            except NameError:
                dims = len(lineSplit)
            result.append([float(e) for e in lineSplit])
    return result


def readWordsFile(fileName, sessionKey):
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'

    if not os.path.exists(folderName):
        return None

    result = []
    with open(folderName+fileName) as inFile:
        for line in inFile:
            line = line.strip('\n\r')
            if line:
               result.append(line.strip())
    return result
