if(localStorage.getItem('startDate'))
{
    window.onload = function () {

        var dps = []; // dataPoints
        var chart = new CanvasJS.Chart("chartAvgAtt", {
            theme: "light1",
            axisY: {
                includeZero: true
            },
            data: [{
                type: "line",
                dataPoints: dps
            }]
        });

        var xVal = localStorage.getItem('startDate');
        console.log(localStorage.getItem('startDate'));
        var yVal = null;
        var updateInterval = 5000;
        var dataLength = 20; // number of dataPoints visible at any point
        var dummyRecordInterval = 1000;

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
                            yVal = data.attentiveness;
                            var day = data.dt[0]+""+data.dt[1];
                            var month = data.dt[3]+""+data.dt[4];
                            var year = data.dt[6]+""+data.dt[7]+""+data.dt[8]+""+data.dt[9]
                            var hr = data.dt[11]+""+data.dt[12];
                            var min = data.dt[14]+""+data.dt[15];
                            var sec = data.dt[17]+""+data.dt[18];
                            xVal = new Date(year,month,day,hr,min,sec);
                        }
                    }
                }
            )
        }


        var updateChart = function (count) {

            count = count || 1;

            for (var j = 0; j < count; j++) {
                //yVal = yVal +  Math.round(5 + Math.random() *(-5-5));
                dps.push({
                    x: xVal,
                    y: yVal
                });
                xVal++;
            }

            if (dps.length > dataLength) {
                dps.shift();
            }

            chart.render();
        };
        //Initially call once
        updateChart(dataLength);
        setInterval(function(){updateChart()}, updateInterval);
        if (yVal != null && xVal!=null)
        {
            updateChart(dataLength);
            setInterval(function(){updateChart()}, updateInterval);
        }


        //Updating Charts Data from Database
        getData();
        setInterval(function(){getData()}, updateInterval);

        //Remove this when data is updated automatically
        setInterval(function(){dummyRecordIns()}, dummyRecordInterval);
        
    }
}