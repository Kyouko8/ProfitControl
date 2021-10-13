document.addEventListener('DOMContentLoaded', function() {
    screen_width = screen.width

    window.addEventListener("resize", () =>{
        screen_width = screen.width
    });

    
    window.addEventListener("scroll", function(){
        try{
            if (window.scrollY <= 0){

                if (screen_width >= 992){
                    document.getElementById("option_buttons").classList.add("on-top")

                }

            }else{
                if (screen_width >= 992){
                    document.getElementById("option_buttons").classList.remove("on-top")
                }
            }
        } catch (error) {}
    })
})