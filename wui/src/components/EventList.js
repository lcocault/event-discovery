import React from "react";

function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of the Earth in kilometers
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export default function EventList({ events, center }) {
  return (
    <div style={{
      position: "relative",
      width: "100%",
      height: "100%", /* Adjusted to occupy the full lower half */
      background: "white",
      overflowY: "auto",
      borderTop: "1px solid #ccc",
      boxShadow: "0 -2px 5px rgba(0,0,0,0.3)",
      zIndex: 1000,
      padding: "10px"
    }}>
      <h2>Nearest Events</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {events.map((evt) => (
          <li key={evt.id} style={{ marginBottom: 10 }}>
            <b>{evt.name}</b>
            <br />
            {evt.startTime} - {evt.endTime}
            <br />
            Distance: {calculateDistance(center.latitude, center.longitude, evt.latitude, evt.longitude).toFixed(2)} km
          </li>
        ))}
      </ul>
    </div>
  );
}