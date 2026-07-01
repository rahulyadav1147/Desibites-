let map = L.map('map').setView([20.5937, 78.9629], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data © OpenStreetMap'
}).addTo(map);

let userMarker = L.marker([0, 0]).addTo(map);
let deliveryMarker = L.marker([0, 0]).addTo(map);

// Get current location
function sendLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {

            let role = document.getElementById("role").value;
            let lat = position.coords.latitude;
            let lng = position.coords.longitude;

            fetch("/update_location", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    role: role,
                    lat: lat,
                    lng: lng
                })
            });
        });
    }
}

// Fetch and show both locations
function updateMap() {
    fetch("/get_locations")
        .then(res => res.json())
        .then(data => {
            if (data.user) {
                userMarker.setLatLng([data.user.lat, data.user.lng])
                    .bindPopup("User").openPopup();
            }
            if (data.delivery) {
                deliveryMarker.setLatLng([data.delivery.lat, data.delivery.lng])
                    .bindPopup("Delivery Partner").openPopup();
            }
        });
}

// Update every 5 seconds
setInterval(sendLocation, 5000);
setInterval(updateMap, 5000);
