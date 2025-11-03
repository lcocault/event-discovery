import React from "react";
import "./EventList.css";

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

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function EventList({ events, center }) {
  const sortedEvents = [...events].sort((a, b) => {
    const distanceA = calculateDistance(center.latitude, center.longitude, a.latitude, a.longitude);
    const distanceB = calculateDistance(center.latitude, center.longitude, b.latitude, b.longitude);
    return distanceA - distanceB;
  });

  return (
    <div className="event-list">
      <h2>Nearest Events</h2>
      <ul>
        {sortedEvents.map((evt) => (
          <li key={evt.id}>
            <b>{evt.name}</b>
            <br />
            Open from {formatTime(evt.startTime)} to {formatTime(evt.endTime)}
            <br />
            Distance: {calculateDistance(center.latitude, center.longitude, evt.latitude, evt.longitude).toFixed(2)} km
          </li>
        ))}
      </ul>
    </div>
  );
}