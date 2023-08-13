document.addEventListener('DOMContentLoaded', function() {



    placeSelect.addEventListener('change', function() {
        const selectedValue = placeSelect.value;
        let checkboxesToCheck = [];
        let checkboxesToUncheck = [];
        const allCheckboxes = ['place-select', 'fires-checkbox', 'bladed_weapons-checkbox', 'stabbing-checkbox',
        'handgun-checkbox', 'long_gun-checkbox', 'brandishing-checkbox', 'dog_aggression-checkbox',
        'car_accident-checkbox', 'brawls-checkbox', 'injured_people-checkbox']

        function setCheckboxStates(checkArray, uncheckArray, check) {
            checkArray.forEach(checkboxId => {
                const checkbox = document.getElementById(checkboxId);
                checkbox.checked = check;
            });
            
            allCheckboxes.forEach(checkboxId => {
                if (checkArray in checkboxId == true) { // Si 
                    // Si algo de allCheckboxes no esta en checkArray entonces lo ponemos en false
                }
            });

            uncheckArray.forEach(checkboxId => {
                const checkbox = document.getElementById(checkboxId);
                checkbox.checked = !check;
            });
        }


        switch(selectedValue) {
            case 'home':
                checkboxesToCheck = ['fires-checkbox', 'injured_people-checkbox', 'dog_aggression-checkbox']
                break;
            case 'building':
                console.log("Ha elegido edificio");
                break; 
            case 'square':
                break;
            case 'street':
                break;
    const placeSelect =  document.getElementById('place-select');
    const firesCheckbox = document.getElementById('fires-checkbox');
    const bladedWeaponsCheckbox = document.getElementById('bladed_weapons-checkbox');
    const stabbingCheckbox = document.getElementById('stabbing-checkbox');
    const handgunCheckbox = document.getElementById('handgun-checkbox');
    const longGunCheckbox = document.getElementById('long_gun-checkbox');
    const brandishingCheckbox = document.getElementById('brandishing-checkbox');
    const dogAggressionCheckbox = document.getElementById('dog_aggression-checkbox');
    const carAccidentCheckbox = document.getElementById('car_accident-checkbox');
    const brawlsCheckbox = document.getElementById('brawls-checkbox');
    const injuredPeopleCheckbox = document.getElementById('injured_people-checkbox');

            
        }
    });
});