import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
from typing import List
from models.event import Event
from models.family import Family
from models.person import Person
from models.location import LocationType


class EventGenerator:
    def _generate_show_events(self, person, family, day_in_year, day_in_week):
        """
        Generate show (cinema, theatre, concert, etc.) events for a person based on their family's social category.
        Farmers = 0%, Artisans = 1%, Employees/Workers = 3%, Inactive/Retirees = 5%, Others = 10%.
        Retirees/Inactive can go anytime, others go in the evening (19-22).
        """
        import random
        from models.person import SocialCategory

        if not family or not family.social_category:
            return
        cat = family.social_category
        # Probabilities per day
        if cat == SocialCategory.FARMERS:
            prob = 0.0
        elif cat == SocialCategory.ARTISANS_MERCHANTS_ENTREPRENEURS:
            prob = 0.01
        elif cat in (SocialCategory.EMPLOYEES, SocialCategory.WORKERS):
            prob = 0.03
        elif cat in (SocialCategory.INACTIVE, SocialCategory.RETIREES):
            prob = 0.05
        else:
            prob = 0.10
        if random.random() < prob:
            # Pick a show type and time
            show_types = ["CINEMA", "THEATRE", "MUSIC_VENUE"]
            show_type = random.choice(show_types)
            # Retirees/Inactive: any time slot, others: evening
            if cat in (SocialCategory.INACTIVE, SocialCategory.RETIREES):
                time_slot = random.choice(list(range(10, 22)))
            else:
                time_slot = random.choice([19, 20, 21, 22])
            # Find nearest show location from home
            pos = family.home_position if family.home_position else None
            show_loc = self._find_nearest_location(pos, show_type) if pos else None
            if show_loc:
                self.events.append(
                    Event(
                        person_id=person.person_id,
                        day_in_year=day_in_year,
                        day_in_week=day_in_week,
                        time_slot=time_slot,
                        location=show_loc.position,
                    )
                )

    """
    Generates daily activity events for each member of a family over one year.
    """

    def __init__(self, families: List[Family], location_repository=None):
        self.families = families
        self.events: List[Event] = []
        self.location_repository = location_repository

    def generate_events(self):
        start_date = datetime(datetime.now().year, 1, 6)  # Jan 6, 2025 is a Monday
        for day_offset in range(31):
            date = start_date + timedelta(days=day_offset)
            day_in_year = date.timetuple().tm_yday
            day_in_week = date.weekday()  # 0=Monday
            for family in self.families:
                for person in family.parents + family.children:
                    self._generate_base_events(person, day_in_year, day_in_week)
                    self._generate_bar_events(person, family, day_in_year, day_in_week)
                    self._generate_religious_events(
                        person, family, day_in_year, day_in_week
                    )
                    self._generate_show_events(person, family, day_in_year, day_in_week)

    def _generate_base_events(self, person, day_in_year, day_in_week):
        for time_slot in range(24):
            location = self._determine_location(person, day_in_week, time_slot)
            event = Event(
                person_id=person.person_id,
                day_in_year=day_in_year,
                day_in_week=day_in_week,
                time_slot=time_slot,
                location=location,
            )
            self.events.append(event)

    def _find_nearest_location(self, position, loc_type_str):
        if not self.location_repository or not position:
            return None
        # Map string to LocationType
        try:
            loc_type = getattr(LocationType, loc_type_str)
        except AttributeError:
            # Try lower-case match (for e.g. 'CHURCH' not in enum)
            loc_type = None
            for t in LocationType:
                if t.name == loc_type_str or t.value.upper() == loc_type_str.upper():
                    loc_type = t
                    break
        if not loc_type:
            return None
        # Find nearest location of this type
        candidates = self.location_repository.get_locations_by_type(loc_type)
        if not candidates:
            print(f"[DEBUG] No candidates found for location type {loc_type_str}")
            return None

        # Find the closest by Euclidean distance
        def dist(loc):
            return (
                (loc.position.latitude - position.latitude) ** 2
                + (loc.position.longitude - position.longitude) ** 2
            ) ** 0.5

        nearest = min(candidates, key=dist)
        min_dist = dist(nearest)
        print(
            f"[DEBUG] Nearest {loc_type_str} to ({position.latitude}, {position.longitude}) is '{getattr(nearest, 'name', None)}' at ({nearest.position.latitude}, {nearest.position.longitude}) with distance {min_dist:.4f} degrees (~{min_dist*111:.2f} km)"
        )
        return nearest

    def _generate_bar_events(self, person, family, day_in_year, day_in_week):
        # Students aged 18+ go to nearest bar after school (assume after 16:00)
        # If you want to use social_category for bar logic, use family.social_category
        if person.is_student and person.is_adult:
            if day_in_week < 5:  # Mon-Fri
                bar = self._find_nearest_location(
                    person.school_location.position, "BAR"
                )
                if bar:
                    self.events.append(
                        Event(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=17,
                            location=bar.position,
                        )
                    )

    def _generate_religious_events(self, person, family, day_in_year, day_in_week):
        import random

        religiosity = getattr(family, "religiosity", None)
        church = self._find_nearest_location(family.home_position, "CHURCH")
        if religiosity:
            if religiosity.name == "VERY_RELIGIOUS":
                # Weekdays + Saturday at 19:00
                if day_in_week < 6:
                    if church:
                        self.events.append(
                            Event(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=19,
                                location=church.position,
                            )
                        )
                # Sunday at 11:00
                if day_in_week == 6:
                    if church:
                        self.events.append(
                            Event(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )
            elif religiosity.name == "MODERATE_RELIGIOUS":
                # Every Sunday at 11:00
                if day_in_week == 6 and church:
                    self.events.append(
                        Event(
                            person_id=person.person_id,
                            day_in_year=day_in_year,
                            day_in_week=day_in_week,
                            time_slot=11,
                            location=church.position,
                        )
                    )
            elif religiosity.name == "OCCASIONAL_RELIGIOUS":
                # One Sunday out of 6
                if day_in_week == 6 and church:
                    if random.randint(1, 6) == 1:
                        self.events.append(
                            Event(
                                person_id=person.person_id,
                                day_in_year=day_in_year,
                                day_in_week=day_in_week,
                                time_slot=11,
                                location=church.position,
                            )
                        )

    def _determine_location(self, person: Person, day_in_week: int, time_slot: int):
        # Always return a Position object; fallback to home if needed
        pos = None
        # Night hours: 0-6, always at home
        if 0 <= time_slot <= 6:
            if person.family and person.family.home_position:
                pos = person.family.home_position
        # School hours: 8-16, Mon-Fri, children
        elif (
            person.is_child
            and person.school_location
            and day_in_week < 5
            and 8 <= time_slot <= 16
        ):
            if getattr(person.school_location, "position", None):
                pos = person.school_location.position
        # Work hours: 8-17, Mon-Fri, adults
        elif (
            person.is_adult
            and person.work_location
            and day_in_week < 5
            and 8 <= time_slot <= 17
        ):
            if getattr(person.work_location, "position", None):
                pos = person.work_location.position
        # Otherwise, home
        elif person.family and person.family.home_position:
            pos = person.family.home_position
        # Fallback: always use home position if nothing else
        if pos is None and person.family and person.family.home_position:
            pos = person.family.home_position
        return pos

    def save_events(self, path: str):
        # Save events to GeoParquet using geopandas
        records = []
        for event in self.events:
            if event.location:
                geometry = Point(event.location.longitude, event.location.latitude)
            else:
                geometry = None
            records.append(
                {
                    "person_id": event.person_id,
                    "day_in_year": event.day_in_year,
                    "day_in_week": event.day_in_week,
                    "time_slot": event.time_slot,
                    "geometry": geometry,
                }
            )
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs="EPSG:4326")
        gdf.to_parquet(path, engine="pyarrow")
