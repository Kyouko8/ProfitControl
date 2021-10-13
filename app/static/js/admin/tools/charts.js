window.onload = function () {
    let csrf_token = $('meta[name=csrf-token]').attr('content');
    
    const headers = {'content-type': 'application/json','accept': 'application/json', "X-CSRFToken": csrf_token};
    const cost_value = document.getElementById("chart_cost").value;
    const extra_cost_value = document.getElementById("chart_extracost").value;
    const price_value = document.getElementById("chart_price").value;
    const new_value = document.getElementById("chart_new").value;
    const is_user_price = document.getElementById("chart_is_user_price").value;
    const btn_show_chart = document.getElementById("btn_show_chart");

    function loadData(){
        try{
            fetch("/api/tools/chart/niceprice/", {
                method: "POST",
                body: JSON.stringify({
                    'cost': parseInt(cost_value),
                    'extra_cost': parseInt(extra_cost_value),
                    'price': parseInt(price_value),
                    'new': parseInt(new_value),
                    'is_user_price': parseInt(is_user_price)
                }),
                headers: headers
            })
            .then( resp => {
                if (resp.ok){
                    return resp.json()
                }else{
                    throw "Estado de respuesta: "+ resp.status
                }
            })
            .then(res => {
                let resp = res.data
                make_chart(resp.points, resp, "chartContainer")
            })

            .catch(error => {
                console.log(error)
            })

        } catch (error) {
            alert(error)
            console.error(error)
        }

    }

    function make_chart(points, data){
        let chartContainer = document.getElementById("chartContainer");
        chartContainer.classList.remove("no-display");
        
        var chart = new CanvasJS.Chart("chartContainer", {
            animationEnabled: true,
            exportEnabled: true,
            zoomEnabled: true,
            zoomType: "xy",
            theme: "dark1",
            title:{
                text: "Comparación de Precios"
            },
            axisX: {
                title: "Precio",
                interval: 1,
            },
            axisY: {
                minimum: 0,
                title: "Valor",
                prefix: "$"
            },
            toolTip: {
                shared: true
            },
            legend:{
                cursor: "pointer",
                itemclick: toggleDataSeries
            },
            data: [{
                type: "stackedBar",
                name: "Costo",
                showInLegend: "true",
                yValueFormatString: "$#,##0",
                dataPoints: points.cost
            },
            {
                type: "stackedBar",
                name: "Costo Extra",
                showInLegend: "true",
                yValueFormatString: "$#,##0",
                dataPoints: points.extra_cost
            },
            {
                type: "stackedBar",
                name: "Ganancia",
                showInLegend: "true",
                yValueFormatString: "$#,##0",
                dataPoints: points.prices
            }]
        });

        function toggleDataSeries(e) {
            if(typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                e.dataSeries.visible = false;
            }
            else {
                e.dataSeries.visible = true;
            }
            chart.render();
        }

        chart.render();
        console.log("CHART RENDER!")
    }

 
    btn_show_chart.addEventListener("click", function (){
        console.log("chart")
        btn_show_chart.classList.add("disabled")
        loadData()
    });

    /* Result Show/Hide */
    const btn_show_all_results = document.getElementById('btn_show_all_results');
    const btn_hide_all_results = document.getElementById('btn_hide_all_results');
    const inp_show_all_results = document.getElementById('show_all');
    const div_results = document.getElementById('show_all_results');


    btn_show_all_results.addEventListener("click", function (){
        if (div_results.classList.contains("no-display")){
            div_results.classList.remove("no-display");
            btn_show_all_results.innerHTML = '<i class="left material-icons">visibility_off</i> Ocultar resultados irrelevantes'
            inp_show_all_results.value = "1"

        } else {
            div_results.classList.add("no-display");
            btn_show_all_results.innerHTML = '<i class="left material-icons">visibility</i> Ver todos los resultados'
            inp_show_all_results.value = "0"
        }
    })

    btn_hide_all_results.addEventListener("click", ()=>{
        div_results.classList.add("no-display");
        btn_show_all_results.innerHTML = '<i class="left material-icons">visibility</i> Ver todos los resultados'
        inp_show_all_results.value = "0"
    })
};