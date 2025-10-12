# Architecture

## Workflow
The general workflow of the application is the following:
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
    LOC_REG -- Location --> POS_EXT[Position Extractor]
    Web --> POS_EXT
    POS_EXT -- Position --> POS_DB[(Positions)]
    POS_DB -- Position --> POS_REG[Position Registry]
    HIS_REG -- History Record --> REC_ENG[Recommendation Engine]
    MTO_EXT -- Forecast --> REC_ENG
    POS_REG -- Position --> REC_ENG
    SEARCH[User Search] -- Position --> REC_ENG
    REC_ENG -- Position --> SEARCH
```

## Concepts

### Location
A **Location** represents a real-world place of interest, such as a venue, institution, or business. Locations are central to the application's data model and are used for event assignment and recommendations. Each location has:
- A unique identifier (`id`)
- A name (`name`)
- A type (`location_type`), such as church, school, restaurant, work place, etc. (see `LocationType` enum)
- A geographic position (`position`), with latitude and longitude
- Optional opening hours and additional metadata (e.g., address, category, tags)

Locations are extracted from OpenStreetMap (OSM) and stored in the unified GeoJSON file. The `category` property in the GeoJSON reflects the original kind of extractor (e.g., church, entertainment, work, hospitality, educational).

### Position
A **Position** represents a geographic coordinate and its context in time and application usage. It is a central concept for both static locations and dynamic person movement. A position can be:
- The fixed location of a place (venue, institution, etc.)
- The dynamic position of a person at a specific time (i.e., a movement or activity)

A position includes:
- `latitude`: The north-south coordinate
- `longitude`: The east-west coordinate

When used for tracking, a position is enriched with temporal and contextual attributes:
- `person_id`: The unique identifier of the person (for movement)
- `date`, `horaire`: Date and time (for user-facing positions)
