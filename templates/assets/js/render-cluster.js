function renderData(jsonData) {
    $( "#bilingual-embeddings" ).show( "slow");
    $("#cluster-render").width($(window).width()-100).height($(window).height());
    // configure for module loader

    require.config({
        paths: {
            echarts: 'http://echarts.baidu.com/build/dist'
        }
    });

    // use
    require(
        [
            'echarts',
            'echarts/chart/scatter' // require the specific chart type
        ],
        function (ec) {
            // Initialize after dom ready
            var myChart = ec.init(document.getElementById('cluster-render'));

            option = {
                tooltip : {
                    trigger: 'axis',
                    showDelay : 0,
                    axisPointer:{
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
                        mark : {show: false,
                            title : {
                                mark : 'Mark',
                                markUndo : 'Undo Mark',
                                markClear : 'Clear Mark'
                            }},
                        dataZoom : {show: true,
                            title : {
                                dataZoom : 'Zoom In',
                                dataZoomReset : 'Reset Zoom'
                            }},
                        dataView : {show: false, readOnly: false, title : 'View Data'},
                        restore : {show: true, title: 'Restore'},
                        saveAsImage : {show: true, title:'Save as Image'}
                    }
                },
                xAxis : [
                    {
                        type : 'value',
                        scale:true
                    }
                ],
                yAxis : [
                    {
                        type : 'value',
                        scale:true
                    }
                ],
                series : [
                    {
                        name:'English',
                        type:'scatter',
                        large: true,
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
        }
    );

}
