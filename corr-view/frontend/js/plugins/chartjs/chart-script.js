/*
* Trending line chart
*/
//var randomScalingFactor = function(){ return Math.round(Math.random()*10)};
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
    // Per year upgrade.
    nReloads++;
    // var x = Math.floor(Math.random() * (max - min + 1)) + min;
    // var y = Math.floor(Math.random() * (max - min + 1)) + min;
    // trendingLineChart.addData([x, y], data.labels[l]);
    // trendingLineChart.removeData();
    // l++;
    // if( l == data.labels.length)
    //     { l = 0;}
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
 // Data per year
      nReloads1++;     
    // var x = Math.floor(Math.random() * (max1 - min1 + 1)) + min1;
    // console.log(x);
    // trendingLineChart.addData([x], dataBarChart.labels[l1]);
    // trendingBarChart.removeData();
    // l1++;
    // if( l1 == dataBarChart.labels.length){ l1 = 0;} 
}
setInterval(updateBarChart, 3000);

/*
Trending Bar Chart
*/
// var radarChartData = {
//     labels: [],
//     datasets: [],
// };
    
    
// var nReloads2 = 0;
// var min2 = 1;
// var max2 = 10;
// var l2 =0;
// var trendingRadarChart;
// function trendingRadarChartupdate() {    
//       nReloads2++;     

//     var x = Math.floor(Math.random() * (max2 - min2 + 1)) + min2;    
    
//     trendingRadarChart.addData([x], radarChartData.labels[l2]);
//     var y = trendingRadarChart.removeData();
//     l2++;
//     if( l2 == radarChartData.labels.length){ l2 = 0;}
 
// }

// setInterval(trendingRadarChartupdate, 3000);    
        
/*
Pie chart 
*/
var pieData = [];
/*
Line Chart
*/
// var lineChartData = {
//     labels : ["USA","UK","UAE","AUS","IN","SA"],
//     datasets : [
//         {
//             label: "My dataset",
//             fillColor : "rgba(255,255,255,0)",
//             strokeColor : "#fff",
//             pointColor : "#00796b ",
//             pointStrokeColor : "#fff",
//             pointHighlightFill : "#fff",
//             pointHighlightStroke : "rgba(220,220,220,1)",
//             data: [65, 45, 50, 30, 63, 45]
//         }
//     ]

// }

// var polarData = [
//         {
//             value: 4800,
//             color:"#f44336",
//             highlight: "#FF5A5E",
//             label: "USA"
//         },
//         {
//             value: 6000,
//             color: "#9c27b0",
//             highlight: "#ce93d8",
//             label: "UK"
//         },
//         {
//             value: 1800,
//             color: "#3f51b5",
//             highlight: "#7986cb",
//             label: "Canada"
//         },
//         {
//             value: 4000,
//             color: "#2196f3 ",
//             highlight: "#90caf9",
//             label: "Austrelia"
//         },
//         {
//             value: 5500,
//             color: "#ff9800",
//             highlight: "#ffb74d",
//             label: "India"
//         },
//         {
//             value: 2100,
//             color: "#009688",
//             highlight: "#80cbc4",
//             label: "Brazil"
//         },
//         {
//             value: 5000,
//             color: "#00acc1",
//             highlight: "#4dd0e1",
//             label: "China"
//         },
//         {
//             value: 3500,
//             color: "#4caf50",
//             highlight: "#81c784",
//             label: "Germany"
//         }



//     ];    

