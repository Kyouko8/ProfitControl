document.addEventListener('DOMContentLoaded', function() {
    M.updateTextFields();
    
    const dropdown = document.querySelectorAll('.dropdown-trigger');
    const dropdown_instance = M.Dropdown.init(dropdown, {
        constrainWidth: false,
        coverTrigger: false,
    });

    const sidenav = document.querySelectorAll('.sidenav');
    const sidenav_instance = M.Sidenav.init(sidenav);

    const select = document.querySelectorAll('select');
    const select_instance = M.FormSelect.init(select);

    const collapsible = document.querySelectorAll('.collapsible');
    const collapsible_instance = M.Collapsible.init(collapsible, {
        accordion: false
    });

    const modals = document.querySelectorAll('.modal');
    const modals_instance = M.Modal.init(modals);

    const tooltippeds = document.querySelectorAll('.tooltipped');
    const tooltippeds_intances = M.Tooltip.init(tooltippeds);

    const fixed_action_btn = document.querySelectorAll('.fixed-action-btn');
    const fixed_action_btn_instance = M.FloatingActionButton.init(fixed_action_btn);

    const datepicker = document.querySelectorAll('.datepicker');
    const datepicker_instance = M.Datepicker.init(datepicker, { 
        firstDay: 0, 
        format: 'dd/mm/yyyy',
        showClearBtn: true,
        i18n: {
            clear: 'Quitar',
            cancel: 'Cancelar',
            done: 'Aceptar',
            months: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
            monthsShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"],
            weekdays: ["Domingo","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
            weekdaysShort: ["Dom","Lun", "Mar", "Mie", "Jue", "Vie", "Sab"],
            weekdaysAbbrev: ["D","L", "M", "X", "J", "V", "S"]
        },
        
        /* DYLAN: ESTO ES PARA SOLUCIONAR UN ERROR EN workday/list.html -> SearchSystem -> Modal */
        container: 'body' // this will append to body
    });

    const slider = document.querySelectorAll('.slider');
    const slider_instance = M.Slider.init(slider, {
        indicators: false,
        height: 600
    });

    $('.tooltipped-click').click(function() {
        let instance = M.Tooltip.getInstance(this);
        if (instance == null){
            $(this).tooltip({"delay": 50});
            $(this).tooltip('open');

        } else {
            if (instance.isOpen){
                $(this).tooltip('close');
            } else {
                $(this).tooltip({"delay": 50});
                $(this).tooltip('open');
            }
        }
    });
          
    $('.tooltipped-click').mouseleave(function() {
        let instance = M.Tooltip.getInstance(this);
        if (instance != null){
            $(this).tooltip('close');
            setTimeout(() => destroyTooltip(this), 550)
        }
    });

    function destroyTooltip(element){
        let instance = M.Tooltip.getInstance(element);
        if (instance != null){
            if (!instance.isOpen){
                $(element).tooltip('destroy');
            } 
        }
    }


});