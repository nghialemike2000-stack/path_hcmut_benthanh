(function(window) {
    const mapName = "__MAP_NAME__";
    const vertexCoords = __VERTEX_COORDS__;
    const edgeCoords = __EDGE_COORDS__;

    let currentEdge = null;

    function getMap() {
        return window[mapName];
    }

    function getVertexMarker(vertexId) {
        const map = getMap();
        const coords = vertexCoords[vertexId];

        if (!map || !coords) {
            return null;
        }

        let foundMarker = null;

        map.eachLayer(function(layer) {
            if (
                foundMarker !== null ||
                typeof layer.getLatLng !== "function" ||
                typeof layer.openPopup !== "function"
            ) {
                return;
            }

            const latLng = layer.getLatLng();

            if (
                Math.abs(latLng.lat - coords[0]) < 0.00000001 &&
                Math.abs(latLng.lng - coords[1]) < 0.00000001
            ) {
                foundMarker = layer;
            }
        });

        return foundMarker;
    }

    function focusVertex(vertexId) {
        const map = getMap();
        const coords = vertexCoords[vertexId];

        if (!map || !coords) {
            return;
        }

        map.setView(
            coords,
            18
        );

        const marker = getVertexMarker(vertexId);

        if (marker) {
            marker.openPopup();
        }
    }

    function focusEdge(coords) {
        const map = getMap();

        if (!map || !coords) {
            return;
        }

        if (currentEdge !== null) {
            map.removeLayer(currentEdge);
        }

        currentEdge = L.polyline(
            coords,
            {
                color: "red",
                weight: 6,
                opacity: 0.8,
                lineJoin: "round"
            }
        ).addTo(map);

        map.fitBounds(
            currentEdge.getBounds(),
            {padding: [50, 50]}
        );
    }

    function focusEdgeById(edgeId) {
        focusEdge(edgeCoords[edgeId]);
    }

    window.HcmutMapInteractions = {
        focusVertex: focusVertex,
        focusEdge: focusEdge,
        focusEdgeById: focusEdgeById
    };

    window.focusVertex = focusVertex;
    window.focusEdge = focusEdge;
})(window);

