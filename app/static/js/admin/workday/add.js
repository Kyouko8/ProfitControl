document.addEventListener('DOMContentLoaded', function() {
    const datepickers = document.querySelectorAll(".datepicker")

    function add_actual_date(element){
        let today = new Date();
        let dd = String(today.getDate()).padStart(2, '0');
        let mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        let yyyy = today.getFullYear();
    
        today = dd + '/' + mm + '/' + yyyy;
        
        element.value = today
    }

    function add_default_date(element){
        add_actual_date(element)

        default_date = element.getAttribute("data-default-value");

        if (default_date != null){
            if (default_date.length >= 5){
                element.value = default_date
            }
        }
    }

    for (let index = 0; index < datepickers.length; index++) {
        const element = datepickers[index];
        add_default_date(element)
    }

    document.getElementById("btn-add-actual-date").addEventListener("click", () => add_actual_date(document.getElementById("date")))

});