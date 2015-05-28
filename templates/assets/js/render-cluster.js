function renderData(jsonData) {
    $( "#bilingual-embeddings" ).show( "slow");
    $("#cluster-render").width($(window).width()-100).height($(window).height());
    // configure for module loader

    require.config({
        paths: {
            echarts: "assets/js/"
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

            option = {
                tooltip : {
                    trigger: 'axis',
                    showDelay : 0,
                    axisPointer:{
                        show:true,
                        type : 'cross',
                        lineStyle: {
                            type : 'dashed',
                            width : 1
                        }
                    },
                    formatter : function (params) {
                        return params.value[2];
                    }
                },
                legend: {
                    data:['English','Chinese']
                },
                toolbox: {
                    show : true,
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
                                    table += '<tr>'
                                    + '<td>' + alignments[i].wordLang1.word + '</td>'
                                    + '<td>' + alignments[i].wordLang2.word + '</td>'
                                    + '</tr>';
                                }
                                table += '</tbody></table>';

                                return table;
                            },
                            lang: ['View Alignments', 'Close', 'Refresh']
                        },
                        restore : {show: true, title: 'Restore'},
                        saveAsImage : {show: true, title:'Save as Image'},
                        myTool : {
                            show : true,
                            title : 'Align',
                            icon : 'assets/img/link.png',
                            onclick : function (){
                                if (alignmentEnabled) {
                                    alignmentEnabled = false;
                                } else {
                                    alignmentEnabled = true;
                                }
                                alert(alignmentEnabled);
                            }
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
                        itemStyle: {
                            normal: {
                                label: {
                                    show: true,
                                    formatter : function (params) {
                                        return params.value[2];
                                    }
                                }
                            }
                        },
                        data: (function () {
                            var d = [];
                            for(var key in jsonData) {
                                if (key == "done") {
                                    continue;
                                }
                                if (jsonData[key].lang == "lang1") {
                                    d.push([jsonData[key].x, jsonData[key].y, jsonData[key].word]);
                                }
                            }
                            //console.log(d)
                            return d;
                        })()
                    }, 
                    
                    {
                        name:'Chinese',
                        type:'scatter',
                        large: true,
                        itemStyle: {
                            normal : {
                                label : {
                                    show: true,
                                    formatter : function (params) {
                                        return params.value[2];
                                    }
                                    //formatter : '{b}'
                                }
                            }
                        },
                        data: (function () {
                            var d = [];
                            for(var key in jsonData) {
                                if (key == "done") {
                                    continue;
                                }
                                if (jsonData[key].lang == "lang2") {
                                    d.push([jsonData[key].x, jsonData[key].y, jsonData[key].word]);
                                }
                            }
                            //console.log(d)
                            return d;
                        })()
                    }
                ]
            };

            // Load data into the ECharts instance
            myChart.setOption(option);

            var ecConfig = require('echarts/config');

            var alignments = [];
            var alignedWords = [];

            function createAlignment(param) {
                if (alignmentEnabled) {
                    var seriesIndex = param.seriesIndex;
                    var seriesName = param.seriesName;
                    var word = param.data[2];
                    var dataIndex = param.dataIndex;

                    if (alignedWords.indexOf(dataIndex) != -1) {
                        alert('Word: ' + word + ', is already aligned. Choose another word.')
                    } else {
                        var alignmentObj = alignments.pop();
                        if (null != alignmentObj) {
                            if(alignmentObj.isAligned()) {
                                alignments.push(alignmentObj);
                                alignmentObj = new Alignment();
                            }
                        } else {
                            alignmentObj = new Alignment();
                        }
                        var wordObj = new Word(word, seriesIndex, seriesName, dataIndex);
                        if (alignmentObj.canAddWord(wordObj)) {
                            alignmentObj.addWord(wordObj);
                            alignedWords.push(dataIndex);
                        } else {
                            var confirmation = confirm("Cannot add " + word + " to alignment as word of same language " +
                            "already selected. Would you like to replace previous selection");
                            if (confirmation) {
                                var replacedWord = alignmentObj.replaceWord(wordObj);
                                alignedWords.push(dataIndex);
                                var index = alignedWords.indexOf(replacedWord.dataIndex);
                                if (index >= 0) {
                                    alignedWords.splice(index, 1);
                                }
                            }
                        }

                        alignments.push(alignmentObj);
                    }
                }
            }

            myChart.on(ecConfig.EVENT.CLICK, createAlignment);
        }
    );

}

function Word(word, seriesIndex, seriesName, dataIndex) {
    this.word = word;
    this.seriesIndex = seriesIndex;
    this.seriesName = seriesName;
    this.dataIndex = dataIndex;
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
        } else {
            return true;
        }
        if (Word.seriesIndex == "1" && null != this.wordLang2) {
            return false;
        } else {
            return true
        }
    }
}
