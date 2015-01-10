function renderData(jsonData) {
    $( "#bilingual-embeddings" ).show( "slow");
    console.log(jsonData);

    var width = $(window).width();
    var height = $(window).height();

    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    var tooltipRendered = false;

    var data = [];
    for(var key in jsonData) {
        if (key == "done") {
            continue;
        }
        data.push([jsonData[key].x, jsonData[key].y, key, jsonData[key].word, jsonData[key].lang]);
    }

    console.log(data.length);

    var xMin = d3.min(data, function(d) {return d[0]});
    var xMax = d3.max(data, function(d) {return d[0]});
    var yMin = d3.min(data, function(d) {return d[1]});
    var yMax = d3.max(data, function(d) {return d[1]});

    var x = d3.scale.linear()
        .domain([xMin, xMax])
        .range([0, width]);

    var y = d3.scale.linear()
        .domain([yMin, yMax])
        .range([0, height]);


    var svg = d3.select("#cluster-render").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .call(d3.behavior.zoom().x(x).y(y).scaleExtent([Number.MIN_VALUE, Number.MAX_VALUE]).on("zoom", zoom));

    var circle = svg.selectAll("circle")
        .data(data)
        .enter().append("circle")
        .attr("r", 3)
        .attr("transform", transform)
        .attr("fill",getColor)
        .on("click", renderTooltip)
        .on("click", renderTooltip);

    function zoom() {
        circle.attr("transform", transform);
    }

    function getColor(d) {
        var lang = d[4];
        if (lang == "lang1") {
            return "hsl(0, 100%, 50%)";
        } else if (lang == "lang2") {
            return "hsl(120, 100%, 25%)";
        }
    }

    function transform(d) {
        return "translate(" + x(d[0]) + "," + y(d[1]) + ")";
    }

    function renderTooltip(d) {
        if (tooltipRendered == false) {
            tooltipRendered = true;
            tooltip.transition().duration(200).style("opacity", 1);
            tooltip.html(d[3])
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        } else {
            tooltipRendered = false;
            tooltip.transition().duration(500).style("opacity", 0)
        }
    }
}
