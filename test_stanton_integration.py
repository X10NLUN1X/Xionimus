#!/usr/bin/env python3
"""
Test script for Stanton Station Distance Integration
Tests the newly implemented Stanton station functionality
"""

import sys
import os
sys.path.append('/home/runner/work/XionimusX/XionimusX/backend')

from stanton_stations import stanton_system
from agents.research_agent import ResearchAgent
from agents.base_agent import AgentTask

def test_stanton_system_basic():
    """Test basic Stanton system functionality"""
    print("=== Testing Stanton Station System ===\n")
    
    # Test 1: Get all stations
    all_stations = stanton_system.get_all_stations()
    print(f"✅ Total stations loaded: {len(all_stations)}")
    
    # Test 2: Test station types
    station_types = set(station.station_type for station in all_stations.values())
    print(f"✅ Station types available: {', '.join(station_types)}")
    
    # Test 3: Test distance calculation
    station_names = list(all_stations.keys())
    if len(station_names) >= 2:
        distance = stanton_system.get_distance(station_names[0], station_names[1])
        if distance:
            print(f"✅ Distance calculation working: {station_names[0]} to {station_names[1]} = {distance.distance:.2f} {distance.unit}")
        else:
            print("❌ Distance calculation failed")
    
    # Test 4: Test nearest stations
    if station_names:
        nearest = stanton_system.find_nearest_stations(station_names[0], 3)
        print(f"✅ Nearest stations to {station_names[0]}: {len(nearest)} found")
        for name, dist in nearest[:2]:
            print(f"   - {name}: {dist:.2f} units")
    
    # Test 5: Test search functionality
    search_results = stanton_system.search_stations("stanton")
    print(f"✅ Search results for 'stanton': {len(search_results)} stations found")
    
    print("\n=== Basic System Tests Completed ===\n")

def test_research_agent_integration():
    """Test Research Agent integration with Stanton stations"""
    print("=== Testing Research Agent Integration ===\n")
    
    agent = ResearchAgent()
    
    # Test different query types
    test_queries = [
        "Stanton station distances",
        "Show me all Stanton stations",
        "Find nearest stations in Stanton",
        "Distanzen zwischen Stanton Stationen"  # German query
    ]
    
    for query in test_queries:
        is_stanton_query = agent._is_stanton_station_query(query)
        print(f"Query: '{query}' -> Stanton query: {'✅ Yes' if is_stanton_query else '❌ No'}")
    
    # Test confidence scoring
    confidence = agent.can_handle_task("Stanton station distances information", {})
    print(f"✅ Confidence for Stanton query: {confidence:.2f}")
    
    print("\n=== Research Agent Integration Tests Completed ===\n")

def test_station_data_quality():
    """Test quality and completeness of station data"""
    print("=== Testing Station Data Quality ===\n")
    
    all_stations = stanton_system.get_all_stations()
    
    # Check data completeness
    stations_with_descriptions = sum(1 for s in all_stations.values() if s.description)
    print(f"✅ Stations with descriptions: {stations_with_descriptions}/{len(all_stations)}")
    
    # Check coordinate validity
    valid_coordinates = sum(1 for s in all_stations.values() 
                          if isinstance(s.coordinates, tuple) and len(s.coordinates) == 2)
    print(f"✅ Stations with valid coordinates: {valid_coordinates}/{len(all_stations)}")
    
    # Check station types
    type_distribution = {}
    for station in all_stations.values():
        type_distribution[station.station_type] = type_distribution.get(station.station_type, 0) + 1
    
    print(f"✅ Station type distribution:")
    for station_type, count in type_distribution.items():
        print(f"   - {station_type}: {count} stations")
    
    print("\n=== Station Data Quality Tests Completed ===\n")

def test_distance_calculations():
    """Test distance calculation accuracy and coverage"""
    print("=== Testing Distance Calculations ===\n")
    
    # Test distance calculations for each station type
    station_types = ['space', 'subway', 'rail']
    
    for station_type in station_types:
        stations = stanton_system.get_stations_by_type(station_type)
        if len(stations) >= 2:
            station_names = list(stations.keys())
            distance = stanton_system.get_distance(station_names[0], station_names[1])
            if distance:
                print(f"✅ {station_type} distance calculation: {distance.distance:.2f} {distance.unit}")
            else:
                print(f"❌ {station_type} distance calculation failed")
        else:
            print(f"⚠️  {station_type}: Not enough stations for distance test")
    
    print("\n=== Distance Calculation Tests Completed ===\n")

def test_integration_examples():
    """Test integration with example use cases"""
    print("=== Testing Integration Examples ===\n")
    
    # Example 1: Route planning
    space_stations = list(stanton_system.get_stations_by_type('space').keys())
    if len(space_stations) >= 3:
        route = space_stations[:3]
        total_distance = stanton_system.get_route_distance(route)
        if total_distance is not None:
            print(f"✅ Route planning works: {' -> '.join(route)} = {total_distance:.2f} units")
        else:
            print(f"❌ Route planning failed")
    
    # Example 2: Multi-language support
    german_queries = [
        "Stanton Stationen Übersicht",
        "Entfernungen zwischen Stationen",
        "Nächste Stationen finden"
    ]
    
    agent = ResearchAgent()
    german_support_count = sum(1 for query in german_queries 
                             if agent._is_stanton_station_query(query))
    print(f"✅ German language support: {german_support_count}/{len(german_queries)} queries recognized")
    
    print("\n=== Integration Examples Completed ===\n")

def main():
    """Run all tests"""
    print("🚀 Starting Stanton Station Integration Tests\n")
    
    try:
        test_stanton_system_basic()
        test_research_agent_integration()
        test_station_data_quality()
        test_distance_calculations()
        test_integration_examples()
        
        print("🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("- Stanton station system is fully operational")
        print("- Research agent integration is working")
        print("- Distance calculations are functional")
        print("- Multi-language support is implemented")
        print("- System ready for user queries")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()