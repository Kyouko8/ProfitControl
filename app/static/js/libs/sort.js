window.onload = () => {
    const table = document.getElementById("sorted_table");
    const searchInput = document.getElementById("fast_search_input");
    const fastSearchButton = document.getElementById("fast_search_mode");
    const fastSearchSwitch = document.getElementById("fast_search_switch");
    const fastSearchSwitchNavBar = document.getElementById("fast-search-nav-button")


    let columns = {'now': null};

    /* Comparar Por Nombre */
    function compareByName(thead, col, mode='auto'){
        function _compare(x, y, mode){
            if (mode){
                return x.textContent.toLowerCase() < y.textContent.toLowerCase()
            } else {
                return x.textContent.toLowerCase() > y.textContent.toLowerCase()
            }
        }
        sortTable(thead, _compare, col, mode)
    }

    /* Comparar Por Precio */
    function compareByPrice(thead, col, mode='auto'){
        function _compare(x, y, mode){
            num1 = parseInt(x.innerHTML.substring(1))
            num2 = parseInt(y.innerHTML.substring(1))
            if (mode){
                return num1 < num2
            } else {
                return num1 > num2
            }
        }
        sortTable(thead, _compare, col, mode)
    }

    /* Comparar Por Número */
    function compareByNumber(thead, col, mode='auto'){
        function _compare(x, y, mode){
            num1 = parseInt(x.innerHTML)
            num2 = parseInt(y.innerHTML)
            if (mode){
                return num1 < num2
            } else {
                return num1 > num2
            }
        }
        sortTable(thead, _compare, col, mode)
    }

    /* Comparar Por Fecha */
    function compareByDate(thead, col, mode='auto'){
        function _compare(x, y, mode){
            date1 = x.textContent.replace("open_in_new", "").split("/")
            date2 = y.textContent.replace("open_in_new", "").split("/")
            date1 = new Date(parseInt(date1[2].trim()), parseInt(date1[1].trim()), parseInt(date1[0].trim()))
            date2 = new Date(parseInt(date2[2].trim()), parseInt(date2[1].trim()), parseInt(date2[0].trim()))
            if (mode){
                return date1 < date2
            } else {
                return date1 > date2
            }
        }
        sortTable(thead, _compare, col, mode)
    }

    /* Comparar Por Stock */
    function compareByStock(thead, col, mode='auto'){
        function _compare(x, y, mode){
            num1 = parseInt(x.children[1].textContent)
            num2 = parseInt(y.children[1].textContent)
            if (mode){
                return num1 < num2
            } else {
                return num1 > num2
            }
        }
        sortTable(thead, _compare, col, mode)
    }

    /* Asignar el icono a la columna */
    function setIcon(thead, icon){
        let i = thead.getElementsByTagName("i")[0];
        i.innerHTML = icon
        i.classList.add("vertical-wrapper")
    }

    /* Ordenar la Tabla */
    function sortTable(thead, compare, col=0, mode=0) {
        var rows, switching, i, x, y, shouldSwitch;
        switching = true;

        if (mode == "auto"){
            if (columns['now'] === thead){
                mode = (columns[thead] == 0)
            } else {
                mode = false
            }
        }

        columns[thead] = mode
        columns['now'] = thead
        headers = table.getElementsByTagName("th")
        for (var i = 0; i < headers.length; i++){
            setIcon(headers[i], "")
        }

        if (mode == 0){
            setIcon(thead, "arrow_drop_up");
        } else {
            setIcon(thead, "arrow_drop_down")
        }
        /*Make a loop that will continue until
        no switching has been done:*/
        while (switching) {
            //start by saying: no switching is done:
            switching = false;
            rows = table.rows;
            /*Loop through all table rows (except the
            first, which contains table headers):*/
            for (i = 1; i < (rows.length - 1); i++) {
                 //start by saying there should be no switching:
                shouldSwitch = false;
                /*Get the two elements you want to compare,
                one from current row and one from the next:*/
                x = rows[i].getElementsByTagName("td")[col];
                y = rows[i + 1].getElementsByTagName("td")[col];
                //check if the two rows should switch place:
                if (compare(x, y, mode)) {
                    //if so, mark as a switch and break the loop:
                    shouldSwitch = true;
                    break;
                }
            }
            if (shouldSwitch) {
                /*If a switch has been marked, make the switch
                and mark that a switch has been done:*/
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
            }
        }
    }


    function initilizeTable(){
        let headers = table.getElementsByTagName("th");
        let i = 0;
        let data_type;
        for (i = 0; i < headers.length; i++){
            header = headers[i]
            columns[header] = 0;
            header.setAttribute("data-col-number", i)

            if (header.getElementsByTagName("i")[0].textContent == "arrow_drop_up"){
                columns['now'] = header
            }
            
            if (header.getAttribute("data-type") != null){
                header.addEventListener("click", function (){
                    data_type = this.getAttribute("data-type").toLowerCase();
                    col = parseInt(this.getAttribute("data-col-number"))
                    if (data_type == "name"){
                        compareByName(this, col)
                    } else if (data_type == "stock"){
                        compareByStock(this, col)
                    } else if (data_type == "price"){
                        compareByPrice(this, col)
                    } else if (data_type == "number"){
                        compareByNumber(this, col)
                    } else if (data_type == "date"){
                        compareByDate(this, col)
                    }

                    doSearch()
                })
            }
        }
    }

    initilizeTable()




    
    /* FILTROS */
    /* Contains (ignore case) */
    function filterContainsUpper(value, search){
        return value.toUpperCase().indexOf(search.toUpperCase()) > -1
    }

    /* Contains (with case) */
    function filterContains(value, search){
        return value.indexOf(search) > -1
    }

    /* StartsWith (ignore case) */
    function filterStartsWithUpper(value, search){
        return value.toUpperCase().startsWith(search.toUpperCase());
    }
    
    /* StartsWith (with case) */
    function filterStartsWith(value, search){
        return value.startsWith(search);
    }

    
    /* Filtrar tabla */
    function searchFunctionInColumn(col=0, filterMethod=filterContainsUpper) {
        // Declare variables 
        var filter, tr, td, i, txtValue;
        filter = searchInput.value;
        tr = table.getElementsByTagName("tr");
        
        let results = 0;
        // Loop through all table rows, and hide those who don't match the search query
        for (i = 0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[col];
            
            if (td) {
                txtValue = td.textContent || td.innerText;
                if (filterMethod(txtValue, filter)) {
                    tr[i].style.display = "";
                    results += 1;
                } else {
                    tr[i].style.display = "none";
                }
            } 
        }
        document.getElementById("searchNumberInfo").innerHTML = results;
    }

    function searchFunctionInAllColumns(filterMethod=filterContainsUpper) {
        // Declare variables 
        var filter, tr, td, tds, i, txtValue;
        filter = searchInput.value;
        tr = table.getElementsByTagName("tr");
        
        let results = 0;
        // Loop through all table rows, and hide those who don't match the search query
        for (i = 1; i < tr.length; i++) {
            tds = tr[i].getElementsByTagName("td");
            tr[i].style.display = "none";
            
            for (p = 0; p < tds.length; p++){
                td = tds[p]
                if (td) {
                    txtValue = td.textContent || td.innerText;
                    if (filterMethod(txtValue, filter)) {
                        tr[i].style.display = "";
                        results += 1;
                        break;
                    }
                } 
            }
        }
        document.getElementById("searchNumberInfo").innerHTML = results;
    }

    function doSearch(){
        try{

            data_mode = fastSearchButton.getAttribute("data-mode");
            if (data_mode == "one"){
                num = parseInt(columns.now.getAttribute("data-col-number"))
                searchFunctionInColumn(num);
            } else {
                searchFunctionInAllColumns()
            }
        } catch (error){};
    }

    function setIconElement(element, icon){
        let i = element.getElementsByTagName("i")[0];
        i.innerHTML = icon
    }

    function configFastSearchSwitch(switchElement){
        try{
            if (switchElement != null){
                switchElement.addEventListener("click", function (){
                    searchInput.value = "";
                    let element = document.getElementById("fast_search_section")
                    element.classList.toggle("no-display")
                    if (element.classList.contains("no-display")){
                        setIconElement(switchElement, 'search')
                    } else {
                        setIconElement(switchElement, 'search_off')
                    }
                    doSearch();
                });
            }
        } catch(error){

        }
    }

    try{
        searchInput.addEventListener("keyup", doSearch);
        fastSearchButton.addEventListener("click", function (){

            data_mode = fastSearchButton.getAttribute("data-mode");
            if (data_mode == "one"){
                fastSearchButton.setAttribute("data-tooltip", "Buscar en todos")
                fastSearchButton.setAttribute("data-mode", "all")
                setIcon(fastSearchButton, "filter_9_plus");
            } else {
                fastSearchButton.setAttribute("data-tooltip", "Buscar en la columna seleccionada")
                fastSearchButton.setAttribute("data-mode", "one")
                setIcon(fastSearchButton, "filter_1");
            }
            doSearch();
        });

        configFastSearchSwitch(fastSearchSwitch);
        configFastSearchSwitch(fastSearchSwitchNavBar);
        
    } catch (error){};

    /*fastSearchButton.addEventListener("click", function () {
        searchInput.classList.toggle("no-display");
    })*/
}