window.onload = () =>{

    const headers = {'content-type': 'application/json','accept': 'application/json', "X-CSRFToken": csrf_token}

    const search_btn = document.getElementById("search_btn")
    const search_results = document.getElementById("search_results")
    const results_list = document.getElementById("results_list")
    const search_loader = document.getElementById("search_loader")
    const search_results_title =  document.querySelector("#search_results .title")

    function search_product(product_name, workday_token){

        fetch("/api/search/product/", {
            method: "POST",
            body: JSON.stringify({'product_name': product_name, "workday_token": workday_token}),
            headers: headers
        })
        .then( resp => {
            if (resp.ok){
                return resp.json()
            }
        })
        .then(res => {
            let resp = res.data
			console.log(resp)
            if (resp.length > 0){
                results_list.innerHTML = ""

                search_results_title.innerHTML = "Resultados de búsqueda:"

                for (let index = 0; index < resp.length; index++) {
                    let result = resp[index];
                    
                    let result_item = document.createElement("li")
                    result_item.classList.add("collection-item")
                    result_item.classList.add("result")
                    result_item.classList.add("hoverable")
                    
                    let result_url = document.createElement("a")
                    result_url.href = result.url

                    result_url.appendChild( result_item )

                    result_item.appendChild( document.createTextNode(result.name) )
                    
                    results_list.appendChild(result_url)
                }

                show_hide_loader("hide")

            }else{
                search_results_title.innerHTML = "No hay resultados para tu búsqueda."
                show_hide_loader("hide")
            }
        })

        .catch(error => {
            console.log(error)
            search_results_title.innerHTML = "Ha ocurrido un error al intentar procesar los datos."
            search_results_title.classList.add("red-text")
            search_results_title.classList.remove("white-text")
            show_hide_loader("hide")
        })

    }

    function create_loader(){
        let div = document.createElement("div")
        div.classList.add("indeterminate")

        return div
    }

    function show_hide_loader(mode){
        if (mode == "show"){
            search_loader.appendChild( create_loader() )
            search_loader.classList.remove("no-display")
        }else{
            search_loader.innerHTML = ""
            search_loader.classList.add("no-display")
        }
    }

    /**
     * BOTON DE BUSCAR
     */
    search_btn.addEventListener("click", function() {
        let searched_product = document.getElementById("product").value;
        let workday_token = document.getElementById("workday_token_input").value

        if (searched_product.length >= 3){
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Buscando..."
            show_hide_loader("show")
            search_product( searched_product,  workday_token)

        }else{
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Debe escribir almenos 3 caracteres para obtener un resultado."
        }

        search_results.classList.remove("no-display")
    })


    /**
     * BOTON DE CERRAR PESTAÑA DE RESULTADOS DE BÚSQUEDA
     */
     document.getElementById("close_search_results").addEventListener("click", () => {
        search_results.classList.add("no-display")
        show_hide_loader("hide")
    })

    /**
     * CHECKEAR SI EL INPUT DE BUSQUEDA TIENE 3 O MÁS CARACTERES
     */
    document.getElementById("product").addEventListener("keyup", function() {
        if (this.value.length >= 3){
            search_btn.classList.remove("disabled")
        }else{
            search_btn.classList.add("disabled")
        }
    })

}