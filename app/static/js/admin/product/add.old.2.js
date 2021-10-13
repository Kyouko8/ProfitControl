window.onload = () =>{

    const headers = {'content-type': 'application/json','accept': 'application/json', "X-CSRFToken": csrf_token}

    const search_btn = document.getElementById("search_btn")
    const search_results = document.getElementById("search_results")
    const results_list = document.getElementById("results_list")
    const search_loader = document.getElementById("search_loader")
    const search_results_title =  document.querySelector("#search_results .title")
    const previous_next_search = document.querySelector(".previous_next_search")
    const next_search = document.getElementById("next_search")
    const previous_search = document.getElementById("previous_search")


    const searched_product = () => document.getElementById("product").value
    const workday_token = () => document.getElementById("workday_token_input").value
    const page_number = () =>  parseInt( document.getElementById("search_page_number").value )

    /**
     * @description Habilita o deshabilita el botón de buscar producto si el valor del input es mayor o menor a 3
     * @version 1.0
    */  
    function enable_disabled_search_button(){
        if (this.value.length >= 3){
            search_btn.classList.remove("disabled")
        }else{
            search_btn.classList.add("disabled")
        }
    }
    // Se llama la función para habiltar o deshabiltar el botón inmediatamente cargué la página
    enable_disabled_search_button()

    /**
     * @description Crea el loader de la búsqueda
     * @version 1.0
     * @returns element
    */      
    function create_loader(){
        let div = document.createElement("div")
        div.classList.add("indeterminate")

        return div
    }

    /**
     * @description Muestra u oculta el loader
     * @version 1.0
    */     
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
     * @description Obtiene y compara los valores para realizar la búsqueda del producto
     * @version 1.0
    */
    function search_btn_action(){

        if (searched_product.length >= 3){
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Buscando..." 
            show_hide_loader("show")
            search_product( searched_product,  workday_token, page_number )

        }else{
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Debe escribir almenos 3 caracteres para obtener un resultado."
        }

        document.getElementById("search_page_number").value = 0
        search_results.classList.remove("no-display")        
    }

    // Escuchador de eventos para el botón de buscar producto
    search_btn.addEventListener("click", search_btn_action)

    /**
     * Boton de página siguiente
     */
    function setActionChangePage(item, increment=1){
        item.addEventListener("click", function() {
            let searched_product = document.getElementById("product").value;
            let workday_token = document.getElementById("workday_token_input").value;
            let page_number = parseInt( document.getElementById("search_page_number").value )
    
            if (!item.classList.contains("disabled")){
                document.getElementById("previous_search").classList.add("disabled")
                document.getElementById("next_search").classList.add("disabled")
                if (searched_product.length >= 3){
                    results_list.innerHTML = ""
                    search_results_title.innerHTML = "Buscando..."
                    show_hide_loader("show")
                    search_product( searched_product,  workday_token, page_number + increment)
        
                }else{
                    results_list.innerHTML = ""
                    search_results_title.innerHTML = "Debe escribir almenos 3 caracteres para obtener un resultado."
                }
            }
    
            search_results.classList.remove("no-display")
        })
    }

    // Escuchador de eventos para cerrar la pestaña de resultados del buscador
    document.getElementById("close_search_results").addEventListener("click", () => {
        search_results.classList.add("no-display")
        show_hide_loader("hide")
    })

    // Escuchador de eventos para que, al estar escribiendo sobre el input del producto, se active o desactive el botón de búsqueda
    document.getElementById("product").addEventListener("keyup", enable_disabled_search_button)

    // Escuchador de eventos para el botón de siguiente página
    next_search.addEventListener("click", ()=>{        
        search_product(searched_product, workday_token, page_number+1)
    })

    // Escuchador de eventos para el botón de anterior página
    previous_search.addEventListener("click", ()=>{        
        search_product(searched_product, workday_token, page_number-1)
    })
    



    function search_product(product_name, workday_token, page=1){
        try {
            
            fetch("/api/search/product/", {
                method: "POST",
                body: JSON.stringify({'product_name': product_name, "workday_token": workday_token, 'page': page}),
                headers: headers
            })
            .then( resp => {
                if (resp.ok){
                    return resp.json()
                }
            })
            .then(res => {
                let resp = res.data
                let info = res.info

                let previous_search1 = document.getElementById("previous_search")
                let next_search1 = document.getElementById("next_search")
                
                if (resp.length > 0){
                    // results_list.innerHTML = ""
    
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
                    
                    document.getElementById("search_page_number").value = info.page
                    
                    console.log(info)
        
                    if (info.has_prev == true) {
                        // let result_item = document.createElement("li")
                        // result_item.classList.add("collection-item")
                        // result_item.classList.add("result")
                        // result_item.classList.add("hoverable")
    
                        // let result_url = document.createElement("a")
                        // setActionChangePage(result_url, -1) /* decrement page +1 */
    
                        // result_url.appendChild( result_item )
                        // result_item.appendChild( document.createTextNode("Anterior") )
                        // results_list.appendChild(result_url)
    
                        previous_search1.classList.remove("disabled")

                        if (!previous_search1.classList.contains("search-configured")){
                            setActionChangePage(previous_search1, -1)
                            previous_search1.classList.add("search-configured")
                        }
                        // previous_search1.addEventListener("click", function(){
                        //     search_product(product_name, workday_token, page=page-1)
                        // })

                    } else {
                        previous_search1.classList.add("disabled")
                    }
    
                    if (info.has_next == true) {
                        // let result_item = document.createElement("li")
                        // result_item.classList.add("collection-item")
                        // result_item.classList.add("result")
                        // result_item.classList.add("hoverable")
    
                        // let result_url = document.createElement("a")
                        // setActionChangePage(result_url, +1) /* increment page +1 */
    
                        // result_url.appendChild( result_item )
                        // result_item.appendChild( document.createTextNode("Siguiente") )
                        // results_list.appendChild(result_url)

                        next_search1.classList.remove("disabled")

                        if (!next_search1.classList.contains("search-configured")){
                            setActionChangePage(next_search1, +1)
                            next_search1.classList.add("search-configured")
                        }

                        // next_search1.addEventListener("click", function(){
                        //     search_product(product_name, workday_token, page=page+1)
                        // })
                    } else {
                        next_search1.classList.add("disabled")
                    }
                    
                    show_hide_loader("hide")

                    if (info.has_prev || info.has_next){
                        document.getElementById("previous_next_search").classList.remove("no-display")
                    }else{
                        document.getElementById("previous_next_search").classList.add("no-display")
                    }                    
    
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

        } catch (error) {
            console.error(error)
        }



    }

}