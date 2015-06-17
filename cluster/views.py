import os, threading, time, json, operator
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from cluster.forms import UploadForm
from cluster.forms import UploadEmbeddingsForm
from WordEmbeddingsViz.settings import MEDIA_ROOT
from nltk import word_tokenize
from collections import defaultdict
import nltk
import bhtsne.bhtsne as tsne
import sys


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

            if 'alignmentFile' in request.FILES:
                alignmentFile = request.FILES['alignmentFile']
                saveUploadedFile(alignmentFile, 'ALIGNMENTDATA', request.session.session_key)
                request.session['align_avail'] = True
            else:
                request.session['align_avail'] = False

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

            if 'alignmentFile' in request.FILES:
                alignmentFile = request.FILES['alignmentFile']
                saveUploadedFile(alignmentFile, 'ALIGNMENTDATA', request.session.session_key)
                request.session['align_avail'] = True
            else:
                request.session['align_avail'] = False

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
    request.session['lang1Concordance'], request.session['vocabPOS'], request.session['vocabCount'] = \
        loadLangConcordance('LANG1DATA', True, request.session.session_key, 25)
    request.session['lang2Concordance'] = loadLangConcordance('LANG2DATA', False, request.session.session_key, 25)

    if request.session.get('align_avail', False):
        request.session['previousAlignments'] = loadPreviousAlignments('ALIGNMENTDATA', request.session.session_key)

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
        vocabPOS = request.session.get('vocabPOS', None)
        vocabCount = request.session.get('vocabCount', None)
        finalVocabPOS = filterVocabByCount(vocabCount, vocabPOS, 100)

        previousAlignmentData = request.session.get('previousAlignments', None)
        lang1AlignedWordList = []
        lang2AlignedWordList = []
        lang1AlignedWordData = {}
        lang2AlignedWordData = {}
        if previousAlignmentData:
            print 'WE HAVE ALIGNMENTS'
            lang1AlignedWordList += previousAlignmentData.keys()
            lang2AlignedWordList += [word for val in previousAlignmentData.values() for word in val]

        print 'DONE READING'
        data = {}
        result = {}
        posVocab = defaultdict(list)
        addedWords = defaultdict(list)
        previousAlignments = []

        for i, ((lang, word), coordinate) in enumerate(zip(words, coordinates)):
            data[i] = {'x': coordinate[0], 'y': coordinate[1], 'word': word, 'lang': lang}
            if word.lower() in finalVocabPOS:
                pos = finalVocabPOS[word.lower()]
                if word.lower() not in addedWords[pos]:
                    addedWords[pos].append(word.lower())
                    posVocab[pos].append({'x': coordinate[0], 'y': coordinate[1], 'word': word, 'lang': lang})

            if word.lower() in lang1AlignedWordList and lang == 'lang1':
                lang1AlignedWordData[word.lower()] = {'x': coordinate[0], 'y': coordinate[1], 'word': word, 'lang': lang}
            elif word.lower() in lang2AlignedWordList and lang == 'lang2':
                lang2AlignedWordData[word.lower()] = {'x': coordinate[0], 'y': coordinate[1], 'word': word, 'lang': lang}

        if previousAlignmentData:
            for key, value in previousAlignmentData.iteritems():
                keyData = lang1AlignedWordData[key]
                for word in value:
                    valueData = lang2AlignedWordData[word]
                    previousAlignments.append([keyData, valueData])

        result['data'] = data
        result['done'] = True
        result['posVocab'] = posVocab
        if previousAlignmentData:
            print previousAlignments
            result['previousAlignments'] = previousAlignments

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
            langConcordance = request.session['lang1Concordance']
        elif language == 'LANG2':
            langConcordance = request.session['lang2Concordance']

        concordance = getConcordance(word, langConcordance, language)

        result = {'concordance': concordance}
        jsonStr = json.dumps(result)
        return HttpResponse(jsonStr, content_type='application/javascript')


def getDataForDownload(request):
    print 'REQUESTING DATA FOR DOWNLOAD'
    dataForDownload = request.GET['downloadName']

    fileName = None
    if dataForDownload == 'COORDINATES':
        fileName = 'COORDINATE-DOWNLOAD.txt'
        coordinates = request.session.get('coordinates', None)
        if coordinates:
            writeCoordinates(request.session.session_key, fileName, coordinates)

    elif dataForDownload == 'WORDS':
        fileName = 'WORDS-DOWNLOAD.txt'
        words = request.session.get('words', None)
        if words:
            writeWords(request.session.session_key, fileName, words)

    filename = MEDIA_ROOT+'/'+request.session.session_key+'/'+fileName
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper)
    response['Content-Disposition'] = 'attachment; filename=%s' % fileName
    return response


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
                result.append((langName, lineSplit[1].decode('utf-8-sig').strip()))
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


