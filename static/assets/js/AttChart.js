if(localStorage.getItem('startDate'))
{
    window.onload = function () {

        /*Avg Attentiveness */
        var dpsAvg = []; // dataPoints
        var chartAvg = new CanvasJS.Chart("chartAvgAtt", {
            theme: "light1",
            axisY: {
                includeZero: true,
                maximum: 100,
                spline: 70
            },
            data: [{
                type: "line",
                dataPoints: dpsAvg
            }]
        });

        var xValAvg = localStorage.getItem('startDate');
        //console.log(localStorage.getItem('startDate'));
        var yValAvg = null;
        var updateIntervalAvg =1000;
        var dataLengthAvg = 20; // number of dataPoints visible at any point
        var dummyRecordInterval = 5000;

        //Remove this when Data is updated automatically!
        var dummyRecordIns = function () {
            $.ajax(
                {
                    type:"POST",
                    url:"/faculty/dummy-record-ins",
                    success: function () {
                      console.log('updated')
                    }
                }
            )
        }

        var getData = function(){
            $.ajax(
                {
                    type:"POST",
                    url:"/faculty/get-avg-attentiveness",
                    success: function (data) {
                        if(data.attentiveness)
                        {
                            yValAvg = data.attentiveness;
                            var day = data.dt[0]+""+data.dt[1];
                            var month = data.dt[3]+""+data.dt[4];
                            var year = data.dt[6]+""+data.dt[7]+""+data.dt[8]+""+data.dt[9]
                            var hr = data.dt[11]+""+data.dt[12];
                            var min = data.dt[14]+""+data.dt[15];
                            var sec = data.dt[17]+""+data.dt[18];
                            xValAvg = new Date(year,month,day,hr,min,sec);
                        }
                    }
                })
        }


        var updateChartAvg = function (count) {

            count = count || 1;

            for (var j = 0; j < count; j++) {
                //yVal = yVal +  Math.round(5 + Math.random() *(-5-5));
                dpsAvg.push({
                    x: xValAvg,
                    y: yValAvg
                });
                xValAvg++;
            }

            if (dpsAvg.length > dataLengthAvg) {
                dpsAvg.shift();
            }

            chartAvg.render();
        };
        //Initially call once
        updateChartAvg(dataLengthAvg);
        setInterval(function(){updateChartAvg()}, updateIntervalAvg);
        if (yValAvg != null && xValAvg!=null)
        {
            updateChartAvg(dataLengthAvg);
            setInterval(function(){updateChartAvg()}, updateIntervalAvg);
        }


        //Updating Charts Data from Database
        getData();
        setInterval(function(){getData()}, updateIntervalAvg);

        //Remove this when data is updated automatically
        setInterval(function(){dummyRecordIns()}, dummyRecordInterval);
        /* End of Avg Attentiveness */



        /* Std-wise Attentiveness */
        var chart = new CanvasJS.Chart("chartStdAtt", {
            axisY: {
                title: "Attentiveness (%)",
                suffix: " %",
                maximum: 100,
                stripLines: [{
                    value: 70,
                    label: ""
                }]
            },
            data: [{
                type: "column",
                indexLabel: "{y}",
                dataPoints: [

                ],

            }]
        });


        function updateChart() {
            var stdAttColor, yVal;
            var dps = chart.options.data[0].dataPoints;
            $.ajax(
                {
                    type:"POST",
                    url:"/faculty/get-std-attentiveness",
                    success: function (data) {
                        for(var i=0;i<data.length;i++)
                        {
                            yVal = data[i]['attentiveness'];
                            stdAttColor = yVal <= 40 ? "#ff3300" : yVal <= 60 ? "#ffa31a" : yVal <= 74 ? "#e6e600" : yVal > 74 ? "#00b300 " : null;
                            dps[i] = {label: data[i]['Name'], y: yVal, color: stdAttColor};
                            //console.log(dps[i])
                        }
                    }
                })
            chart.options.data[0].dataPoints = dps;
            chart.render();
        };
        updateChart();
        setInterval(function() {updateChart()}, 50);
        /* End of Std-wise Attentiveness */
        
    }
}