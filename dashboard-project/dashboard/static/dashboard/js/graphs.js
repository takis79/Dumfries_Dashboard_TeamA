/*jshint*/

/*global d3, console, GLOBAL */
function setActiveStyleSheet(title) {
    var i, a, main;
    for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
        if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
            a.disabled = true;
            if(a.getAttribute("title") == title) a.disabled = false;

        }

    }
}
function reload(){
}
function getActiveStyleSheet() {
    var i, a;
    for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
        if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title") && !a.disabled) return a.getAttribute("title");
    }
    return null;
}

function getPreferredStyleSheet() {
    var i, a;
    for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
        if(a.getAttribute("rel").indexOf("style") != -1 &&
            a.getAttribute("rel").indexOf("alt") == -1 &&
            a.getAttribute("title")
            ) return a.getAttribute("title");
    }
    return null;
}

function createCookie(name,value,days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        expires = "; expires="+date.toGMTString();
    }
    else expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

window.onload = function(e) {
    var cookie = readCookie("style");
    var title = cookie ? cookie : getPreferredStyleSheet();
    setActiveStyleSheet(title);
};

window.onunload = function(e) {
    var title = getActiveStyleSheet();
    createCookie("style", title, 365);
};

var cookie = readCookie("style");
var title = cookie ? cookie : getPreferredStyleSheet();
setActiveStyleSheet(title);

console.log(getActiveStyleSheet());

//console.log(getPreferredStyleSheet());

function drawGraph(elemID, data, type,datasetLabels,xLabel,yLabel) {
    if ($("#" + elemID).parent().width() < 0) return;
    switch(type) {
        case "bar":
            bargraph(elemID, data,xLabel,yLabel);
            break;
        case "line":
            linegraph(elemID, data,datasetLabels,xLabel,yLabel);
            break;
    }
}

