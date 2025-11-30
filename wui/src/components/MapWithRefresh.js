import React, { useRef } from "react";
import { MapContainer, TileLayer, Circle, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapWithRefresh({ events, position, onRefresh }) {
  const mapRef = useRef();

  function handleRefresh() {
    const map = mapRef.current;
    if (map) {
      const center = map.getCenter();
      onRefresh({ latitude: center.lat, longitude: center.lng });
    }
  }

  function SetMapRef() {
    const map = useMap();
    mapRef.current = map;
    return null;
  }

  return (
    <div style={{ position: "relative", height: "100%", width: "100%" }}>
      <button
        onClick={handleRefresh}
        style={{ position: "absolute", top: 10, right: 10, zIndex: 1000 }}
      >
        Refresh
      </button>
      <MapContainer
        center={[position.latitude, position.longitude]}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <SetMapRef />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
          maxZoom={19}
        />
        {events.map((evt) => (
          <Circle
            key={evt.id}
            center={[evt.latitude, evt.longitude]}
            radius={10}
            pathOptions={{ color: "#1976d2", fillColor: "#1976d2", fillOpacity: 0.7 }}
          >
            <Popup>
              <b>{evt.name}</b>
              <br />
              {evt.startTime} - {evt.endTime}
            </Popup>
          </Circle>
        ))}
      </MapContainer>
    </div>
  );
}