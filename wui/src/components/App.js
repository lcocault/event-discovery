import React, { useEffect, useState } from "react";
import MapWithRefresh from "./MapWithRefresh";
import { fetchEvents } from "../api/eventsApi";
import { Event } from "../models/eventModel";
import "leaflet/dist/leaflet.css";
import EventList from "./EventList";

const DEFAULT_POSITION = { latitude: 43.6, longitude: 1.44 };

function App() {
  const [events, setEvents] = useState([]);
  const [position, setPosition] = useState(DEFAULT_POSITION);

  useEffect(() => {
    fetchEvents(position)
      .then((data) => setEvents(data.map(Event.fromApiResponse)))
      .catch(() => setEvents([]));
  }, [position]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ flex: 1 }}>
        <MapWithRefresh
          events={events}
          position={position}
          onRefresh={setPosition}
        />
      </div>
      <div style={{ height: "50%" }}>
        <EventList events={events} center={position} />
      </div>
    </div>
  );
}

export default App;