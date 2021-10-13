document.addEventListener('DOMContentLoaded', function() {
    try {
        
        const delete_buttons = document.querySelectorAll(".btn-delete")
        const btn_modal_delete = document.getElementById("btn_modal_delete")
        const modal_instance = M.Modal.getInstance(document.getElementById('modal_delete_item'));

        

        for (let i = 0; i < delete_buttons.length; i++) {
            let btn = delete_buttons[i];
            let url = btn.getAttribute("data-url")
            let element = btn.getAttribute("data-element")
    
            btn.addEventListener("click", ()=>{
                btn_modal_delete.href = url

                modal_instance.open()
            })
        }

    } catch (error) {
        
    }

    // FLASH ALERT //
	try {
		document.getElementById("closeFlash").addEventListener('click', function(){
			$("#flash-alert").remove();
		})
	} catch (error) {
			
	}

	// SHOW / HIDE PASSWORD //
    try {

        const password_visibility = document.querySelectorAll(".password-visibility")

        for (let i = 0; i < password_visibility.length; i++) {
            password_visibility[i].addEventListener("click", function(){
                let target_id = this.getAttribute("data-target");
                let target = document.getElementById(target_id);
    
                if (target.getAttribute("type") == "password"){
                    target.setAttribute("type", "text")
                    this.innerText = "visibility_off";
                }else{
                    target.setAttribute("type", "password")
                    this.innerText = "visibility";
                }
    
                
            })
            
        }        
        
    } catch (error) {
        
    }

    /* Dylan */
    function hideOptionButton(){
        try{
            let nav_options_parent = document.getElementById("nav_options_parent")
            if (nav_options_parent != null){
                let nav_options = document.getElementById("nav_options")

                if (nav_options == null){
                    nav_options_parent.classList.add("no-display")
                } else {
                    if (nav_options.childElementCount == 0){
                        nav_options_parent.classList.add("no-display")
                    }
                }
            }
        }catch(error){}
    }

    hideOptionButton()

})