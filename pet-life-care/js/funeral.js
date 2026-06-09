document.getElementById("findBtn").addEventListener("click", findFuneralHomes);

async function findFuneralHomes() {

    navigator.geolocation.getCurrentPosition(async (position) => {

        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;

        const response = await fetch("../data/funeral_home.csv");
        const csvText = await response.text();

        const lines = csvText.trim().split("\n");

        let homes = [];

        for(let i = 1; i < lines.length; i++) {

            const cols = lines[i].split(",");

            const home = {
                name: cols[0],
                address: cols[1],
                phone: cols[2],
                latitude: parseFloat(cols[3]),
                longitude: parseFloat(cols[4])
            };

            home.distance = getDistance(
                userLat,
                userLng,
                home.latitude,
                home.longitude
            );

            homes.push(home);
        }

        homes.sort((a,b) => a.distance - b.distance);

        let html = "";

        homes.forEach(home => {
            html += `
                <div>
                    <h3>${home.name}</h3>
                    <p>주소 : ${home.address}</p>
                    <p>전화번호 : ${home.phone}</p>
                    <p>거리 : ${home.distance.toFixed(2)} km</p>
                    <hr>
                </div>
            `;
        });

        document.getElementById("result").innerHTML = html;

    });
}

function getDistance(lat1, lon1, lat2, lon2) {

    const R = 6371;

    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}