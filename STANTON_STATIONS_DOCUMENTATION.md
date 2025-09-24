# Stanton Station Distance Integration

## Overview

This document describes the newly integrated Stanton Station Distance functionality in the XIONIMUS AI system. The integration allows users to query information about stations in the Stanton system, calculate distances between them, and perform route planning.

## Features

### 🚉 Station Types Supported
- **Space Stations**: Star Citizen Stanton system locations
- **Subway Stations**: NYC area Stanton-related stations  
- **Rail Stations**: Generic transit system stations

### 📏 Distance Calculations
- Automatic distance calculation between any two stations of the same type
- Support for different units (km, au, miles)
- Haversine formula for Earth-based coordinates
- Euclidean distance for space coordinates

### 🔍 Search Capabilities
- Search stations by name or description
- Find nearest stations to any given station
- Route planning through multiple stations
- Multi-language support (German/English)

## Usage Examples

### German Queries (Deutsch)
```
"Zeige mir alle Stanton Stationen"
"Distanzen zwischen Stanton Stationen"
"Nächste Stationen zu Port Olisar"
"Stanton Station Übersicht"
```

### English Queries
```
"Show me all Stanton stations"
"Distance between Stanton stations"  
"Nearest stations to Stanton Central"
"Stanton station overview"
```

## Technical Implementation

### Files Modified/Added
- `backend/stanton_stations.py` - Core station system and distance calculations
- `backend/agents/research_agent.py` - Enhanced with Stanton query handling
- `backend/agents/github_agent.py` - Added integration reporting

### Data Structure
```python
@dataclass
class Station:
    name: str
    coordinates: Tuple[float, float]
    station_type: str
    description: Optional[str] = None

@dataclass  
class StationDistance:
    from_station: str
    to_station: str
    distance: float
    unit: str = "km"
```

### Agent Integration
- Research Agent automatically detects Stanton station queries
- High confidence scoring (0.9-1.0) for station-related requests
- Offline capability using local station database
- No external API calls required for basic station information

## Station Database

### Space Stations (Star Citizen Stanton System)
- Port Olisar (Primary space station)
- Grim HEX (Asteroid mining station)
- Kareah Security Station (Security post)
- Cry-Astro Station (Fuel and repair)
- Covalex Shipping Hub (Cargo transfer)

### NYC Area Stations
- Stanton Street (NYC subway)
- Delancey St-Essex St (Transit hub)
- Grand Street (Nearby station)

### Generic Rail System
- Stanton Central (Hub station)
- Stanton North/South/East/West (Branch terminals)

## Query Processing

The system automatically:
1. Detects Stanton station queries using keyword matching
2. Determines query type (overview, distance, nearest, etc.)
3. Retrieves relevant data from local database
4. Formats response in requested language
5. Provides structured results with distances and metadata

## Performance

- **Fast Response**: Local database eliminates API latency
- **High Accuracy**: Precise distance calculations using appropriate formulas
- **Scalable**: Easy to add new stations and station types
- **Multilingual**: Supports German and English queries

## Future Enhancements

- Real-time transit data integration
- Route optimization algorithms
- Interactive station maps
- Additional station types (bus, tram, ferry)
- Live traffic/delay information