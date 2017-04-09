/*
* Trending line chart
*/
var data = {
    labels : ["JAN","FEB","MAR","APR","MAY","JUNE","JULY", "AUG", "SEPT", "OCT", "NOV", "DEC"],
    datasets : []
};

var nReloads = 0;
var min = 1;
var max = 10;
var l =0;
var trendingLineChart;
function update() {
    nReloads++;
}
setInterval(update, 3000);
/*
Polor Chart Widget
*/
var doughnutData = [];
/*
Trending Bar Chart
*/
var dataBarChart = {
    labels : ["JAN","FEB","MAR","APR","MAY", "JUNE","JULY", "AUG", "SEPT", "OCT", "NOV", "DEC"],
    datasets: []
};
var nReloads1 = 0;
var min1 = 1;
var max1 = 10;
var l1 =0;
var trendingBarChart;
function updateBarChart() {
    nReloads1++;
}
setInterval(updateBarChart, 3000);      
/*
Pie chart 
*/
var pieData = [];
if(Cookies.get('session') != undefined){
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", config.mode+"://"+config.host+":"+config.port+"/cloud/v0.1/private/user/dashboard");
    xmlhttp.onreadystatechange=function()
    {
        if(this.readyState == 4){
            if (this.status == 200) {
                var response = JSON.parse(this.responseText);
                var projects_total = response["projects_total"];
                var records_total = response["records_total"];
                var environments_total = response["environments_total"];
                var projects = response["projects"];

                if(document.getElementById("trending-line-chart-wrapper"))
                    document.getElementById("trending-line-chart-wrapper").innerHTML = "<canvas id='trending-line-chart' height='70'></canvas>";

                if(document.getElementById("doughnut-chart-wrapper"))
                    document.getElementById("doughnut-chart-wrapper").innerHTML = "<canvas id='doughnut-chart' height='200'></canvas><div class='doughnut-chart-status' id='doughnut-chart-status'>"+records_total+"<p class='ultra-small center-align'>Records</p></div>";

                if(document.getElementById("trending-bar-chart-wrapper"))
                    document.getElementById("trending-bar-chart-wrapper").innerHTML = "<canvas id='trending-bar-chart' height='90'></canvas>";
                data["datasets"] = [];
                dataBarChart["datasets"] = [];
                doughnutData = [];
                color = "#000000";
                if(response["projects"].length > 0){
                    for(var i = 0; i < response["projects"].length; i++){
                        var project = response["projects"][i];
                        var project_color = (function(m,s,c){return (c ? arguments.callee(m,s,c-1) : '#') + s[m.floor(m.random() * s.length)]})(Math,'0123456789ABCDEF',5);
                        var highlight_color = (function(m,s,c){return (c ? arguments.callee(m,s,c-1) : '#') + s[m.floor(m.random() * s.length)]})(Math,'0123456789ABCDEF',5);
                        var dataset = {
                            label: project["name"],
                            fillColor : "rgba(128, 222, 234, 0.6)",
                            strokeColor : project_color,
                            pointColor : project_color,
                            pointStrokeColor : "#ffffff",
                            pointHighlightFill : "#ffffff",
                            pointHighlightStroke : "#ffffff",
                            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        };

                        var dataBarset = {
                            label: project["name"],
                            fillColor: project_color,
                            strokeColor: project_color,
                            highlightFill: "rgba(70, 191, 189, 0.4)",
                            highlightStroke: "rgba(70, 191, 189, 0.9)",
                            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        };

                        dataset["data"][0] = project["records"]["January"]["number"];
                        dataset["data"][1] = project["records"]["February"]["number"];
                        dataset["data"][2] = project["records"]["March"]["number"];
                        dataset["data"][3] = project["records"]["April"]["number"];
                        dataset["data"][4] = project["records"]["May"]["number"];
                        dataset["data"][5] = project["records"]["June"]["number"];
                        dataset["data"][6] = project["records"]["July"]["number"];
                        dataset["data"][7] = project["records"]["August"]["number"];
                        dataset["data"][8] = project["records"]["September"]["number"];
                        dataset["data"][9] = project["records"]["October"]["number"];
                        dataset["data"][10] = project["records"]["November"]["number"];
                        dataset["data"][11] = project["records"]["December"]["number"];
                        dataBarset["data"][0] = project["records"]["January"]["number"];
                        dataBarset["data"][1] = project["records"]["February"]["number"];
                        dataBarset["data"][2] = project["records"]["March"]["number"];
                        dataBarset["data"][3] = project["records"]["April"]["number"];
                        dataBarset["data"][4] = project["records"]["May"]["number"];
                        dataBarset["data"][5] = project["records"]["June"]["number"];
                        dataBarset["data"][6] = project["records"]["July"]["number"];
                        dataBarset["data"][7] = project["records"]["August"]["number"];
                        dataBarset["data"][8] = project["records"]["September"]["number"];
                        dataBarset["data"][9] = project["records"]["October"]["number"];
                        dataBarset["data"][10] = project["records"]["November"]["number"];
                        dataBarset["data"][11] = project["records"]["December"]["number"];
                        doughnutset = {
                            value: 0,
                            color:project_color,
                            highlight: highlight_color,
                            label: project["name"]
                        };
                        doughnutset["value"] = project["records"]["January"]["number"]+project["records"]["February"]["number"]+project["records"]["March"]["number"]+project["records"]["April"]["number"]+project["records"]["May"]["number"]+project["records"]["June"]["number"]+project["records"]["July"]["number"]+project["records"]["August"]["number"]+project["records"]["September"]["number"]+project["records"]["October"]["number"]+project["records"]["November"]["number"]+project["records"]["December"]["number"];
                        doughnutData.push(doughnutset);
                        data["datasets"].push(dataset);
                        dataBarChart["datasets"].push(dataset);
                    }
                }else{
                    var project_color = "grey";
                    var highlight_color = (function(m,s,c){return (c ? arguments.callee(m,s,c-1) : '#') + s[m.floor(m.random() * s.length)]})(Math,'0123456789ABCDEF',5);
                    var dataset = {
                        label: "no project",
                        fillColor : "rgba(128, 222, 234, 0.6)",
                        strokeColor : project_color,
                        pointColor : project_color,
                        pointStrokeColor : "#ffffff",
                        pointHighlightFill : "#ffffff",
                        pointHighlightStroke : "#ffffff",
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    };

                    var dataBarset = {
                        label: "no project",
                        fillColor: project_color,
                        strokeColor: project_color,
                        highlightFill: "rgba(70, 191, 189, 0.4)",
                        highlightStroke: "rgba(70, 191, 189, 0.9)",
                        data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    };

                    dataset["data"][0] = 0;
                    dataset["data"][1] = 0;
                    dataset["data"][2] = 0;
                    dataset["data"][3] = 0;
                    dataset["data"][4] = 0;
                    dataset["data"][5] = 0;
                    dataset["data"][6] = 0;
                    dataset["data"][7] = 0;
                    dataset["data"][8] = 0;
                    dataset["data"][9] = 0;
                    dataset["data"][10] = 0;
                    dataset["data"][11] = 0;
                    dataBarset["data"][0] = 0;
                    dataBarset["data"][1] = 0;
                    dataBarset["data"][2] = 0;
                    dataBarset["data"][3] = 0;
                    dataBarset["data"][4] = 0;
                    dataBarset["data"][5] = 0;
                    dataBarset["data"][6] = 0;
                    dataBarset["data"][7] = 0;
                    dataBarset["data"][8] = 0;
                    dataBarset["data"][9] = 0;
                    dataBarset["data"][10] = 0;
                    dataBarset["data"][11] = 0;
                    doughnutset = {
                        value: 0,
                        color:project_color,
                        highlight: highlight_color,
                        label: "no records"
                    };
                    doughnutset["value"] = 1;
                    doughnutData.push(doughnutset);
                    data["datasets"].push(dataset);
                    dataBarChart["datasets"].push(dataset);
                }
                try{
                    var trendingLineChartBlock = document.getElementById("trending-line-chart");
                    if(trendingLineChartBlock != null){
                        var trendingLineChart = trendingLineChartBlock.getContext("2d");
                        window.trendingLineChart = new Chart(trendingLineChart).Line(data, {        
                        scaleShowGridLines : true,///Boolean - Whether grid lines are shown across the chart        
                        scaleGridLineColor : "rgba(255,255,255,0.4)",//String - Colour of the grid lines        
                        scaleGridLineWidth : 1,//Number - Width of the grid lines        
                        scaleShowHorizontalLines: true,//Boolean - Whether to show horizontal lines (except X axis)        
                        scaleShowVerticalLines: false,//Boolean - Whether to show vertical lines (except Y axis)        
                        bezierCurve : true,//Boolean - Whether the line is curved between points        
                        bezierCurveTension : 0.4,//Number - Tension of the bezier curve between points        
                        pointDot : true,//Boolean - Whether to show a dot for each point        
                        pointDotRadius : 5,//Number - Radius of each point dot in pixels        
                        pointDotStrokeWidth : 2,//Number - Pixel width of point dot stroke        
                        pointHitDetectionRadius : 20,//Number - amount extra to add to the radius to cater for hit detection outside the drawn point        
                        datasetStroke : true,//Boolean - Whether to show a stroke for datasets        
                        datasetStrokeWidth : 3,//Number - Pixel width of dataset stroke        
                        datasetFill : true,//Boolean - Whether to fill the dataset with a colour                
                        animationSteps: 15,// Number - Number of animation steps        
                        animationEasing: "easeOutQuart",// String - Animation easing effect            
                        tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                        scaleFontSize: 12,// Number - Scale label font size in pixels        
                        scaleFontStyle: "normal",// String - Scale label font weight style        
                        scaleFontColor: "#fff",// String - Scale label font colour
                        tooltipEvents: ["mousemove", "touchstart", "touchmove"],// Array - Array of string names to attach tooltip events        
                        tooltipFillColor: "rgba(255,255,255,0.8)",// String - Tooltip background colour        
                        tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                        tooltipFontSize: 12,// Number - Tooltip label font size in pixels
                        tooltipFontColor: "#000",// String - Tooltip label font colour        
                        tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                        tooltipTitleFontSize: 14,// Number - Tooltip title font size in pixels        
                        tooltipTitleFontStyle: "bold",// String - Tooltip title font weight style        
                        tooltipTitleFontColor: "#000",// String - Tooltip title font colour        
                        tooltipYPadding: 8,// Number - pixel width of padding around tooltip text        
                        tooltipXPadding: 16,// Number - pixel width of padding around tooltip text        
                        tooltipCaretSize: 10,// Number - Size of the caret on the tooltip        
                        tooltipCornerRadius: 6,// Number - Pixel radius of the tooltip border        
                        tooltipXOffset: 10,// Number - Pixel offset from point x to tooltip edge
                        responsive: true
                        });
                    }
                    var doughnutChartBlock = document.getElementById("doughnut-chart");
                    if(doughnutChartBlock != null){
                        var doughnutChart = doughnutChartBlock.getContext("2d");
                        window.myDoughnut = new Chart(doughnutChart).Doughnut(doughnutData, {
                            segmentStrokeColor : "#fff",
                            tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                            percentageInnerCutout : 50,
                            animationSteps : 15,
                            segmentStrokeWidth : 4,
                            animateScale: true,
                            percentageInnerCutout : 60,
                            responsive : true
                        });
                    }
                    var trendingBarChartBlock = document.getElementById("trending-bar-chart");
                    if(trendingBarChartBlock != null){
                        var trendingBarChart = trendingBarChartBlock.getContext("2d");
                        window.trendingBarChart = new Chart(trendingBarChart).Bar(dataBarChart,{
                            scaleShowGridLines : false,///Boolean - Whether grid lines are shown across the chart
                            showScale: true,
                            animationSteps:15,
                            tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                            responsive : true
                        });
                    }
                }
                catch(err) {
                    console.log(err.message);
                }
            }else{
                config.error_modal('An error occured.', this.responseText);
            }
        }
    }
    xmlhttp.setRequestHeader("Authorization", "Basic " + btoa("user-session:" + Cookies.get('session')));
    xmlhttp.send();
}else{
    window.onload = function(){
        var trendingLineChartBlock = document.getElementById("trending-line-chart");
        if(trendingLineChartBlock != null){
            var trendingLineChart = trendingLineChartBlock.getContext("2d");
            window.trendingLineChart = new Chart(trendingLineChart).Line(data, {        
                scaleShowGridLines : true,///Boolean - Whether grid lines are shown across the chart        
                scaleGridLineColor : "rgba(255,255,255,0.4)",//String - Colour of the grid lines        
                scaleGridLineWidth : 1,//Number - Width of the grid lines        
                scaleShowHorizontalLines: true,//Boolean - Whether to show horizontal lines (except X axis)        
                scaleShowVerticalLines: false,//Boolean - Whether to show vertical lines (except Y axis)        
                bezierCurve : true,//Boolean - Whether the line is curved between points        
                bezierCurveTension : 0.4,//Number - Tension of the bezier curve between points        
                pointDot : true,//Boolean - Whether to show a dot for each point        
                pointDotRadius : 5,//Number - Radius of each point dot in pixels        
                pointDotStrokeWidth : 2,//Number - Pixel width of point dot stroke        
                pointHitDetectionRadius : 20,//Number - amount extra to add to the radius to cater for hit detection outside the drawn point        
                datasetStroke : true,//Boolean - Whether to show a stroke for datasets        
                datasetStrokeWidth : 3,//Number - Pixel width of dataset stroke        
                datasetFill : true,//Boolean - Whether to fill the dataset with a colour                
                animationSteps: 15,// Number - Number of animation steps        
                animationEasing: "easeOutQuart",// String - Animation easing effect            
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                scaleFontSize: 12,// Number - Scale label font size in pixels        
                scaleFontStyle: "normal",// String - Scale label font weight style        
                scaleFontColor: "#fff",// String - Scale label font colour
                tooltipEvents: ["mousemove", "touchstart", "touchmove"],// Array - Array of string names to attach tooltip events        
                tooltipFillColor: "rgba(255,255,255,0.8)",// String - Tooltip background colour        
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                tooltipFontSize: 12,// Number - Tooltip label font size in pixels
                tooltipFontColor: "#000",// String - Tooltip label font colour        
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                tooltipTitleFontSize: 14,// Number - Tooltip title font size in pixels        
                tooltipTitleFontStyle: "bold",// String - Tooltip title font weight style        
                tooltipTitleFontColor: "#000",// String - Tooltip title font colour        
                tooltipYPadding: 8,// Number - pixel width of padding around tooltip text        
                tooltipXPadding: 16,// Number - pixel width of padding around tooltip text        
                tooltipCaretSize: 10,// Number - Size of the caret on the tooltip        
                tooltipCornerRadius: 6,// Number - Pixel radius of the tooltip border        
                tooltipXOffset: 10,// Number - Pixel offset from point x to tooltip edge
                responsive: true
            });
        }
        var doughnutChartBlock = document.getElementById("doughnut-chart");
        if(doughnutChartBlock != null){
            var doughnutChart = doughnutChartBlock.getContext("2d");
            window.myDoughnut = new Chart(doughnutChart).Doughnut(doughnutData, {
                segmentStrokeColor : "#fff",
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                percentageInnerCutout : 50,
                animationSteps : 15,
                segmentStrokeWidth : 4,
                animateScale: true,
                percentageInnerCutout : 60,
                responsive : true
            });
        }
        var trendingBarChartBlock = document.getElementById("trending-bar-chart");
        if(trendingBarChartBlock != null){
            var trendingBarChart = trendingBarChartBlock.getContext("2d");
            window.trendingBarChart = new Chart(trendingBarChart).Bar(dataBarChart,{
                scaleShowGridLines : false,///Boolean - Whether grid lines are shown across the chart
                showScale: true,
                animationSteps:15,
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                responsive : true
            });
        }
    };
}
