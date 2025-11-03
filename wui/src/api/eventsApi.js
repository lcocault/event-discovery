const API_URL = "http://localhost:3702/events/around";

export function fetchEvents(pos) {
  const now = new Date().toISOString();
  return fetch(
    `${API_URL}?latitude=${pos.latitude}&longitude=${pos.longitude}&time=${encodeURIComponent(now)}`
  ).then((res) => res.json());
}