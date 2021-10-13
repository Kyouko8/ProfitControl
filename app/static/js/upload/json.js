
window.onload = () => {

    const condition_radio_buttons = document.getElementsByName("if_exists");
    const hidden_section = document.getElementById("customize_if_exists");

    for (var i = 0; i < condition_radio_buttons.length; i++) {
        condition_radio_buttons[i].addEventListener('change', function() {
            if (this.value == "0") {
                hidden_section.classList.remove("no-display")
            } else {
                hidden_section.classList.add("no-display")
            }
        });
    }

}
