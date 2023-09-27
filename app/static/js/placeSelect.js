function emptyCheckBox(idValues) {
    let alert;
    for (let i = 0; i < idValues.length; i++) {
        alert = document.getElementById(idValues[i]);
        alert.checked = false;
    }
}
function setTruePlaces(idValues, setToTrueValues) {
    let alert;
    for (let i = 0; i < idValues.length; i++) {
        alert = document.getElementById(idValues[i]);
        if (setToTrueValues.includes(idValues[i])) {
            alert.checked = true;
        }
        else {
            alert.checked = false;
        }
    }
}
document.addEventListener('DOMContentLoaded', function() {
    const placeSelect = document.getElementById('place-select')
    let allIdCheckBox = ['fires-checkbox', 'bladed_weapons-checkbox', 'handgun-checkbox',
    'long_gun-checkbox', 'brandishing-checkbox', 'dog_aggression-checkbox', 
    'car_accident-checkbox', 'brawls-checkbox', 'injured_people-checkbox'];

    let buildingValues = ['fires-checkbox', 'brawls-checkbox', 'injured_people-checkbox'];

    let homeValues = ['fires-checkbox', 'dog_aggression-checkbox', 'injured_people-checkbox'];

    let squareValues = ['injured_people-checkbox', 'brawls-checkbox', 'brandishing-checkbox', 
                        'fires-checkbox', 'dog_aggression-checkbox']

    let streetValues = ['injured_people-checkbox', 'brawls-checkbox', 'brandishing-checkbox', 
                        'fires-checkbox', 'dog_aggression-checkbox', 'handgun-checkbox',
                        'long_gun-checkbox', 'car_accident-checkbox']
    placeSelect.addEventListener('change', function() {
       let placeSelectValue = placeSelect.value;
        switch (placeSelectValue) {
            case 'personalized':
                emptyCheckBox(allIdCheckBox);
                break
            case 'home':
                setTruePlaces(allIdCheckBox, homeValues);
                break;
            case 'building':
                setTruePlaces(allIdCheckBox, buildingValues);
                break;
            case 'square':
                setTruePlaces(allIdCheckBox, squareValues);
                break;
            case 'street':
                setTruePlaces(allIdCheckBox, streetValues);
                break;
        }
    });
    
});