function bargraph(elemID, data,xLabel,yLabel) {
    var HEIGHT=0;
    var tool_bar_height=100;
    if ($("#" + elemID).parent().parent().parent().height()-tool_bar_height>1000){
        HEIGHT = 500;
    }else{
        HEIGHT = $("#" + elemID).parent().parent().parent().height()-tool_bar_height;
    }
    data = data[0];
    $("#" + elemID).empty();
    var width = $("#" + elemID).parent().width(),
        barHeight =  HEIGHT/data.length;

    var x = d3.scale.linear()
        .domain([0, d3.max(data, function(d) {return d.y;})])
        .range([0, width - 5]);

    var chart = d3.select("#" + elemID)
        .attr("width", width)
        .attr("height", HEIGHT);

    var bar = chart.selectAll("g")
        .data(data)
        .enter().append("g")
        .attr("transform", function (d, i) {
            return "translate(0," + i * barHeight + ")";
        });

    bar.append("rect")
        .attr("width", function(d) {
            return x(d.y);
        })
        .attr("height", barHeight - 1)
        .on("mouseover", function() {                   //on mouseover the bar is highlighted with light blue
            d3.select(this).classed("highlight", true);
        })
        .on("mouseout", function() {
            d3.select(this).classed("highlight", false);
        });


    bar.append("text")
        .attr("fill","white")
        .attr("x", function (d) {
            return x(d.y) - 3;
        })
        .attr("y", barHeight / 2)
        .attr("dy", ".35em")
        .text(function (d) {
            return (d.x+" "+d.y);
        });
}
function add_Trend_Element(elemID){
    var vis = d3.select("#" + elemID);
    vis.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ ($("#" + elemID).width()-100) +","+(($("#" + elemID).height()-250))+")")  // centre below axis
        .text("Highest Value was : 500")
        .append('svg:tspan')
        .attr('x', -40)
        .attr('dy', 15)
        .text("Now is : 300")
        .append('svg:tspan')
        .attr('x', -40)
        .attr('dy', 15)
        .text("Lowest was : 100");
}
function cleanup_data(data, type, clean_data){
    var end_date = GLOBAL.endDateRange;
    var start_date = GLOBAL.startDateRange;
    var i,d, c_date, input;

    if (!end_date || !start_date) {
        start_date = new Date();
        start_date.setYear(1900);
        end_date.setYear(2100);
        end_date.setYear(2100);
    }
    //Check date type
    if (type=="normal"){ //Yearly
        for (i=0; i<data.length; i++) {
            for (d=0;d<data[i].length; d++) {
                c_date=new Date();
                c_date.setYear(data[i][d].x);
                if(c_date<=end_date && c_date>=start_date) {
                    input={};
                    input.x=c_date;
                    input.y=data[i][d].y;
                    clean_data[i].push(input);
                }
            }
        }
    } else {//Date object
        for (i=0; i<data.length; i++) {
            for (d=0;d<data[i].length; d++) {
                c_date=new Date(data[i][d].x);
                if(c_date<=end_date && c_date>=start_date) {
                    input={};
                    input.x=c_date;
                    input.y=data[i][d].y;
                    clean_data[i].push(input);
                }
            }
        }
    }

    return clean_data;
}
function add_legend(elemID,vis,data,colours,datasetLabels,MARGINS){
    var y=0;
    var data_width=40;
    var rect_height=12;
    //for every data add coressponidng
    for (var i=0; i < data.length;i++) {
        if (data[i] === null) {
            continue;
        }
        vis.append("rect")
            .attr("width",30)
            .attr("height",rect_height)
            .attr("x",MARGINS.left)
            .attr("y",y)
            .attr("dy","-3.5em")
            .attr('fill',colours[i]);
        vis.append("text")
            .attr("font-size","0.75vw")
            .attr("x",MARGINS.left+data_width)
            .attr("y",y+rect_height)
            .text(datasetLabels[i]);
        y+=17;
    }
}
function linegraph(elemID, data,datasetLabels,xLabel,yLabel) {
    var vis;
    var c_data=data;//Copy of our data given in
    var type="normal";
    var clean_data=[];

    $("#" + elemID).empty();// Clean previous graph in widget

    for (var i=0;i<data.length;i++) {//Initialize the number of lines
        clean_data[i] = [];
    }

    if (!data[0][0]) return;

    if (typeof(data[0][0].x)=="string") type="date_format"; //Temporary solution for the different date formats

    clean_data=cleanup_data(c_data,type,clean_data);// Sends a copy of our data to be filtered and converts dates to JS Date format

    if (clean_data[0].length === 0 ) {
        vis = d3.select("#" + elemID).attr('width', $("#" + elemID).parent().width()).attr('height', 270);
        vis.append("text")
            .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
            .attr('x',$("#" + elemID).width()/2)
            .attr('y',$("#" + elemID).height()/2)
            .text("No information available for these dates");
        return;
    }

    var xMin = clean_data[0][0].x, xMax = clean_data[0][0].x, yMin = clean_data[0][0].y, yMax = clean_data[0][0].y;
    var xMinCurr, xMaxCurr, yMinCurr, yMaxCurr;
    var x=0;

    //Date comparison to find min and max values
    for (x=0;x<clean_data.length;x++){
        for (i=0; i<clean_data[x].length; i++) {

            xMinCurr = clean_data[x][i].x;
            xMaxCurr = clean_data[x][i].x;
            yMinCurr = clean_data[x][i].y;
            yMaxCurr = clean_data[x][i].y;

            if (xMinCurr < xMin) xMin = xMinCurr;
            if (xMaxCurr > xMax) xMax = xMaxCurr;
            if (yMinCurr < yMin) yMin = yMinCurr;
            if (yMaxCurr > yMax) yMax = yMaxCurr;
        }
    }
    //Get the year value
    xMin=xMin.getFullYear();
    xMax=xMax.getFullYear();


    var HEIGHT=0;
    var WIDTH, colours, MARGINS;
    var tool_bar_height=100;
    if ($("#" + elemID).parent().parent().parent().height()-tool_bar_height>1000){
        HEIGHT = 300;
    }else{
        HEIGHT = $("#" + elemID).parent().parent().parent().height()-tool_bar_height;
    }
    if(getActiveStyleSheet() === "default") {
        WIDTH = $("#" + elemID).parent().parent().width();
        colours = ['#00264d', ' #0064cc' , '#0066cc', ' #3399ff', ' #fff'];
        MARGINS = {
            top: 30,
            right: 25,
            bottom: data.length*10+10,
            left: 60
        };

    }else {
        WIDTH = $("#" + elemID).parent().parent().width();
        colours = ['#1a001a', ' #4d004d' , '#800080', ' #b300b3', ' #fff'];
        MARGINS = {
            top: 30,
            right: 25,
            bottom: data.length * 10 + 10,
            left: 60
        };

    }
    //Create svg element
    vis = d3.select("#" + elemID).attr("width", WIDTH).attr("height", HEIGHT);

    var xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([xMin, xMax]);
    var yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([yMin, yMax]);
    
    //console.log(xMin);
    //console.log(xMax);

    if (clean_data[0].length==1) {// In case of 1 element margin domain changes
        xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([xMin-1, xMax+1]);
        yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([yMax/2, yMax*2]);
    }else if(type !== "normal"){
        xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([xMin, xMax+1]);
    }

    //Specify x axis
    var xAxis = d3.svg.axis()
        .scale(xScale)
        .tickFormat(d3.format("date"))
        .orient("bottom")
        .ticks((WIDTH-90)/30);

    //Specify y axis
    var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");

    //Add y axis
    vis.append("svg:g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + MARGINS.left + ",0)")
        .call(yAxis);

    //Add x axis
    vis.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (HEIGHT - MARGINS.top) + ")")
        .call(xAxis);

    //Line generator
    var lineGen = d3.svg.line()
        .x(function(d) {
            return xScale(d.x.getFullYear()+(d.x.getMonth())/12);
        })
        .y(function(d) {
            return yScale(d.y);
        });
    
    var div = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    var bisectDate = d3.bisector(function(d) { console.log(d.y);return d.y; }).left;

    //In case of 1 element we append a circle with just a text
    if (clean_data[0].length==1){
        vis.append('circle')
            .attr("cx", WIDTH/2)
            .attr("cy", HEIGHT/2+40)
            .attr("r", 10);
        vis.append('text')
            .attr("transform", "translate("+ (WIDTH/2-40) +","+((HEIGHT/2-40))+")")  // centre below axis
            .text(clean_data[0][0].y+" for "+clean_data[0][0].x.getFullYear());
        return;
    }


    //generate the line graph by calling lineGen
    for (i=0; i<clean_data.length; i++) {
        vis.append('svg:path')
            .attr('d', lineGen(clean_data[i]))
            .attr('stroke', colours[i])
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .on("mousemove", function(d) {
                div.transition()
                    .duration(10)
                    .style("opacity", 1)
                    .delay(1000)
                    .style("opacity",0);
            })
            .on("mouseover", mousemove);

    }

    //finds and display the current coordinates mouse is on
    function mousemove() {
        var a=0;
        var y1 = 0;
        for (a = 0; a < clean_data.length; a++) {
            var x0 = xScale.invert(d3.mouse(this)[0]).toFixed(0);


            var y = yScale.invert(d3.mouse(this)[1]);
            y = y.toString();
            var res = y.substring(0, 2);
if(res == '0.'){
                var y1 = yScale.invert(d3.mouse(this)[1]).toFixed(2);
console.log(y1);
}else{
                var y1 = yScale.invert(d3.mouse(this)[1]).toFixed(0);

}
    div.transition()
                .duration(10)
                .style("opacity",0.9);
            div.html(yLabel+"<b/>" +": " + y1+  "<br/>"  + xLabel +": " +x0)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");

        }
    }

    //Check that labels for the dataset exist and then add them
    if(typeof datasetLabels !== undefined || datasetLabels !== null){
        add_legend(elemID,vis,clean_data,colours,datasetLabels,MARGINS);
    }
    add_axis_labels(vis,xLabel,yLabel,WIDTH,HEIGHT,MARGINS);

}

//Add the axis labels to the linegraphs
function add_axis_labels(vis,xLabel,yLabel,WIDTH,HEIGHT,MARGINS){

    vis.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ 12 +","+((HEIGHT)/2)+")rotate("+270+")")  // centre below axis
        .text(yLabel);

    vis.append("text")
        .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
        .attr("transform", "translate("+ (WIDTH/2) +","+((HEIGHT))+")")  // centre below axis
        .text(xLabel);
}

reload();
