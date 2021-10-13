document.onreadystatechange = () => {

    console.log(screen.width)

    if (screen.width <= 992){

        document.getElementById("mobile_fullscreen").classList.add("fullscreen")
    }

    

}