let map;
let marker;

const latitudeInput = document.getElementById('modalLatitude');
const longitudeInput = document.getElementById('modalLongitude');
const modal = document.getElementById('catFormModal');

function placeMarkerAndSetValue(location) {
    if (marker) {
        marker.setPosition(location);
    } else {
        marker = new google.maps.Marker({
            position: location,
            map: map,
            animation: google.maps.Animation.DROP
        });
    }
}

function openModal(lat, lng) {
    modal.style.display = 'flex';
    latitudeInput.value = lat;
    longitudeInput.value = lng;
    setupCheckboxButtons();
}

function closeModal() {
    modal.style.display = 'none';
    if (marker) {
        marker.setMap(null);
        marker = null;
    }
    document.getElementById('addCatForm').reset();
    const checkboxLabels = document.querySelectorAll('.checkbox-group label');
    checkboxLabels.forEach(label => {
        label.classList.remove('checked');
    });
}

window.onclick = function(event) {
    if (event.target == modal) {
        closeModal();
    }
}

function setupCheckboxButtons() {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        const label = document.querySelector(`label[for="${checkbox.id}"]`);
        if (label) {
            label.removeEventListener('click', handleCheckboxLabelClick);
            label.addEventListener('click', handleCheckboxLabelClick);

            if (checkbox.checked) {
                label.classList.add('checked');
            } else {
                label.classList.remove('checked');
            }
        }
    });
}

function handleCheckboxLabelClick(event) {
    event.preventDefault();

    const label = event.currentTarget;
    const checkboxId = label.getAttribute('for');
    const checkbox = document.getElementById(checkboxId);

    if (checkbox) {
        checkbox.checked = !checkbox.checked;

        if (checkbox.checked) {
            label.classList.add('checked');
        } else {
            label.classList.remove('checked');
        }
    }
}