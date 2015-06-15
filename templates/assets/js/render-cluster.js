function renderData(jsonData, tooltipURL) {
    $( "#bilingual-embeddings" ).show( "slow");
    $("#cluster-render").width($(window).width()*0.75).height($(window).height()-60);
    //$("#word-concordance").width($(window).width()*0.25);
    // configure for module loader

    require.config({
        paths: {
            echarts: "assets/js/",
            zrender: "assets/js/"
        }
    });

    // use
    require(
        [
            'echarts',
            'echarts/chart/scatter' // require the specific chart type
        ],
        function (ec) {
            //initialize variables
            var alignmentEnabled = false;

            // Initialize after dom ready
            var myChart = ec.init(document.getElementById('cluster-render'));

            var previousTooltipWord = null;

            option = {
                tooltip : {
                    trigger: 'item',
                    showDelay : 0,
                    axisPointer:{
                        show: false,
                        type : 'cross',
                        lineStyle: {
                            type : 'dashed',
                            width : 1
                        }
                    },
                    formatter : function (params) {
                        if(params.name.indexOf('Markline') === 0) {
                            return 'Alignment';
                        } else {
                            if (null == previousTooltipWord || params.name != previousTooltipWord) {
                                previousTooltipWord = params.name;
                                if(alignmentEnabled) {
                                    getWordTooltip(params.name, params.seriesIndex, tooltipURL);
                                }
                            }
                            return params.name;
                        }
                    }
                },
                legend: {
                    data:['English','Chinese']
                },
                toolbox: {
                    show : true,
                    x: 'right',
                    padding: [3,80,0,0],
                    feature : {
                        mark : {
                            show: false,
                            title : {
                                mark : 'Mark',
                                markUndo : 'Undo Mark',
                                markClear : 'Clear Mark'
                            },
                            lineStyle : {
                                width : 2,
                                color : '#1e90ff',
                                type : 'dashed'
                            }
                        },
                        dataZoom : {
                            show: true,
                            title : {
                                dataZoom : 'Zoom In',
                                dataZoomReset : 'Reset Zoom'
                            }
                        },
                        dataView : {
                            show: true,
                            readOnly: true,
                            title : 'View Alignments',
                            optionToContent: function(){
                                if (alignments.length == 0 || null == alignments[0].wordLang1 ||
                                    null == alignments[0].wordLang2) {
                                    return '';
                                }
                                var table = '<table style="width:100%;text-align:center"><tbody><tr>'
                                    + '<td><b>' + alignments[0].wordLang1.seriesName + '</b></td>'
                                    + '<td><b>' + alignments[0].wordLang2.seriesName + '</b></td>'
                                    + '</tr>';
                                for (var i = 0, l = alignments.length; i < l; i++) {
                                    if (null == alignments[i].wordLang1 || null == alignments[i].wordLang2) {
                                        continue;
                                    }
                                    table += '<tr>'
                                    + '<td>' + alignments[i].wordLang1.word + '</td>'
                                    + '<td>' + alignments[i].wordLang2.word + '</td>'
                                    + '</tr>';
                                }
                                table += '</tbody></table>';

                                return table;
                            },
                            lang: ['', 'Close', 'Refresh']
                        },
                        restore : {show: true, title: 'Restore'},
                        saveAsImage : {show: true, title:'Save as Image'},
                        align : {
                            show : true,
                            title : 'Align',
                            icon : 'assets/img/link.png',
                            onclick : function (){
                                if (alignmentEnabled) {
                                    alignmentEnabled = false;
                                    var alignmentObj = alignments.pop();
                                    if (alignmentObj.isAligned()) {
                                        alignments.push(alignmentObj);
                                    } else {
                                        var word = null;
                                        if (null != alignmentObj.wordLang1) {
                                            word = alignmentObj.wordLang1;
                                        } else if(null != alignmentObj.wordLang2) {
                                            word = alignmentObj.wordLang2;
                                        }
                                    }
                                } else {
                                    alignmentEnabled = true;
                                }
                                alert(alignmentEnabled);
                            }
                        },
                        download : {
                            show : true,
                            title : 'Download Alignments',
                            icon : 'assets/img/download.png',
                            onclick : downloadData
                        }
                    }
                },
                xAxis : [
                    {
                        type : 'value',
                        scale:true,
                        show: false
                    }
                ],
                yAxis : [
                    {
                        type : 'value',
                        scale:true,
                        show: false
                    }
                ],
                series : [
                    {
                        name:'English',
                        type:'scatter',
                        large: true,
                        z: 5,
                        itemStyle: {
                            normal: {
                                label: {
                                    show: true,
                                    formatter : function (params) {
                                        return params.name;
                                    }
                                }
                            }
                        },
                        data: (function () {
                            var d = [];
                            for(var key in jsonData.data) {
                                if (jsonData.data[key].lang == "lang1") {
                                    //d.push([jsonData.data[key].x, jsonData.data[key].y, jsonData.data[key].word]);
                                    d.push(
                                        {
                                            value: [jsonData.data[key].x, jsonData.data[key].y],
                                            name: jsonData.data[key].word
                                        }
                                    );
                                }
                            }
                            return d;
                        })(),
                        markLine : {
                            clickable: true,
                            symbol: ['none', 'none'],
                            itemStyle: {
                                normal: {
                                    color: '#088308',
                                    lineStyle: {
                                        type: 'dashed',
                                        width: 1
                                    }
                                }
                            },
                            data: []
                        }
                    },

                    {
                        name:'Chinese',
                        type:'scatter',
                        z: 5,
                        large: true,
                        itemStyle: {
                            normal : {
                                label : {
                                    show: true,
                                    formatter : function (params) {
                                        return params.name;
                                    }
                                    //formatter : '{b}'
                                }
                            }
                        },
                        data: (function () {
                            var d = [];
                            for(var key in jsonData.data) {
                                if (jsonData.data[key].lang == "lang2") {
                                    //d.push([jsonData.data[key].x, jsonData.data[key].y, jsonData.data[key].word]);
                                    d.push(
                                        {
                                            value: [jsonData.data[key].x, jsonData.data[key].y],
                                            name: jsonData.data[key].word
                                        }
                                    );
                                }
                            }
                            //console.log(d)
                            return d;
                        })()
                    },

                    /*{
                        name:'MarkpointSeries',
                        type:'scatter',
                        z: 2,
                        large: true,
                        data: [{value: [0,0]}]
                    }*/

                ]
            };

            // Load data into the ECharts instance
            myChart.setOption(option);

            var ecConfig = require('echarts/config');
            
            myChart.on(ecConfig.EVENT.CLICK, createAlignment);

            var alignments = [];

            function createAlignment(param) {
                if(param.name.indexOf('Markline') === 0 ) {
                    var deleteConfirm = confirm("Would you like to delete this alignment?");
                    if (deleteConfirm) {
                        deleteAlignment(param);
                    }
                } else if (alignmentEnabled) {
                    //getWordTooltip(param.data[2], param.seriesIndex, tooltipURL);

                    var seriesIndex = param.seriesIndex;
                    var seriesName = param.seriesName;
                    var word = param.name;
                    var xCoord = param.value[0];
                    var yCoord = param.value[1];

                    var alignmentObj = alignments.pop();
                    if (null != alignmentObj) {
                        if(alignmentObj.isAligned()) {
                            alignments.push(alignmentObj);
                            alignmentObj = new Alignment();
                        }
                    } else {
                        alignmentObj = new Alignment();
                    }
                    var wordObj = new Word(word, seriesIndex, seriesName, xCoord, yCoord);
                    if (alignmentObj.canAddWord(wordObj)) {
                        alignmentObj.addWord(wordObj);
                    } else {
                        var confirmation = confirm("Cannot add " + word + " to alignment as word of same language " +
                        "already selected. Would you like to replace previous selection");
                        if (confirmation) {
                            var replacedWord = alignmentObj.replaceWord(wordObj);
                        }
                    }

                    //If alignment object is aligned then create markLine
                    if (alignmentObj.isAligned()) {
                        var wordLang1 = alignmentObj.wordLang1;
                        var wordLang2 = alignmentObj.wordLang2;
                        var markLineData = {data: [[{xAxis: wordLang1.xCoord, yAxis: wordLang1.yCoord,
                            name:'Markline - '+ alignments.length.toString(), word1: wordLang1.word, alignmentIndex: alignments.length}, {xAxis: wordLang2.xCoord, yAxis: wordLang2.yCoord,
                        word2: wordLang2.word}]]};
                        myChart.addMarkLine(0, markLineData);
                        alignmentObj.alignmentIndex = alignments.length;
                    }
                    alignments.push(alignmentObj);
                    
                } else {
                    //getWordTooltip(param.data[2], param.seriesIndex, tooltipURL);
                }
            }

            function deleteAlignment(param) {
                console.log('Delete Alignment');

                //Find the alignment
                //remove the alignment
                var alignmentIndex = param.data.alignmentIndex;
                var index = findAlignment(alignmentIndex);
                var alignmentObj = alignments[index];

                console.log('Deleting - ');
                console.log(alignments[index]);
                alignments.splice(index, 1);

                //remove the markline
                myChart.delMarkLine(0, param.name);
            }

            function findAlignment(alignmentIndex) {
                var result;
                for(result = 0; result < alignments.length; result++) {
                    if(alignments[result].alignmentIndex == alignmentIndex){
                        return result;
                    }
                }
                return null;
            }

            function downloadData() {
                var table = '';
                if (alignments.length == 0 || null == alignments[0].wordLang1 ||
                    null == alignments[0].wordLang2) {
                    alert('No words have been currently aligned. No download available.');
                } else {
                    for (var i = 0, l = alignments.length; i < l; i++) {
                        if (null == alignments[i].wordLang1 || null == alignments[i].wordLang2) {
                            continue;
                        }
                        table += alignments[i].wordLang1.word + '\t' + alignments[i].wordLang2.word +'\n';
                    }

                    var blob = new Blob([table], {type: "text/plain;charset=utf-8"});
                    saveAs(blob, "Alignments.tsv");
                }

            }

            function createPreviousAlignment() {
                alignmentEnabled = true;
                for (var index in jsonData.previousAlignments) {
                    var alignmentArray = jsonData.previousAlignments[index];
                    for (var i in alignmentArray) {
                        var word = alignmentArray[i];
                        var paramObj = {};

                        paramObj.name = word.word;
                        if (word.lang == 'lang1') {
                            paramObj.seriesIndex = 0;
                            paramObj.seriesName = 'English';
                        } else if (word.lang == 'lang2') {
                            paramObj.seriesIndex = 1;
                            paramObj.seriesName = 'Chinese';
                        }
                        paramObj.value = [];
                        paramObj.value.push(word.x);
                        paramObj.value.push(word.y);

                        createAlignment(paramObj);
                    }

                }
                alignmentEnabled = false;
            }

            renderVocabPOSList(jsonData.posVocab, myChart);

            if('previousAlignments' in jsonData) {
                createPreviousAlignment();
            }
        }

    );

}

