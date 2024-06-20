function updateCheckboxes() {
    const place = document.getElementById('place-select').value;

    const fires = document.getElementById('fires');
    const bladed_weapon = document.getElementById('bladed_weapon');
    const handgun = document.getElementById('handgun');
    const long_gun = document.getElementById('long_gun');
    const cannoning = document.getElementById('cannoning');
    const car_accident = document.getElementById('car_accident');
    const dog_attack = document.getElementById('dog_attack');
    const brawls = document.getElementById('brawls');
    const injured_people = document.getElementById('injured_people');

    fires.checked = false;
    bladed_weapon.checked = false;
    handgun.checked = false;
    long_gun.checked = false;
    cannoning.checked = false;
    car_accident.checked = false;
    dog_attack.checked = false;
    brawls.checked = false;
    injured_people.checked = false;

    if (place === 'Home') {
        fires.checked = true;
        dog_attack.checked = true;
        injured_people.checked = true;
    } else if (place === 'Building') {
        fires.checked = true;
        brawls.checked = true;
        injured_people.checked = true;
    } else if (place === 'Square') {
        fires.checked = true;
        brawls.checked = true;
        cannoning.checked = true;
        dog_attack.checked = true;
        injured_people.checked = true;
    } else if (place === 'Street') {
        long_gun.checked = true;
        handgun.checked = true;
        brawls.checked = true;
        fires.checked = true;
        dog_attack.checked = true;
        injured_people.checked = true;
    }
}

function updatePlace() {
    const place = document.getElementById('place-select');
    if (place.value !== 'Personalized') {
        place.value = 'Personalized';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('place-select').addEventListener('change', updateCheckboxes);

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updatePlace);
    });

    updateCheckboxes(); 
});