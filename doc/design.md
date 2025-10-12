# Architecture

## Workflow
The general workflow of the application is as follows:

```mermaid
graph TD
    OSM --> LOC_EXT[Location Extractor]
    LOC_EXT --Location--> LOC_DB[(Locations)]
    LOC_DB --Location--> LOC_REG[Location Registry]
    SIMULATOR[Data Simulator] <--Family--> FAM_DB[(Families)]
    SIMULATOR <--Position--> POS_DB[(Positions)]
    SIMULATOR <--Weather--> MTO_DB[(Weather)]
    SIMULATOR --Position </br> Current Weather--> POS_PROC[Position Processor]
    POS_SRC[Position Source] --Position--> POS_PROC
    LOC_REG --Location--> SIMULATOR
    LOC_REG --Location--> POS_PROC
    MTO_EXT --Current Weather--> POS_PROC
    POS_PROC --HistoryRecord--> HIS_REG[History Registry]
    HIS_REG <--History Record --> HIS_DB[(History)]
    LOC_REG -- Location --> EVT_EXT[Event Extractor]
    Web --> EVT_EXT
    EVT_EXT -- Event --> EVT_DB[(Events)]
    EVT_DB -- Event --> EVT_REG[Event Registry]
    HIS_REG -- History Record --> REC_ENG[Recommendation Engine]
    MTO_EXT -- Forecast --> REC_ENG
    EVT_REG -- Event --> REC_ENG
    SEARCH[User Search] -- Position --> REC_ENG
    REC_ENG -- Event --> SEARCH
```

## Concepts

### Position
A **Position** represents a geographic coordinate and its context in time and application usage. Since the system operates at the scale of a city, the precise location is not critical—positions are used mainly to represent the presence or movement of people within the city. A position includes:
- `latitude`: The north-south coordinate
- `longitude`: The east-west coordinate
- `person_id`: The unique identifier of the person (for movement)
- `date`, `horaire`: Date and time (for user-facing positions)

### Event
An **Event** represents an occurrence or activity associated with a specific time. Events are central to the application's purpose of discovering and recommending relevant happenings to users. Each event has:
- A unique identifier (`id`)
- A descriptive name (`name`)
- A start and end time (`start_time`, `end_time`)
- A type or category (`event_type`), such as religious service, class, meal, meeting, etc.
- Optional metadata, such as description, tags, or organizer information

### Weather
A **Weather** entity captures atmospheric conditions relevant to a specific time in the city. The system distinguishes between:
- **Current Weather**: Real-time meteorological data for the city.
- **Weather Forecast**: Predicted weather conditions for future time intervals.

The weather parameters used are:
- `clouds`: Cloud cover percentage or description
- `rain`: Precipitation amount or probability
- `temperature`: Air temperature in degrees Celsius

Weather data is sourced from external providers and linked to events and user activities to enhance recommendations and user experience.

### History Record
A **History Record** aggregates information about a person's presence at a specific location and time, along with the corresponding weather conditions. It combines:
- A **Position** (person, location, timestamp)
- The **Weather** at that time and place

This record enables the system to analyze user movement patterns and contextual factors, supporting personalized recommendations and insights.