function Word(word, seriesIndex, seriesName, xCoord, yCoord) {
    this.word = word;
    this.seriesIndex = seriesIndex;
    this.seriesName = seriesName;
    this.xCoord = xCoord;
    this.yCoord = yCoord;
}

function Alignment(){
    this.addWord = function(Word) {
        if (Word.seriesIndex == "0" && null == this.wordLang1) {
            this.wordLang1 = Word;
        } else if (Word.seriesIndex == "1" && null == this.wordLang2) {
            this.wordLang2 = Word;
        }
    };

    this.replaceWord = function(Word) {
        if (Word.seriesIndex == "0") {
            var replacedWord = this.wordLang1;
            this.wordLang1 = Word;
        } else if (Word.seriesIndex == "1") {
            var replacedWord = this.wordLang2;
            this.wordLang2 = Word;
        }
        return replacedWord;
    };

    this.isAligned = function () {
        if (null != this.wordLang1 && null != this.wordLang2) {
            return true;
        } else {
            return false;
        }
    };

    this.canAddWord = function(Word) {
        if (Word.seriesIndex == "0" && null != this.wordLang1) {
            return false;
        } else if (Word.seriesIndex == "1" && null != this.wordLang2) {
            return false;
        } else {
            return true
        }
    }
}

function getWordTooltip(word, seriesIndex, tooltipURL) {
    //clear html
    $('#word-concordance').html('');

    //Create spinner
    loadSpinner("word-concordance", true);

    if (seriesIndex == "0") {
        seriesIndex = "LANG1"
    } else if(seriesIndex == "1") {
        seriesIndex = "LANG2"
    }
    var csrftoken = $.cookie('csrftoken');
    var text = {word: word, language: seriesIndex};
    //text = JSON.stringify(text);

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax ({
        type: "POST",
        url: tooltipURL,
        data: text,
        dataType: "json",
        traditional: true,
        cache: false, //VITAL line: the getJON func does not prevent caching!
        success: tooltipUpdater
    });
}

