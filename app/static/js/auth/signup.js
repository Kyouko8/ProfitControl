document.addEventListener('DOMContentLoaded', function() {


    const password_value = () => document.getElementById("password").value 

    document.getElementById("confirm").addEventListener("keyup", function(){
        console.log(this.value)

        if (this.value != password_value){
            this.classList.remove("valid")
            this.classList.add("invalid")

        }else{
            this.classList.add("valid")
            this.classList.remove("invalid")
        }

        // if (this.value.isEmpty()){
        //     this.classList.add("valid")
        // }

    })

})