document.addEventListener('DOMContentLoaded', () => {
    let expanded = false;
    const selectBox = document.querySelector('.selectBox');
    const checkboxes = document.getElementById("checkboxes");
    const container = document.querySelector('.multiselect');

    if (selectBox) {
        selectBox.addEventListener('click', (e) => {
            
            e.stopPropagation();
            
            if (!expanded) {
                checkboxes.style.display = "block";
                expanded = true;
            } else {
                checkboxes.style.display = "none";
                expanded = false;
            }
        });
    }

    
    if (checkboxes) {
        checkboxes.addEventListener('click', (e) => {
            e.stopPropagation(); 
        });
    }


    document.addEventListener('click', (e) => {
        if (expanded) {
            checkboxes.style.display = "none";
            expanded = false;
        }
    });
});
