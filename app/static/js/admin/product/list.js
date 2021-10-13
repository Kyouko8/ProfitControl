document.addEventListener('DOMContentLoaded', function() {

    let csrf_token = $('meta[name=csrf-token]').attr('content')

    const headers = {'content-type': 'application/json', 'accept': 'application/json', "X-CSRFToken": csrf_token}

    const product_stock = token => document.querySelector("#product_stock_"+token+" .stock")

    screen_width = screen.width

    function change_table_size(){
        try {

            if (screen.width <= 330){
                document.querySelector(".product-table").classList.add("responsive-table")
                document.querySelector(".product-table").classList.remove("product-table")
            }
            else{
                document.querySelector(".responsive-table").classList.add("product-table")
                document.querySelector(".responsive-table").classList.remove("responsive-table")
            }

        } catch (error) {
            
        }
    }

    change_table_size()

    window.addEventListener("resize", () =>{
        change_table_size()
        screen_width = screen.width
    });


    modify_stock_buttons = document.querySelectorAll(".btn-modify-stock")

    for (let i = 0; i < modify_stock_buttons.length; i++) {
        let button = modify_stock_buttons[i];
        
        button.addEventListener("click", function(){
            let mode = this.getAttribute("data-mode")
            let token = this.getAttribute("data-token")

            if (mode == "add"){
                product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)+1
            }else if (mode == "remove"){
                product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)-1
            }

            modify_product_stock(token, mode);

        })
    }

    function modify_product_stock(token, mode){

        try {
            fetch("/api/modify/product/stock/", {
                method: "POST",
                body: JSON.stringify({'product_token': token, "mode": mode}),
                headers: headers
            })
            .then( resp => {
                if (resp.ok){
                    return resp.json()
                }else{
                    throw resp.status
                }
            })
            .then(resp => {
                let product_stock_td = document.querySelector("#product_stock_"+token) 
                let product_stock_remove_button = document.querySelector("#product_stock_"+token+" .btn-remove-stock")
                
                if (resp.new_stock >= 1){
                    product_stock(token).innerHTML = resp.new_stock

                    product_stock_remove_button.classList.remove("disabled")
                    product_stock_td.classList.remove("red-text", "lighten-3")
                    product_stock_td.classList.add("white-text")
                } else {
                    product_stock(token).innerHTML = "0"

                    product_stock_remove_button.classList.add("disabled")
                    product_stock_td.classList.remove("white-text")
                    product_stock_td.classList.add("red-text", "lighten-3")
                }

                M.toast({html: 'El stock se ha modificado.', classes: 'rounded'});
            })
    
            .catch(status => {
                if (status == 400){
                    M.toast({html: 'La solicitud no fue hecha correctamente.', classes: 'rounded toast-error'});

                }else if (status == 404){
                    M.toast({html: 'Uno de los parámetros es incorrecto.', classes: 'rounded toast-error'});

                }else if (status == 403){
                    M.toast({html: 'El ID de usuario no corresponde con el producto.', classes: 'rounded toast-error'});

                }else if (status == 500){
                    M.toast({html: 'Hubo un error al intentar modificar el stock', classes: 'rounded toast-error'});

                }else{
                    alert("Ha ocurrido un error inesperado: código de error: "+ status)
                }

                if (mode == "add"){
                    product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)-1
                }else if (mode == "remove"){
                    product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)+1
                }            
            })

        } catch (error) {

            if (mode == "add"){
                product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)-1
            }else if (mode == "remove"){
                product_stock(token).innerHTML = parseInt(product_stock(token).innerHTML)+1
            }

            M.toast({html: 'Ha ocurrido un error al intentar modificar el stock.', classes: 'rounded toast-error'});

            console.error(error)
        }


    }

    /* SEARCH SYSTEM */
    const search_advanced_section = document.querySelector("#search-advanced");
    const btn_search_advanced = document.querySelector("#btnSearchAdvanced");
    const search_advanced_icon = document.querySelector("#btnSearchAdvanced .material-icons")

    btn_search_advanced.addEventListener("click", function () {

        if (search_advanced_section.classList.contains("no-display")){
            search_advanced_section.classList.remove("no-display")
            search_advanced_icon.innerHTML = "expand_less"
        } else {
            search_advanced_section.classList.add("no-display")
            search_advanced_icon.innerHTML = "expand_more"
        }
    })

})