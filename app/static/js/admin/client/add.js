document.addEventListener('DOMContentLoaded', function() {
    /* OPTIONAL FIELDS SYSTEM */
    const form_section = document.querySelector("#form-optional-fields");
    const btn_optional_fields = document.querySelector("#optional_fields_btn");
    const optional_fields_icon = document.querySelector("#optional_fields_btn .material-icons")

    btn_optional_fields.addEventListener("click", function () {

        if (form_section.classList.contains("no-display")){
            form_section.classList.remove("no-display")
            optional_fields_icon.innerHTML = "expand_less"
            btn_optional_fields.setAttribute("data-tooltip", "Ocultar campos opcionales")
        } else {
            form_section.classList.add("no-display")
            optional_fields_icon.innerHTML = "expand_more"
            btn_optional_fields.setAttribute("data-tooltip", "Mostrar campos opcionales")
        }
    });
});