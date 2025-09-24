"""
Stanton Station Distance Data
Module for handling station distance information and calculations
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class Station:
    """Represents a station with coordinates and metadata"""
    name: str
    coordinates: Tuple[float, float]  # (latitude, longitude) or (x, y)
    station_type: str  # "subway", "space", "rail", etc.
    description: Optional[str] = None
    
@dataclass
class StationDistance:
    """Represents distance between two stations"""
    from_station: str
    to_station: str
    distance: float
    unit: str = "km"  # km, miles, au (astronomical units for space)
    
class StantonStationSystem:
    """Manages Stanton station network and distance calculations"""
    
    def __init__(self):
        self.stations: Dict[str, Station] = {}
        self.distances: Dict[Tuple[str, str], StationDistance] = {}
        self._initialize_default_stations()
    
    def _initialize_default_stations(self):
        """Initialize with default Stanton station data"""
        
        # Star Citizen Stanton System stations (space stations)
        stanton_space_stations = [
            Station("Port Olisar", (0, 0), "space", "Primary space station around Crusader"),
            Station("Grim HEX", (-150, 200), "space", "Asteroid mining station"),
            Station("Kareah Security Station", (100, -180), "space", "Security post"),
            Station("Cry-Astro Station", (80, 150), "space", "Fuel and repair station"),
            Station("Covalex Shipping Hub", (-200, -100), "space", "Cargo transfer station")
        ]
        
        # NYC area Stanton-related stations
        nyc_stations = [
            Station("Stanton Street", (40.7218, -73.9883), "subway", "NYC subway station"),
            Station("Delancey St-Essex St", (40.7188, -73.9883), "subway", "Major NYC transit hub"),
            Station("Grand Street", (40.7186, -73.9939), "subway", "Nearby station")
        ]
        
        # Generic transit system
        generic_stations = [
            Station("Stanton Central", (52.5200, 13.4050), "rail", "Central station hub"),
            Station("Stanton North", (52.5400, 13.4000), "rail", "Northern terminal"),
            Station("Stanton South", (52.5000, 13.4100), "rail", "Southern terminal"),
            Station("Stanton East", (52.5200, 13.4250), "rail", "Eastern branch"),
            Station("Stanton West", (52.5200, 13.3850), "rail", "Western branch")
        ]
        
        # Add all stations
        all_stations = stanton_space_stations + nyc_stations + generic_stations
        for station in all_stations:
            self.stations[station.name] = station
        
        # Calculate distances between stations
        self._calculate_all_distances()
    
    def _calculate_all_distances(self):
        """Calculate distances between all stations"""
        station_names = list(self.stations.keys())
        
        for i, station1_name in enumerate(station_names):
            for station2_name in station_names[i+1:]:
                station1 = self.stations[station1_name]
                station2 = self.stations[station2_name]
                
                if station1.station_type == station2.station_type:
                    distance = self._calculate_distance(station1, station2)
                    distance_obj = StationDistance(
                        station1_name, 
                        station2_name, 
                        distance,
                        self._get_unit_for_type(station1.station_type)
                    )
                    
                    # Store both directions
                    self.distances[(station1_name, station2_name)] = distance_obj
                    self.distances[(station2_name, station1_name)] = distance_obj
    
    def _calculate_distance(self, station1: Station, station2: Station) -> float:
        """Calculate distance between two stations"""
        x1, y1 = station1.coordinates
        x2, y2 = station2.coordinates
        
        if station1.station_type == "subway" or station1.station_type == "rail":
            # Use Haversine formula for Earth coordinates
            return self._haversine_distance(x1, y1, x2, y2)
        else:
            # Use Euclidean distance for space or generic coordinates
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points on Earth using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _get_unit_for_type(self, station_type: str) -> str:
        """Get appropriate unit for station type"""
        if station_type in ["subway", "rail"]:
            return "km"
        elif station_type == "space":
            return "au"  # Astronomical units
        else:
            return "units"
    
    def get_distance(self, from_station: str, to_station: str) -> Optional[StationDistance]:
        """Get distance between two stations"""
        return self.distances.get((from_station, to_station))
    
    def get_all_stations(self) -> Dict[str, Station]:
        """Get all stations"""
        return self.stations
    
    def get_stations_by_type(self, station_type: str) -> Dict[str, Station]:
        """Get stations of a specific type"""
        return {name: station for name, station in self.stations.items() 
                if station.station_type == station_type}
    
    def find_nearest_stations(self, station_name: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Find nearest stations to a given station"""
        if station_name not in self.stations:
            return []
        
        source_station = self.stations[station_name]
        distances = []
        
        for name, station in self.stations.items():
            if name != station_name and station.station_type == source_station.station_type:
                distance_obj = self.get_distance(station_name, name)
                if distance_obj:
                    distances.append((name, distance_obj.distance))
        
        distances.sort(key=lambda x: x[1])
        return distances[:limit]
    
    def get_route_distance(self, stations: List[str]) -> Optional[float]:
        """Calculate total distance for a route through multiple stations"""
        if len(stations) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(stations) - 1):
            distance_obj = self.get_distance(stations[i], stations[i + 1])
            if distance_obj:
                total_distance += distance_obj.distance
            else:
                return None  # Route not possible
        
        return total_distance
    
    def search_stations(self, query: str) -> List[Station]:
        """Search stations by name or description"""
        query_lower = query.lower()
        results = []
        
        for station in self.stations.values():
            if (query_lower in station.name.lower() or 
                (station.description and query_lower in station.description.lower())):
                results.append(station)
        
        return results

# Initialize global instance
stanton_system = StantonStationSystem()