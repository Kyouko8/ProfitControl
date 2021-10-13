document.addEventListener('DOMContentLoaded', function() {

    let csrf_token = $('meta[name=csrf-token]').attr('content')

    const headers = {'content-type': 'application/json', 'accept': 'application/json', "X-CSRFToken": csrf_token}
    const by_unit = parseInt(document.getElementById("by_unit").value);
    const client_results_section = document.getElementById("client-results-section");
    const client_results_restart = document.getElementById("client-results-restart");

    const sale_quantity = token => document.querySelector("#sale_quantity_"+token+" .stock")

    modify_stock_buttons = document.querySelectorAll(".btn-modify-stock")

    for (let i = 0; i < modify_stock_buttons.length; i++) {
        let button = modify_stock_buttons[i];
        
        button.addEventListener("click", function(){
            let mode = this.getAttribute("data-mode")
            let sale_token = this.getAttribute("data-token")
            let client_token = this.getAttribute("data-client")

            if (mode == "add"){
                sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)+1
            }else if (mode == "remove"){
                sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)-1
            }

            modify_sale_quantity(client_token, sale_token, mode);

        })
    }

    function modify_sale_quantity(client_token, sale_token, mode){

        try {
            fetch("/api/modify/c/sale/quantity/", {
                method: "POST",
                body: JSON.stringify({'client_token': client_token, 'sale_token': sale_token, "mode": mode, "by_unit": by_unit}),
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
                let sale_quantity_td = document.querySelector("#sale_quantity_"+sale_token) 
                let sale_quantity_remove_button = document.querySelector("#sale_quantity_"+sale_token+" .btn-remove-stock")
                let sale_quantity_add_button = document.querySelector("#sale_quantity_"+sale_token+" .btn-add-stock")

                // ¿Se calcula por unidad o por total?
                // if not by_unit: Se calcula por total, hay que actualizar los datos al actualizar el stock
                if (!by_unit) {
                    let sale_price_td = document.querySelector("#sale_price_"+sale_token)
                    let sale_paid_td = document.querySelector("#sale_paid_"+sale_token)
                    let sale_not_paid_td = document.querySelector("#sale_npaid_"+sale_token)

                    sale_price_td.innerHTML = "$" + (resp.new_stock * resp.data.price)
                    sale_paid_td.innerHTML = "$" + (resp.new_stock * resp.data.cost)
                    sale_not_paid_td.innerHTML = "$" + (resp.new_stock * (resp.data.price - resp.data.cost))
                }
                
                // Activar el botón "-" si el stock es >= 1, desactivarlo en otro caso.
                if (resp.new_stock >= 1){
                    sale_quantity(sale_token).innerHTML = resp.new_stock

                    sale_quantity_remove_button.classList.remove("disabled")
                    sale_quantity_td.classList.remove("red-text", "lighten-3")
                    sale_quantity_td.classList.add("white-text")
                } else {
                    sale_quantity(sale_token).innerHTML = "0"

                    sale_quantity_remove_button.classList.add("disabled")
                    sale_quantity_td.classList.remove("white-text")
                    sale_quantity_td.classList.add("red-text", "lighten-3")
                }

                // Deshabilitar el boton "+" cuando no haya stock disponible
                if (resp.data.disable_add){
                    sale_quantity_add_button.classList.add("disabled")
                } else {
                    sale_quantity_add_button.classList.remove("disabled")
                }

                // Ocultar el Resumen y mostrar un botón para recargar.
                if (!client_results_section.classList.contains("no-display")){
                    client_results_restart.classList.remove("no-display");
                    client_results_section.classList.add("no-display")
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
                    sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)-1
                }else if (mode == "remove"){
                    sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)+1
                }            
            })

        } catch (error) {

            if (mode == "add"){
                sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)-1
            }else if (mode == "remove"){
                sale_quantity(sale_token).innerHTML = parseInt(sale_quantity(sale_token).innerHTML)+1
            }

            M.toast({html: 'Ha ocurrido un error al intentar modificar el stock.', classes: 'rounded toast-error'});

            console.error(error)
        }


    }

})