var param = window.location.search.substring(1);
var parts = param.split("=");
if(parts[0] == "session"){
    var session = parts[1];
    var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
    console.log(session);
    xmlhttp.open("GET", "http://0.0.0.0:5200/cloud/v0.1/private/"+session+"/user/dashboard");
    xmlhttp.send();
    xmlhttp.onreadystatechange=function()
    {
        // console.log(xmlhttp.responseText);
        if ((xmlhttp.status >= 200 && xmlhttp.status <= 300) || xmlhttp.status == 304) {
            // console.log(xmlhttp.responseText);
            var response = JSON.parse(xmlhttp.responseText);
            console.log(response);
            var projects_total = response["projects_total"];
            var records_total = response["records_total"];
            var environments_total = response["environments_total"];
            var projects = response["projects"];

            document.getElementById("trending-line-chart-wrapper").innerHTML = "<canvas id=\"trending-line-chart\" height=\"70\"></canvas>";

            document.getElementById("doughnut-chart-wrapper").innerHTML = "<canvas id=\"doughnut-chart\" height=\"200\"></canvas><div class=\"doughnut-chart-status\" id=\"doughnut-chart-status\">"+records_total+"<p class=\"ultra-small center-align\">Records</p></div>";

            document.getElementById("trending-bar-chart-wrapper").innerHTML = "<canvas id=\"trending-bar-chart\" height=\"90\"></canvas>";

            // document.getElementById("doughnut-chart-status").innerHTML = "<div class=\"doughnut-chart-status\">"+records_total+"<p class=\"ultra-small center-align\">Records</p></div>";
            
            // console.log("Total Projects:"+projects_total);
            // console.log("Total Records:"+records_total);
            // console.log("Total Environments:"+environments_total);
            // console.log("Projects:"+projects);
            data["datasets"] = [];
            dataBarChart["datasets"] = [];
            // radarChartData["labels"] = [];
            // radarChartData["datasets"] = [];
            doughnutData = []

            color = "#000000";
            console.log(data);
            for(var i = 0; i < response["projects"].length; i++){
                var project = response["projects"][i];
                // radarChartData["labels"].push(project["name"]);
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

                // console.log(dataset);

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
                // radarChartData["datasets"].push(project["records"]["January"]["number"]+project["records"]["February"]["number"]+project["records"]["March"]["number"]+project["records"]["April"]["number"]+project["records"]["May"]["number"]+project["records"]["June"]["number"]+project["records"]["July"]["number"]+project["records"]["August"]["number"]+project["records"]["September"]["number"]+project["records"]["October"]["number"]+project["records"]["November"]["number"]+project["records"]["December"]["number"]);

                // console.log(data);
            }
            console.log(data);
            try{
                var trendingLineChart = document.getElementById("trending-line-chart").getContext("2d");
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

                    var doughnutChart = document.getElementById("doughnut-chart").getContext("2d");
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

                    var trendingBarChart = document.getElementById("trending-bar-chart").getContext("2d");
                    window.trendingBarChart = new Chart(trendingBarChart).Bar(dataBarChart,{
                        scaleShowGridLines : false,///Boolean - Whether grid lines are shown across the chart
                        showScale: true,
                        animationSteps:15,
                        tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                        responsive : true
                    });

                    // window.trendingRadarChart = new Chart(document.getElementById("trending-radar-chart").getContext("2d")).Radar(radarChartData, {
                        
                    //     angleLineColor : "rgba(255,255,255,0.5)",//String - Colour of the angle line            
                    //     pointLabelFontFamily : "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label    
                    //     pointLabelFontColor : "#fff",//String - Point label font colour
                    //     pointDotRadius : 4,
                    //     animationSteps:15,
                    //     pointDotStrokeWidth : 2,
                    //     pointLabelFontSize : 12,
                    //     responsive: true
                    // });

                    // var pieChartArea = document.getElementById("pie-chart-area").getContext("2d");
                    // window.pieChartArea = new Chart(pieChartArea).Pie(pieData,{
                    //     responsive: true        
                    // });

                    // var lineChart = document.getElementById("line-chart").getContext("2d");
                    // window.lineChart = new Chart(lineChart).Line(lineChartData, {
                    //     scaleShowGridLines : false,
                    //     bezierCurve : false,
                    //     scaleFontSize: 12,
                    //     scaleFontStyle: "normal",
                    //     scaleFontColor: "#fff",
                    //     responsive: true,            
                    // });

                    // var polarChartCountry = document.getElementById("polar-chart-country").getContext("2d");
                    // window.polarChartCountry = new Chart(polarChartCountry).PolarArea(polarData, {
                    //     segmentStrokeWidth : 1,            
                    //     responsive:true
                    // });
                console.log(data);
            }
            catch(err) {
                console.log(err.message);
            }
            console.log(data);

        } else {
            // Materialize.toast('<span>Cannot reach the cloud!</span>', 3000);
            console.log("Cannot reach the cloud!");
        }
    }
}else{
    window.onload = function(){
        var trendingLineChart = document.getElementById("trending-line-chart").getContext("2d");
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

            var doughnutChart = document.getElementById("doughnut-chart").getContext("2d");
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

            var trendingBarChart = document.getElementById("trending-bar-chart").getContext("2d");
            window.trendingBarChart = new Chart(trendingBarChart).Bar(dataBarChart,{
                scaleShowGridLines : false,///Boolean - Whether grid lines are shown across the chart
                showScale: true,
                animationSteps:15,
                tooltipTitleFontFamily: "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label        
                responsive : true
            });

            // window.trendingRadarChart = new Chart(document.getElementById("trending-radar-chart").getContext("2d")).Radar(radarChartData, {
                
            //     angleLineColor : "rgba(255,255,255,0.5)",//String - Colour of the angle line            
            //     pointLabelFontFamily : "'Roboto','Helvetica Neue', 'Helvetica', 'Arial', sans-serif",// String - Tooltip title font declaration for the scale label    
            //     pointLabelFontColor : "#fff",//String - Point label font colour
            //     pointDotRadius : 4,
            //     animationSteps:15,
            //     pointDotStrokeWidth : 2,
            //     pointLabelFontSize : 12,
            //     responsive: true
            // });

            // var pieChartArea = document.getElementById("pie-chart-area").getContext("2d");
            // window.pieChartArea = new Chart(pieChartArea).Pie(pieData,{
            //     responsive: true        
            // });

            // var lineChart = document.getElementById("line-chart").getContext("2d");
            // window.lineChart = new Chart(lineChart).Line(lineChartData, {
            //     scaleShowGridLines : false,
            //     bezierCurve : false,
            //     scaleFontSize: 12,
            //     scaleFontStyle: "normal",
            //     scaleFontColor: "#fff",
            //     responsive: true,            
            // });

            // var polarChartCountry = document.getElementById("polar-chart-country").getContext("2d");
            // window.polarChartCountry = new Chart(polarChartCountry).PolarArea(polarData, {
            //     segmentStrokeWidth : 1,            
            //     responsive:true
            // });

    };
}
