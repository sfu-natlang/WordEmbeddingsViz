import os, threading, time, json
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from cluster.forms import UploadForm
from cluster.forms import UploadEmbeddingsForm
from WordEmbeddingsViz.settings import MEDIA_ROOT
from nltk import word_tokenize
from collections import defaultdict
import nltk
import bhtsne.bhtsne as tsne


def upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.session.exists(request.session.session_key):
                request.session.create()
            print request.session.session_key

            lang1EmbeddingFile = request.FILES['lang1EmbeddingFile']
            saveUploadedFile(lang1EmbeddingFile, 'LANG1EMBEDDINGS', request.session.session_key)

            lang1WordsFile = request.FILES['lang1WordsFile']
            saveUploadedFile(lang1WordsFile, 'LANG1WORDS', request.session.session_key)

            lang1DataFile = request.FILES['lang1DataFile']
            saveUploadedFile(lang1DataFile, 'LANG1DATA', request.session.session_key)

            lang2EmbeddingFile = request.FILES['lang2EmbeddingFile']
            saveUploadedFile(lang2EmbeddingFile, 'LANG2EMBEDDINGS', request.session.session_key)

            lang2WordsFile = request.FILES['lang2WordsFile']
            saveUploadedFile(lang2WordsFile, 'LANG2WORDS', request.session.session_key)

            lang2DataFile = request.FILES['lang2DataFile']
            saveUploadedFile(lang2DataFile, 'LANG2DATA', request.session.session_key)

            request.session['is_pre_calc'] = False
            return HttpResponseRedirect('/cluster')
    else:
        form = UploadForm()

    return render_to_response('upload.html', {'form': form},
                              context_instance=RequestContext(request))


def uploadCoordinates(request):
    if request.method == 'POST':
        form = UploadEmbeddingsForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.session.exists(request.session.session_key):
                request.session.create()
            print request.session.session_key

            coordinatesFile = request.FILES['coordinatesFile']
            saveUploadedFile(coordinatesFile, 'PRECAL_COORDINATES', request.session.session_key)

            wordsFile = request.FILES['wordsFile']
            saveUploadedFile(wordsFile, 'PRECAL_WORDS',  request.session.session_key)

            lang1DataFile = request.FILES['lang1DataFile']
            saveUploadedFile(lang1DataFile, 'LANG1DATA', request.session.session_key)

            lang2DataFile = request.FILES['lang2DataFile']
            saveUploadedFile(lang2DataFile, 'LANG2DATA', request.session.session_key)

            request.session['is_pre_calc'] = True
            return HttpResponseRedirect('/cluster')
    else:
        form = UploadEmbeddingsForm()
    return render_to_response('upload-coordinates.html', {'form': form},
                              context_instance=RequestContext(request))


def cluster(request):
    request.session['done'] = False
    request.session.modified = True
    return render_to_response('cluster.html')


def executeClustering(request):
    isPreCalc = request.session.get('is_pre_calc', False)
    request.session['lang1Concordance'] = loadLangConcordance('LANG1DATA', request.session.session_key)
    request.session['lang2Concordance'] = loadLangConcordance('LANG2DATA', request.session.session_key)

    if isPreCalc:
        print 'EXECUTING CLUSTERING - PRECALCULATED'
        request.session['words'] = readPreCalcWords(request.session.session_key)
        request.session['coordinates'] = readPreCalcCoordinates(request.session.session_key)
        request.session['done'] = True
    else:
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
    print isItDone
    if isItDone:
        words = request.session.get('words', None)
        coordinates = request.session.get('coordinates', None)
        result = {}
        for i, ((lang, word), coordinate) in enumerate(zip(words, coordinates)):
            result[i] = {'x': coordinate[0], 'y': coordinate[1], 'word': word, 'lang': lang}
        result['done'] = True
        jsonStr = json.dumps(result)
        return HttpResponse(jsonStr, content_type='application/javascript')
    else:
        result = {'done': False}
        jsonStr = json.dumps(result)
        return HttpResponse(jsonStr, content_type='application/javascript')


def getLangConcordance(request):
    print 'REQUESTING CONCORDANCE'
    if request.method == 'POST':
        word = request.POST.get('word')
        language = request.POST.get('language')

        if language == 'LANG1':
            concordanceIndex = request.session['lang1Concordance']
        elif language == 'LANG2':
            concordanceIndex = request.session['lang2Concordance']

        concordance = getConcordance(word, concordanceIndex['tokens'], concordanceIndex['offsets'])
        print concordance

        result = {'concordance': concordance}
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
    print 'tsneThread'
    lang1Embeddings = readEmbeddingFile('LANG1EMBEDDINGS', sessionKey)
    lang1Words = readWordsFile('LANG1WORDS', sessionKey)
    lang2Embeddings = readEmbeddingFile('LANG2EMBEDDINGS', sessionKey)
    lang2Words = readWordsFile('LANG2WORDS', sessionKey)
    words = []
    for word in lang1Words:
        words.append(('lang1', word))
    for word in lang2Words:
        words.append(('lang2', word))

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


def readPreCalcWords(sessionKey):
    print 'READING PRECALC WORDS'
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None
    result = []
    prevLang = ''
    langNum = 0
    with open(folderName+'PRECAL_WORDS') as inFile:
        for line in inFile:
            line = line.strip('\n\r')
            if line:
                lineSplit = line.split('\t')
                if not (lineSplit[0].strip() == prevLang):
                    prevLang = lineSplit[0].strip()
                    langNum += 1
                    langName = 'lang'+str(langNum)
                result.append((langName, lineSplit[1].strip()))
    return result


def readPreCalcCoordinates(sessionKey):
    print 'READING PRECALC COORDINATES'
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    result = []
    with open(folderName+'PRECAL_COORDINATES') as inFile:
        for line in inFile:
            line = line.strip('\n\r')
            if line:
                lineSplit = line.split()
                result.append([float(lineSplit[0].strip()), float(lineSplit[1].strip())])
    return result


def loadLangConcordance(fileName, sessionKey):
    """
    The functionality of this function has been copied over from
    NLTK ConcordanceIndex.
    """
    print 'READING CONCONDANCE - ' + fileName
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    result = ''
    with open(folderName+fileName) as inFile:
        for line in inFile:
            line = line.strip('\r\n').strip()
            if line:
                result += line + ' '

    tokens = word_tokenize(result.decode('utf8').lower())
    offsets = defaultdict(list)
    for index, word in enumerate(tokens):
        offsets[word.lower()].append(index)

    return {'tokens': tokens, 'offsets': offsets}


def getConcordance(word, tokens, offsets, width=75, lines=25):
    """
    This function is copied from print_concordance function in NLTK
    """

    word = word.encode('utf-8').decode('utf-8')

    half_width = (width - len(word) - 2) // 2
    context = width // 4 # approx number of words of context

    offsets = getOffsets(offsets, word)

    result = []
    if offsets:
        lines = min(lines, len(offsets))
        for i in offsets:
            if lines <= 0:
                break
            left = (' ' * half_width +
                    ' '.join(tokens[i-context:i]))
            right = ' '.join(tokens[i+1:i+context])
            left = left[-half_width:]
            right = right[:half_width]
            result.append(left.strip() + ' ' + tokens[i].strip() + ' ' + right.strip())
            lines -= 1
    return result


def getOffsets(offsets, word):
    if word.lower() in offsets:
        return offsets[word.lower()]
    else:
        return []
