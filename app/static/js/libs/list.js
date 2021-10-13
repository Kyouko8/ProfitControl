document.addEventListener('DOMContentLoaded', function() {
    screen_width = screen.width

    window.addEventListener("resize", () =>{
        screen_width = screen.width
    });

    /* Moved to 'buttons.js'

    window.addEventListener("scroll", function(){
        if (window.scrollY <= 0){

            if (screen_width >= 992){
                document.getElementById("option_buttons").classList.add("on-top")

            }

        }else{
            if (screen_width >= 992){
                document.getElementById("option_buttons").classList.remove("on-top")
            }
        }
    })
    */


    /*
    const delete_buttons = document.querySelectorAll(".btn-delete")

    for (let i = 0; i < delete_buttons.length; i++) {
        let btn = delete_buttons[i];

        btn.addEventListener("click", ()=>{
            let token = btn.getAttribute("data-token")

            // modificar btn del modal
            // abrir modal
        })
        
    */

})