function tooltipUpdater(result) {
    result = result['concordance'];

    //stop spinner and show table
    loadSpinner("word-concordance", false);

    if(result.length == 0) {
        $('#word-concordance').html('');
        $('button[type="clear"]').prop('disabled', true);
    } else {
        var table = '<ol>';
        for (var i = 0; i < result.length; i++) {
            table += '<li>' + result[i] + '</li>';
        }
        table += '</ol>';
        $('#word-concordance').html(table);
        $('button[type="clear"]').removeAttr('disabled');
    }

    $('button[type="clear"]').click(function(){
        $('#word-concordance').html('');
        $('button[type="clear"]').prop('disabled', true);
    });
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var spinner;
var spinTargetDiv;
function loadSpinner(divName, start) {

    var opts = {
        lines: 11 // The number of lines to draw
        , length: 28 // The length of each line
        , width: 2 // The line thickness
        , radius: 10 // The radius of the inner circle
        , scale: 0.5 // Scales overall size of the spinner
        , corners: 1 // Corner roundness (0..1)
        , color: '#000' // #rgb or #rrggbb or array of colors
        , opacity: 0.25 // Opacity of the lines
        , rotate: 0 // The rotation offset
        , direction: 1 // 1: clockwise, -1: counterclockwise
        , speed: 1 // Rounds per second
        , trail: 60 // Afterglow percentage
        , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
        , zIndex: 2e9 // The z-index (defaults to 2000000000)
        , className: 'spinner' // The CSS class to assign to the spinner
        , top: '50%' // Top position relative to parent
        , left: '50%' // Left position relative to parent
        , shadow: false // Whether to render a shadow
        , hwaccel: false // Whether to use hardware acceleration
        , position: 'absolute' // Element positioning
    };
    if (start == true) {
        spinTargetDiv = document.getElementById(divName);
        spinner = new Spinner(opts).spin(spinTargetDiv);
    } else {
        spinner.stop();
    }

}

function renderVocabPOSList(data, myChart) {
    for(var key in data) {
        var divData = '<div class="panel panel-default">';
               divData += '<div class="panel-heading" role="tab" id="heading' + key + '">';
                   divData += '<h4 class="panel-title">';
                       divData += '<a data-toggle="collapse" data-parent="#accordion" href="#collapse' + key +
                                      '" aria-expanded="false" aria-controls="collapse'+key+'">';
                           divData += key;
                       divData += '</a>';
                   divData += '</h4>';
               divData += '</div>';
               divData += '<div id="collapse'+ key + '" class="panel-collapse collapse" role="tabpanel" ' +
               'aria-labelledby="heading' + key + '">';
                   divData += '<div class="panel-body">';
                       divData += '<ul class="list-unstyled">';
                           var words = data[key];
                           for (var i in words) {
                               divData += '<li id="'+key+'_vocabword_' + i + '" class="vocab-word" data-x="'+ words[i].x
                               +'" data-y="' + words[i].y + '" data-lang="'+ words[i].lang+'" data-word="'
                               + words[i].word + '">' + words[i].word + '</li>';
                           }
                       divData += '</ul>';
                   divData += '</div>';
               divData += '</div>';
           divData += '</div>';
        $("#pos-vocab").append(divData);

        $("#collapse"+key).on('click', '.vocab-word', function(d){
            vocabPOSListClickHandler(myChart, d);
        });
    }
}

var vocabIdPrevSelection = null;

function vocabPOSListClickHandler(chartObj, eventObj) {
    var targetId = eventObj.target.id;
    if (vocabIdPrevSelection == targetId) {
        removePrevVocabPOSSelection(targetId, chartObj);
        vocabIdPrevSelection = null;
    } else {
        if (null != vocabIdPrevSelection) {
            removePrevVocabPOSSelection(vocabIdPrevSelection, chartObj);
        }
        addNewVocabPOSSelection(targetId, chartObj);
        vocabIdPrevSelection = targetId;
    }
}

function addNewVocabPOSSelection(elementId, chartObj) {
    var elementObj = document.getElementById(elementId);
    elementObj.classList.add("vocab-word-select");

    var xCoord = parseFloat(elementObj.getAttribute('data-x'));
    var yCoord = parseFloat(elementObj.getAttribute('data-y'));
    var word = elementObj.getAttribute('data-word');
    var lang = elementObj.getAttribute('data-lang');

    var seriesIdx;
    if (lang == 'lang1') {
        seriesIdx = 0;
    } else if(lang == 'lang2') {
        seriesIdx = 1;
    }

    var markPointData = {data: [{name: word, xAxis: xCoord, yAxis: yCoord}],
        effect : {show: true, shadowBlur : 0, type: 'bounce',}, symbol:'emptycircle', symbolSize: 10, clickable: false};

    var dataPoint = [xCoord, yCoord];

    chartObj.addMarkPoint(seriesIdx, markPointData);
    dataPoint = {value: [xCoord, yCoord], name: word};

    //chartObj.addData(2, dataPoint, false, true);

    //chartObj.restore();
}

function removePrevVocabPOSSelection(elementId, chartObj) {
    var elementObj = document.getElementById(elementId);
    elementObj.classList.remove("vocab-word-select");

    var word = elementObj.getAttribute('data-word');
    var lang = elementObj.getAttribute('data-lang');

    var seriesIdx;
    if (lang == 'lang1') {
        seriesIdx = 0;
    } else if(lang == 'lang2') {
        seriesIdx = 1;
    }

    chartObj.delMarkPoint(seriesIdx, word);
    chartObj.refresh();

}