window.onload = () =>{

    let csrf_token = $('meta[name=csrf-token]').attr('content')
    
    const headers = {'content-type': 'application/json','accept': 'application/json', "X-CSRFToken": csrf_token}

    const search_btn = document.getElementById("search_btn")
    const search_results = document.getElementById("search_results")
    const results_list = document.getElementById("results_list")
    const search_loader = document.getElementById("search_loader")
    const search_results_title =  document.querySelector("#search_results .title")
    const next_search = document.getElementById("next_search")
    const previous_search = document.getElementById("previous_search")

    const searched_product_val = () => document.getElementById("product").value
    const workday_token_val = () => document.getElementById("workday_token_input").value
    const page_number_val = () =>  parseInt( document.getElementById("search_page_number").value )

    /**
     * @description Habilita o deshabilita el botón de buscar producto si el valor del input es mayor o menor a 3
     * @version 1.0
    */  
    function enable_disabled_search_button(){
        if (searched_product_val().length >= 3){
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

        if (searched_product_val().length >= 3){
            search_product( searched_product_val(),  workday_token_val())

        }else{
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Debe escribir almenos 3 caracteres para obtener un resultado."
        }

        search_results.classList.remove("no-display")        
    }


    /**
     * @description Habilita o deshabilta el boton de anterior o siguiente búsqueda
     * @version 1.0
    */    
    function enable_disabled_pagination_buttons(info){
        if (info.has_prev == true) {
            previous_search.classList.remove("disabled")

        } else {
            previous_search.classList.add("disabled")
        }

        if (info.has_next == true) {
            next_search.classList.remove("disabled")

        } else {
            next_search.classList.add("disabled")
        }
    }

    /**
     * @description Crea y muestra los resúltados de la búsqueda
     * @version 1.0
    */      
    function create_results_items(items){
        for (let index = 0; index < items.length; index++) {
            let result = items[index];
            
            let result_item = document.createElement("li")
            result_item.classList.add("collection-item", "result", "hoverable")
            
            let result_url = document.createElement("a")
            result_url.href = result.url

            result_url.appendChild( result_item ) // <a> <li> </li> </a>

            result_item.appendChild( document.createTextNode(result.name) )  // <a> <li> texto </li> </a>
            
            results_list.appendChild(result_url)  // <div> <a> <li> texto </li> </a> </div>
        }
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
        search_product(searched_product_val(), workday_token_val(), page_number_val()+1)
    })

    // Escuchador de eventos para el botón de anterior página
    previous_search.addEventListener("click", ()=>{        
        search_product(searched_product_val(), workday_token_val(), page_number_val()-1)
    })
    
    // Escuchador de eventos para el botón de buscar producto
    search_btn.addEventListener("click", search_btn_action)


    /**
     * @description Buscá el producto mediante un fetch
     * @version 1.0
    */  
    function search_product(product_name, workday_token, page=1){
        try {
            
            results_list.innerHTML = ""
            search_results_title.innerHTML = "Buscando..." 
            show_hide_loader("show")

            search_btn.classList.add("disabled")

            fetch("/api/search/product/", {
                method: "POST",
                body: JSON.stringify({'product_name': product_name, "workday_token": workday_token, 'page': page}),
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
                let info = res.info
                
                if (resp.length > 0){
                    results_list.innerHTML = ""
    
                    search_results_title.innerHTML = "Resultados de búsqueda:"
    
                    create_results_items(resp)
                    
                    document.getElementById("search_page_number").value = info.page
                    
                    console.log(info)

                    enable_disabled_pagination_buttons(info)
                    
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
            alert(error)
            console.error(error)
        }

        search_btn.classList.remove("disabled")

    }

}