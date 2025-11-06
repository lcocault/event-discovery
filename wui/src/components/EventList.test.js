import React from "react";
import { render } from "@testing-library/react";
import EventList from "./EventList";

describe("EventList Component", () => {
  const mockEvents = [
    {
      id: 1,
      name: "Event 1",
      startTime: "2025-11-03T10:00:00Z",
      endTime: "2025-11-03T12:00:00Z",
      latitude: 48.8566,
      longitude: 2.3522,
    },
    {
      id: 2,
      name: "Event 2",
      startTime: "2025-11-03T14:00:00Z",
      endTime: "2025-11-03T16:00:00Z",
      latitude: 48.8567,
      longitude: 2.3523,
    },
  ];

  const mockCenter = {
    latitude: 48.8566,
    longitude: 2.3522,
  };

  it("renders the event list with formatted opening hours", () => {
    const { getByText } = render(<EventList events={mockEvents} center={mockCenter} />);

    expect(getByText("Event 1")).toBeInTheDocument();
    expect(getByText(/Open from 10:00 to 12:00/)).toBeInTheDocument();

    expect(getByText("Event 2")).toBeInTheDocument();
    expect(getByText(/Open from 14:00 to 16:00/)).toBeInTheDocument();
  });

  it("sorts events by distance", () => {
    const { container } = render(<EventList events={mockEvents} center={mockCenter} />);
    const listItems = container.querySelectorAll("li");

    expect(listItems[0]).toHaveTextContent("Event 1");
    expect(listItems[1]).toHaveTextContent("Event 2");
  });
});