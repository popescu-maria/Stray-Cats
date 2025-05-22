let map;
let heatmap;
let infoWindow;
let markers = {};

function buildInfoWindowContent(catData) {
    let content = `
        <div class="info-window-content">
            <h4>${catData.nume || 'Pisică necunoscută'}</h4>
            ${catData.address ? `<p><strong>Adresă:</strong> ${catData.address}</p>` : ''}
            <p>Nevoi:</p>
            <div class="nevoi-checklist" data-cat-id="${catData.id}">
    `;

    if (catData.nevoi && catData.nevoi.length > 0) {
        catData.nevoi.forEach(nevoie => {
            const nevoiName = typeof nevoie.name === 'string' ? nevoie.name.replace('_', ' ') : 'N/A';
            const isChecked = nevoie.is_met_recently ? 'checked' : '';
            const isDisabled = nevoie.is_met_recently ? 'disabled' : '';

            content += `
                <div class="nevoi-checkbox-item">
                    <input type="checkbox" id="nevoi-${catData.id}-${nevoie.id}" value="${nevoie.id}" ${isChecked} ${isDisabled}>
                    <label for="nevoi-${catData.id}-${nevoie.id}">${nevoiName}</label>
                </div>
            `;
        });
    } else {
        content += `<p>Nicio nevoie specificată.</p>`;
    }
    content += `</div>`;

    // NEW: Add Adopt button if user is authenticated
    if (window.isUserAuthenticated) {
        content += `
            <button class="adopt-button" data-cat-id="${catData.id}">Adopt This Cat!</button>
        `;
    }

    content += `</div>`;
    return content;
}

function updateHeatmap() {
    const heatmapData = window.catLocations
        .filter(location => location.lat !== null && location.lng !== null && typeof location.lat === 'number' && typeof location.lng === 'number')
        .map(location => new google.maps.LatLng(location.lat, location.lng));

    if (heatmap) {
        heatmap.setMap(null);
    }

    if (heatmapData.length > 0) {
        heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatmapData,
            map: map,
            radius: 30,
            gradient: [
                'rgba(255, 240, 245, 0)',
                'rgba(255, 230, 235, 0.4)',
                'rgba(255, 220, 225, 0.6)',
                'rgba(255, 200, 210, 0.7)',
                'rgba(255, 170, 180, 0.8)',
                'rgba(255, 140, 150, 0.9)',
                'rgba(255, 110, 120, 0.95)',
                'rgba(255, 80, 90, 1)',
                'rgba(255, 0, 80, 1)'
            ],
            opacity: 0.8
        });
    } else {
        console.warn("No valid cat locations to display heatmap.");
    }
}


function initMap() {
    const defaultLocation = { lat: 44.4268, lng: 26.1025 };

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: defaultLocation,
        mapTypeId: 'roadmap'
    });

    infoWindow = new google.maps.InfoWindow();

    window.catLocations.forEach(cat => {
        if (cat.lat === null || cat.lng === null || typeof cat.lat !== 'number' || typeof cat.lng !== 'number') {
            console.warn(`Skipping marker for cat "${cat.nume}" (ID: ${cat.id}) due to invalid coordinates: lat=${cat.lat}, lng=${cat.lng}`);
            return;
        }

        const catLatLng = new google.maps.LatLng(cat.lat, cat.lng);

        const marker = new google.maps.Marker({
            position: catLatLng,
            map: map,
            title: cat.nume || 'Unknown Cat'
        });

        markers[cat.id] = marker;

        marker.addListener('click', () => {
            const content = buildInfoWindowContent(cat);
            infoWindow.setContent(content);
            infoWindow.open(map, marker);

            infoWindow.addListener('domready', () => {
                const adoptButton = infoWindow.getContent().querySelector('.adopt-button');
                if (adoptButton) {
                    adoptButton.addEventListener('click', async () => {
                        const catId = adoptButton.dataset.catId;
                        if (confirm(`Are you sure you want to adopt ${cat.nume}? This will remove them from the map.`)) {
                            try {
                                const response = await fetch('/adopt-cat', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ cat_id: parseInt(catId) })
                                });

                                const result = await response.json();

                                if (response.ok) {
                                    alert(result.message);
                                    infoWindow.close();
                                    markers[catId].setMap(null);
                                    delete markers[catId];

                                    window.catLocations = window.catLocations.filter(c => c.id !== parseInt(catId));

                                    updateHeatmap();
                                } else {
                                    alert("Error adopting cat: " + (result.message || "Unknown error."));
                                }
                            } catch (error) {
                                console.error("Network error during adoption:", error);
                                alert("Network error. Could not adopt cat.");
                            }
                        }
                    });
                }

                const form = document.querySelector(`.nevoi-checklist[data-cat-id="${cat.id}"]`);
                if (form) {
                    form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                        if (!checkbox.disabled) {
                            checkbox.addEventListener('change', async (event) => {
                                const changedCheckbox = event.target;
                                const nevoiId = changedCheckbox.value;
                                const catId = form.dataset.catId;

                                if (changedCheckbox.checked) {
                                    try {
                                        const response = await fetch('/check-need', {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json'
                                            },
                                            body: JSON.stringify({
                                                cat_id: parseInt(catId),
                                                nevoi_id: parseInt(nevoiId)
                                            })
                                        });

                                        const result = await response.json();

                                        if (result.success) {
                                            changedCheckbox.disabled = true;
                                            console.log(result.message);
                                            const catIndex = window.catLocations.findIndex(c => c.id === parseInt(catId));
                                            if (catIndex !== -1) {
                                                const nevoiIndex = window.catLocations[catIndex].nevoi.findIndex(n => n.id === parseInt(nevoiId));
                                                if (nevoiIndex !== -1) {
                                                    window.catLocations[catIndex].nevoi[nevoiIndex].is_met_recently = true;
                                                }
                                            }
                                        } else {
                                            changedCheckbox.checked = false;
                                            console.error("Error marking need as met:", result.message);
                                            alert("Eroare la marcarea nevoii: " + result.message);
                                        }
                                    } catch (error) {
                                        changedCheckbox.checked = false;
                                        console.error("Network error:", error);
                                        alert("Eroare de rețea la marcarea nevoii.");
                                    }
                                } else {
                                    changedCheckbox.checked = true;
                                    alert("Această nevoie a fost marcată ca îndeplinită și va rămâne așa pentru următoarele 24 de ore.");
                                }
                            });
                        }
                    });
                }
            });
        });
    });

    updateHeatmap();
}