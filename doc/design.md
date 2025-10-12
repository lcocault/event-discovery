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

The following diagrams summarizes the concepts defined in this section:

```mermaid
erDiagram
    TIME_SLOT {
        long id  
        int year  
        int day_of_year  
        int hour  
        int day_of_week  
    }
    POSITION {
        string person_id
        float latitude
        float longitude
    }
    LOCATION {
        string id
        float latitude
        float longitude
        string name
        string type
    }
    EVENT {
        string id
        string name
        string event_type
        string location_id
    }
    WEATHER {
        float clouds
        float rain
        float temperature
    }
    HISTORY_RECORD {
        string id
    }

    EVENT }o--|| LOCATION : "occurs at"
    EVENT }|--|| TIME_SLOT : "starts at"
    EVENT }|--|| TIME_SLOT : "ends at"
    EVENT ||..|| WEATHER : "affected by"
    WEATHER ||--o{ HISTORY_RECORD : "is part of"
    HISTORY_RECORD }o--|| TIME_SLOT : "occurs at"
    HISTORY_RECORD }o--|| LOCATION : "is part of"
    POSITION }o--|| TIME_SLOT : "occurs at"
```

### Time slot
For the volumetry of the system to be supportable, the time is sliced in slots characterized by:
- A unique **identifier** composed of the three following attributes
- The **year**
- The **day** in year
- The **hour** in day
- The day in **week**

### Position
A **Position** represents a geographic coordinate and its context in time and application usage. Since the system operates at the scale of a city, the precise location is not critical—positions are used mainly to represent the presence or movement of people within the city. A position includes:
- `latitude`: The north-south coordinate
- `longitude`: The east-west coordinate
- `person_id`: The unique identifier of the person (for movement)
- `slot`: The time slot

### Location
A **Location** refers to a specific geographic point or area within the city, often associated with meaningful places such as buildings, parks, intersections, or venues. Locations provide semantic context to raw geographic coordinates, enabling the system to relate positions and events to recognizable places. Each location typically includes:
- `latitude` and `longitude`: The central coordinates of the location
- `name`: A human-readable identifier (e.g., "Central Park", "Library")
- `type`: The category of the location (e.g., park, school, restaurant)
- Optional metadata, such as address, description, or tags

Locations are extracted from external sources (e.g., OpenStreetMap) and maintained in a registry to support event association, user queries, and recommendation logic.

### Event
An **Event** represents an occurrence or activity associated with a specific time. Events are central to the application's purpose of discovering and recommending relevant happenings to users. Each event has:
- A unique identifier (`id`)
- A descriptive name (`name`)
- A location where the event occurs (`location`)
- A start and end time slots (`start_time`, `end_time`)
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
- A **Location**
- A **time slot**
- The **Weather** at that time and place

This record enables the system to analyze user movement patterns and contextual factors, supporting personalized recommendations and insights.