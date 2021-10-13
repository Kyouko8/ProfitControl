document.addEventListener('DOMContentLoaded', function() {
    /* SEARCH SYSTEM */
    const search_advanced_section = document.querySelector("#search-advanced");
    const btn_search_advanced = document.querySelector("#btnSearchAdvanced");
    const search_advanced_icon = document.querySelector("#btnSearchAdvanced .material-icons")

    btn_search_advanced.addEventListener("click", function () {

        if (search_advanced_section.classList.contains("no-display")){
            search_advanced_section.classList.remove("no-display")
            search_advanced_icon.innerHTML = "expand_less"
        } else {
            search_advanced_section.classList.add("no-display")
            search_advanced_icon.innerHTML = "expand_more"
        }
    });

});