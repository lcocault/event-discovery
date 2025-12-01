import React, { useEffect, useState } from "react";
import EventMap from "./EventMap";
import { fetchEvents } from "../api/eventsApi";
import { Event } from "../models/eventModel";
import "leaflet/dist/leaflet.css";
import EventList from "./EventList";

const DEFAULT_POSITION = { latitude: 43.6, longitude: 1.44, zoom: 13 };

function App() {
  const [events, setEvents] = useState([]);
  const [position, setPosition] = useState(DEFAULT_POSITION);

  useEffect(() => {
    fetchEvents(position)
      .then((data) => setEvents(data.map(Event.fromApiResponse)))
      .catch(() => setEvents([]));
  }, [position]);

  const handleEventClick = (event) => {
    console.info("handleEventClick triggered with event:", event);
    setPosition({
      latitude: event.latitude,
      longitude: event.longitude,
      zoom: event.zoom || 17,
    });
  };

  console.info("Passing position to EventMap:", position);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ flex: 1 }}>
        <EventMap
          events={events}
          position={position}
          onRefresh={setPosition}
        />
      </div>
      <div style={{ height: "50%" }}>
        <EventList events={events} center={position} onEventClick={handleEventClick} />
      </div>
    </div>
  );
}

export default App;