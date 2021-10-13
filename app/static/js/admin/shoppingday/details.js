document.addEventListener('DOMContentLoaded', function() {

    let csrf_token = $('meta[name=csrf-token]').attr('content')

    const headers = {'content-type': 'application/json', 'accept': 'application/json', "X-CSRFToken": csrf_token}
    const by_unit = parseInt(document.getElementById("by_unit").value);
    const shoppingday_results_section = document.getElementById("shoppingday-results-section");
    const shoppingday_results_restart = document.getElementById("shoppingday-results-restart");

    const shopping_quantity = token => document.querySelector("#shopping_quantity_"+token+" .stock")

    modify_stock_buttons = document.querySelectorAll(".btn-modify-stock")

    for (let i = 0; i < modify_stock_buttons.length; i++) {
        let button = modify_stock_buttons[i];
        
        button.addEventListener("click", function(){
            let mode = this.getAttribute("data-mode")
            let shopping_token = this.getAttribute("data-token")
            let shoppingday_token = this.getAttribute("data-shoppingday")

            if (mode == "add"){
                shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)+1
            }else if (mode == "remove"){
                shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)-1
            }

            modify_shopping_quantity(shoppingday_token, shopping_token, mode);

        })
    }

    function modify_shopping_quantity(shoppingday_token, shopping_token, mode){

        try {
            fetch("/api/modify/shopping/quantity/", {
                method: "POST",
                body: JSON.stringify({'shoppingday_token': shoppingday_token, 'shopping_token': shopping_token, "mode": mode, "by_unit": by_unit}),
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
                let shopping_quantity_td = document.querySelector("#shopping_quantity_"+shopping_token) 
                let shopping_quantity_remove_button = document.querySelector("#shopping_quantity_"+shopping_token+" .btn-remove-stock")
                let shopping_quantity_add_button = document.querySelector("#shopping_quantity_"+shopping_token+" .btn-add-stock")

                // ¿Se calcula por unidad o por total?
                // if not by_unit: Se calcula por total, hay que actualizar los datos al actualizar el stock
                if (!by_unit) {
                    let shopping_price_td = document.querySelector("#shopping_price_"+shopping_token)
                    let shopping_cost_td = document.querySelector("#shopping_cost_"+shopping_token)
                    let shopping_profit_td = document.querySelector("#shopping_profit_"+shopping_token)

                    shopping_price_td.innerHTML = "$" + (resp.new_stock * resp.data.price)
                    shopping_cost_td.innerHTML = "$" + (resp.new_stock * resp.data.cost)
                    shopping_profit_td.innerHTML = "$" + (resp.new_stock * (resp.data.price - resp.data.cost))
                }
                
                // Activar el botón "-" si el stock es >= 1, desactivarlo en otro caso.
                if (resp.new_stock >= 1){
                    shopping_quantity(shopping_token).innerHTML = resp.new_stock

                    shopping_quantity_remove_button.classList.remove("disabled")
                    shopping_quantity_td.classList.remove("red-text", "lighten-3")
                    shopping_quantity_td.classList.add("white-text")
                } else {
                    shopping_quantity(shopping_token).innerHTML = "0"

                    shopping_quantity_remove_button.classList.add("disabled")
                    shopping_quantity_td.classList.remove("white-text")
                    shopping_quantity_td.classList.add("red-text", "lighten-3")
                }

                // Deshabilitar el boton "+" cuando no haya stock disponible
                if (resp.data.disable_add){
                    shopping_quantity_add_button.classList.add("disabled")
                } else {
                    shopping_quantity_add_button.classList.remove("disabled")
                }

                // Ocultar el Resumen y mostrar un botón para recargar.
                if (!shoppingday_results_section.classList.contains("no-display")){
                    shoppingday_results_restart.classList.remove("no-display");
                    shoppingday_results_section.classList.add("no-display")
                }

                // Verificar si ocurrió un error, y mostrar el toast correspondiente.
                if (resp.error){
                    M.toast({html: resp.data.name+': '+resp.message+'.', classes: 'rounded toast-error'});
                } else {
                    M.toast({html: resp.data.name+': '+resp.message+'.', classes: 'rounded'});
                }
            })
    
            .catch(status => {
                if (status == 400){
                    M.toast({html: 'La solicitud no fue hecha correctamente.', classes: 'rounded toast-error'});

                }else if (status == 404){
                    M.toast({html: 'Uno de los parámetros es incorrecto.', classes: 'rounded toast-error'});

                }else if (status == 403){
                    M.toast({html: 'El ID de usuario no corresponde con esta venta.', classes: 'rounded toast-error'});

                }else if (status == 500){
                    M.toast({html: 'Hubo un error al intentar modificar el stock', classes: 'rounded toast-error'});

                }else{
                    alert("Ha ocurrido un error inesperado: código de error: "+ status)
                }

                if (mode == "add"){
                    shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)-1
                }else if (mode == "remove"){
                    shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)+1
                }            
            })

        } catch (error) {

            if (mode == "add"){
                shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)-1
            }else if (mode == "remove"){
                shopping_quantity(shopping_token).innerHTML = parseInt(shopping_quantity(shopping_token).innerHTML)+1
            }

            M.toast({html: 'Ha ocurrido un error al intentar modificar el stock.', classes: 'rounded toast-error'});

            console.error(error)
        }


    }

})

