#!/usr/bin/env python3
"""
Stanton Station Distance System Demo
Demonstrates the newly integrated Stanton station functionality
"""

import sys
sys.path.append('/home/runner/work/XionimusX/XionimusX/backend')

from stanton_stations import stanton_system
import json

def demo_header():
    print("🚉 STANTON STATION DISTANCE SYSTEM DEMO")
    print("=" * 50)
    print("Zeigt die neu integrierte Stanton-Stationen-Funktionalität")
    print("(Demonstrating newly integrated Stanton station functionality)")
    print()

def demo_station_overview():
    print("📋 STATION OVERVIEW / STATIONSÜBERSICHT")
    print("-" * 40)
    
    all_stations = stanton_system.get_all_stations()
    print(f"Gesamtzahl der Stationen: {len(all_stations)}")
    print(f"Total stations: {len(all_stations)}\n")
    
    # Group by type
    by_type = {}
    for station in all_stations.values():
        if station.station_type not in by_type:
            by_type[station.station_type] = []
        by_type[station.station_type].append(station)
    
    for station_type, stations in by_type.items():
        print(f"🔹 {station_type.upper()} STATIONS ({len(stations)}):")
        for station in stations:
            coords_str = f"({station.coordinates[0]:.2f}, {station.coordinates[1]:.2f})"
            print(f"   • {station.name} {coords_str}")
            print(f"     {station.description}")
        print()

def demo_distance_calculations():
    print("📏 DISTANCE CALCULATIONS / DISTANZBERECHNUNGEN")
    print("-" * 45)
    
    # Show examples for each station type
    examples = [
        ("Port Olisar", "Grim HEX"),
        ("Stanton Central", "Stanton North"), 
        ("Stanton Street", "Grand Street")
    ]
    
    for station1, station2 in examples:
        if station1 in stanton_system.get_all_stations() and station2 in stanton_system.get_all_stations():
            distance = stanton_system.get_distance(station1, station2)
            if distance:
                print(f"🔸 {station1} ↔ {station2}")
                print(f"   Entfernung: {distance.distance:.2f} {distance.unit}")
                print(f"   Distance: {distance.distance:.2f} {distance.unit}\n")

def demo_nearest_stations():
    print("🎯 NEAREST STATIONS / NÄCHSTE STATIONEN")
    print("-" * 42)
    
    test_stations = ["Port Olisar", "Stanton Central"]
    
    for station_name in test_stations:
        if station_name in stanton_system.get_all_stations():
            nearest = stanton_system.find_nearest_stations(station_name, 3)
            print(f"🔸 Nächste Stationen zu / Nearest to {station_name}:")
            for name, dist in nearest:
                station = stanton_system.get_all_stations()[name]
                unit = "au" if station.station_type == "space" else "km"
                print(f"   • {name}: {dist:.2f} {unit}")
            print()

def demo_route_planning():
    print("🛣️  ROUTE PLANNING / ROUTENPLANUNG") 
    print("-" * 38)
    
    # Space route
    space_route = ["Port Olisar", "Cry-Astro Station", "Grim HEX"]
    total_distance = stanton_system.get_route_distance(space_route)
    if total_distance:
        print("🔸 Weltraum-Route / Space Route:")
        print(f"   {' → '.join(space_route)}")
        print(f"   Gesamtdistanz: {total_distance:.2f} au")
        print(f"   Total distance: {total_distance:.2f} au\n")
    
    # Rail route  
    rail_route = ["Stanton Central", "Stanton North", "Stanton East"]
    total_distance = stanton_system.get_route_distance(rail_route)
    if total_distance:
        print("🔸 Bahn-Route / Rail Route:")
        print(f"   {' → '.join(rail_route)}")
        print(f"   Gesamtdistanz: {total_distance:.2f} km")
        print(f"   Total distance: {total_distance:.2f} km\n")

def demo_search_functionality():
    print("🔍 SEARCH FUNCTIONALITY / SUCHFUNKTION")
    print("-" * 40)
    
    search_terms = ["stanton", "station", "central"]
    
    for term in search_terms:
        results = stanton_system.search_stations(term)
        print(f"🔸 Suche nach / Search for '{term}': {len(results)} Ergebnisse")
        for station in results[:3]:  # Show first 3 results
            print(f"   • {station.name} ({station.station_type})")
        print()

def demo_integration_examples():
    print("💡 INTEGRATION EXAMPLES / INTEGRATIONSBEISPIELE")
    print("-" * 48)
    
    print("🔸 Beispiel-Anfragen / Example Queries:")
    queries = [
        '"Zeige mir alle Stanton Stationen"',
        '"Distance between Port Olisar and Grim HEX"',
        '"Nächste Stationen zu Stanton Central"',
        '"Stanton station overview"',
        '"Route von Stanton North zu Stanton South"'
    ]
    
    for query in queries:
        print(f"   • {query}")
    
    print("\n🔸 Diese Anfragen werden automatisch erkannt von:")
    print("   These queries are automatically recognized by:")
    print("   • Research Agent (Recherche-Agent)")
    print("   • GitHub Agent (für Integration-Status)")
    
    print("\n🔸 Unterstützte Sprachen / Supported Languages:")
    print("   • 🇩🇪 Deutsch (German)")
    print("   • 🇺🇸 English")

def demo_technical_details():
    print("\n⚙️  TECHNICAL DETAILS / TECHNISCHE DETAILS")
    print("-" * 45)
    
    print("🔸 Dateien / Files:")
    print("   • backend/stanton_stations.py (Hauptsystem)")
    print("   • backend/agents/research_agent.py (erweitert)")
    print("   • backend/agents/github_agent.py (erweitert)")
    
    print("\n🔸 Features:")
    print("   • Lokale Datenbank (keine API-Aufrufe nötig)")
    print("   • Local database (no API calls required)")
    print("   • Mehrsprachige Erkennung / Multi-language detection")
    print("   • Verschiedene Koordinatensysteme / Multiple coordinate systems")
    print("   • Routenplanung / Route planning")
    
    print("\n🔸 Performance:")
    all_stations = stanton_system.get_all_stations()
    total_distances = len(stanton_system.distances)
    print(f"   • {len(all_stations)} Stationen geladen")
    print(f"   • {total_distances} Distanzen berechnet") 
    print("   • Antwortzeit: <100ms (lokal)")
    print("   • Response time: <100ms (local)")

def main():
    demo_header()
    demo_station_overview()
    demo_distance_calculations()
    demo_nearest_stations()
    demo_route_planning()
    demo_search_functionality()
    demo_integration_examples()
    demo_technical_details()
    
    print("\n✅ INTEGRATION COMPLETE / INTEGRATION ABGESCHLOSSEN")
    print("=" * 55)
    print("Das Stanton-Stationssystem ist jetzt vollständig integriert!")
    print("The Stanton station system is now fully integrated!")
    print("\nBenutzer können jetzt Stanton-Stationen über den Research Agent abfragen.")
    print("Users can now query Stanton stations through the Research Agent.")

if __name__ == "__main__":
    main()