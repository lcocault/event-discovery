import React, { useEffect, useState } from "react";
import MapWithRefresh from "./MapWithRefresh";
import "leaflet/dist/leaflet.css";

const API_URL = "http://localhost:2702/events/around";
const DEFAULT_POSITION = { latitude: 43.6, longitude: 1.44 };

function App() {
  const [events, setEvents] = useState([]);
  const [position, setPosition] = useState(DEFAULT_POSITION);

  function fetchEvents(pos) {
    const now = new Date().toISOString();
    fetch(
      `${API_URL}?latitude=${pos.latitude}&longitude=${pos.longitude}&time=${encodeURIComponent(now)}`
    )
      .then((res) => res.json())
      .then((data) => setEvents(data))
      .catch(() => setEvents([]));
  }

  useEffect(() => {
    fetchEvents(position);
  }, [position]);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ width: "30%", overflowY: "auto", borderRight: "1px solid #ccc" }}>
        <h2>Nearest Events</h2>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {events.map((evt) => (
            <li key={evt.id} style={{ marginBottom: 10 }}>
              <b>{evt.name}</b>
              <br />
              {evt.start_time} - {evt.end_time}
              <br />
              Lat: {evt.latitude}, Lon: {evt.longitude}
            </li>
          ))}
        </ul>
      </div>
      <div style={{ flex: 1 }}>
        <MapWithRefresh
          events={events}
          position={position}
          onRefresh={setPosition}
        />
      </div>
    </div>
  );
}

export default App;
