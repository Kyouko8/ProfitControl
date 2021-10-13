window.onload = () =>{

    let csrf_token = $('meta[name=csrf-token]').attr('content')
    
    const headers = {'content-type': 'application/json','accept': 'application/json', "X-CSRFToken": csrf_token}

    const config_checkbox_elements = document.querySelectorAll(".config-checkbox");
    const config_radio_elements = document.querySelectorAll(".config-radio");
    const user_id_value = getValueOfElementId("user_id");

    function getValueOfElementId(element_id, default_value=null){
        try{
            element = document.getElementById(element_id)
            if (element != null){
                return element.value
            } else {
                return default_value
            }
        } catch(error){
            return default_value
        }
    }


    function sendConfig(config, value){
        try {
            fetch("/api/user/config/set/", {
                method: "POST",
                body: JSON.stringify({
                    'user_id': user_id_value,
                    "config": config,
                    'value': value
                }),
                headers: headers
            })
            .then( resp => {
                if (resp.ok){
                    
                }else{
                    throw "Estado de respuesta: "+ resp.status
                }
            })
            .catch(error => {
                console.log(error)
            })

        } catch (error) {
            console.error(error)
        }

    }

    /* Enable/disable an specific element */
    function enable_disable_element(element, enable=true){
        if (enable){
            if (element.classList.contains("disabled")){
                element.classList.remove("disabled");
            }
            element.removeAttribute("disabled")
        } else {
            element.classList.add("disabled");
            element.setAttribute("disabled", "disabled")
        }
    }

    /* Enable/disable element specified in data-disable-config and data-enable-config attribute.*/
    function enable_disable_configs(element){
        /* Disable */
        disable_config = element.getAttribute("data-disable-config")
        if (disable_config != null){
            array = document.getElementsByName(disable_config);
            
            for (let index = 0; index < array.length; index++) {
                const input_element = array[index];
                enable_disable_element(input_element, !element.checked)
            }
            
        }
        /* Enable */
        enable_config = element.getAttribute("data-enable-config")
        if (enable_config != null){
            if (enable_config != disable_config){
                array = document.getElementsByName(disable_config);
            
                for (let index = 0; index < array.length; index++) {
                    const input_element = array[index];
                    enable_disable_element(input_element, element.checked)
                }
            } else {
                console.error("Activando y desactivando la misma sección: ", element)
            }
        }
    }


    for (let index = 0; index < config_checkbox_elements.length; index++) {
        const element = config_checkbox_elements[index];
        
        element.addEventListener("click", function () {
            sendConfig(this.getAttribute("name"), this.checked)
            enable_disable_configs(this);
        });

        enable_disable_configs(element);
    }

    for (let index = 0; index < config_radio_elements.length; index++) {
        const element = config_radio_elements[index];
        
        element.addEventListener("click", function(){
            sendConfig(this.getAttribute("name"), this.value)
        });
    }
}