def writeCoordinates(sessionKey, fileName, coordinates):
    print 'WRITING COORDINATES'
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    with open(folderName+fileName, 'w') as outFile:
        for coordinate in coordinates:
            outFile.write('{}\t{}\n'.format(coordinate[0], coordinate[1]))


def writeWords(sessionKey, fileName, words):
    print 'WRITING WORDS'
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    with open(folderName+fileName, 'w') as outFile:
        for (lang, word) in words:
            outFile.write('{}\t{}\n'.format(lang, word.encode('utf-8-sig')))


def loadLangConcordance(fileName, isPOSAvail, sessionKey, lines=25):
    print 'READING CONCONDANCE - ' + fileName
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    tokenLinesSet = defaultdict(set)
    vocabPOS = {}
    vocabCount = defaultdict(int)

    with open(folderName+fileName) as inFile:
        for index, line in enumerate(inFile):
            if index % 10000 == 0:
                print index

            line = line.strip('\r\n').strip()
            if line:
                lineSplit = line.split(' ')
                for token in lineSplit:
                    if isPOSAvail:
                        tokenPOSSplit = token.split('_', 1)
                        pos = None
                        if tokenPOSSplit[0] == '' and tokenPOSSplit[1].startswith('_'):
                            token = tokenPOSSplit[1][:-2]
                            pos = tokenPOSSplit[1][-2:]
                        elif not(tokenPOSSplit[0] == ''):
                            token = tokenPOSSplit[0]
                            pos = tokenPOSSplit[1]

                        if pos.startswith('NN'):
                            pos = 'NN'
                        elif pos.startswith('JJ'):
                            pos = 'JJ'
                        elif pos.startswith('RB'):
                            pos = 'RB'
                        elif pos.startswith('VB'):
                            pos = 'VB'
                        else:
                            pos = None
                        # elif pos == 'PRP$':
                        #     pos = 'PRP'
                        # elif pos == ',':
                        #     pos = 'COMMA'
                        # elif pos == ':':
                        #     pos = 'COLON'
                        # elif pos == '$':
                        #     pos = 'DOLLAR'
                        # elif pos == '.':
                        #     pos = 'DOT'
                        if pos:
                            vocabPOS[token.lower()] = pos
                            vocabCount[token.lower()] += 1

                    if len(tokenLinesSet[token.lower()]) <= lines:
                        tokenLinesSet[token.lower()].add(line)

    tokenLines = {}
    for token, lines in tokenLinesSet.iteritems():
        tokenLines[token] = list(lines)

    if isPOSAvail:
        return tokenLines, vocabPOS, vocabCount
    else:
        return tokenLines


def cleanLinesOfPOS(lines):
    result = []
    for line in lines:
        lineSplit = line.split()
        newLine = ''
        for tokenPOS in lineSplit:
            tokenPOSSplit = tokenPOS.split('_', 1)
            token = ''
            if tokenPOSSplit[0] == '' and tokenPOSSplit[1].startswith('_'):
                token = tokenPOSSplit[1][:-2]
            elif not(tokenPOSSplit[0] == ''):
                token = tokenPOSSplit[0]
            newLine += '{} '.format(token)
        result.append(newLine.strip())
    return result


def getConcordance(word, tokenLines, language):
    word = word.encode('utf-8').decode('utf-8')
    if word.lower() in tokenLines:
        lines = tokenLines[word.lower()]
        if language == 'LANG1':
            lines = cleanLinesOfPOS(lines)
        return lines
    else:
        return []


def filterVocabByCount(vocabCount, vocabPOS, numPerPOS):
    print 'FILTERING VOCAB BY COUNT'
    sortedVocabCount = sorted(vocabCount.items(), key=operator.itemgetter(1), reverse=True)
    countOfEachPOS = defaultdict(int)
    result = {}
    posCount = len(set(vocabPOS.values()))
    for token, count in sortedVocabCount:
        pos = vocabPOS[token]
        if countOfEachPOS[pos] < numPerPOS+1:
            result[token] = pos
            countOfEachPOS[pos] = countOfEachPOS[pos] + 1

        limitPOS = 0
        for posCount in countOfEachPOS.values():
            if posCount == numPerPOS:
                limitPOS += 1
        if limitPOS == posCount:
            break
    return result


def loadPreviousAlignments(fileName, sessionKey):
    print 'READING ALIGNMENT DATA'
    folderName = MEDIA_ROOT+'/'+sessionKey+'/'
    if not os.path.exists(folderName):
        return None

    result = defaultdict(list)
    with open(folderName+fileName) as inFile:
        for line in inFile:
            line = line.decode('utf-8-sig').strip('\r\n')
            if line:
                print line
                lineSplit = line.split('\t')
                result[lineSplit[0].strip()].append(lineSplit[1].strip())
    print result
    return result