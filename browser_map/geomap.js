// Load the tile images from OpenStreetMap
var mytiles = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
});
// Initialise an empty map
var map = L.map('map');
// Read the GeoJSON data with jQuery, and create a circleMarker element for each tweet
$.getJSON("./geojson/geo_data.json", function(data) {
    var myStyle = {
        radius: 3,
        fillColor: "red",
        color: "red",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    };

    var geojson = L.geoJson(data, {
        pointToLayer: function (feature, latlng) {
            var popupText = feature['properties']['text'];
            var popup_datetime = feature['properties']['created_at'];
            return L.circleMarker(latlng, myStyle).bindPopup(popupText + '\n' + popup_datetime);
        }
    });
    geojson.addTo(map)
});
// Add the tiles to the map, and initialise the view in the middle of Europe
map.addLayer(mytiles).setView([50.5, 5.0], 5);
