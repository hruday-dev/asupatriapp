"""
Hospital Search Improvements for Patient App
This module contains enhanced hospital search functionality to improve accuracy and coverage.
"""

import requests
import math
from typing import List, Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6371 * c
    return km

def get_comprehensive_hospitals(lat: float, lon: float, radius_km: int = 25) -> List[Dict[str, Any]]:
    """
    Get comprehensive hospital data from multiple sources
    """
    hospitals = []
    
    # 1. Enhanced Overpass API query
    overpass_hospitals = get_overpass_hospitals(lat, lon, radius_km)
    hospitals.extend(overpass_hospitals)
    
    # 2. Try additional data sources if needed
    if len(hospitals) < 5:  # If we found very few hospitals
        # Add Google Places API (if API key available)
        google_hospitals = get_google_places_hospitals(lat, lon, radius_km)
        hospitals.extend(google_hospitals)
        
        # Add OpenStreetMap Nominatim search
        nominatim_hospitals = get_nominatim_hospitals(lat, lon, radius_km)
        hospitals.extend(nominatim_hospitals)
    
    # Remove duplicates and sort by distance
    unique_hospitals = remove_duplicate_hospitals(hospitals)
    unique_hospitals.sort(key=lambda x: x.get('distance_km', float('inf')))
    
    return unique_hospitals[:20]  # Return top 20 nearest

def get_overpass_hospitals(lat: float, lon: float, radius_km: int) -> List[Dict[str, Any]]:
    """
    Enhanced Overpass API query with comprehensive healthcare facility search
    """
    hospitals = []
    
    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Comprehensive query for all healthcare facilities
        overpass_query = f"""
        [out:json][timeout:45];
        (
          node["amenity"="hospital"](around:{radius_km*1000},{lat},{lon});
          way["amenity"="hospital"](around:{radius_km*1000},{lat},{lon});
          relation["amenity"="hospital"](around:{radius_km*1000},{lat},{lon});
          
          node["amenity"="clinic"](around:{radius_km*1000},{lat},{lon});
          way["amenity"="clinic"](around:{radius_km*1000},{lat},{lon});
          relation["amenity"="clinic"](around:{radius_km*1000},{lat},{lon});
          
          node["amenity"="doctors"](around:{radius_km*1000},{lat},{lon});
          way["amenity"="doctors"](around:{radius_km*1000},{lat},{lon});
          relation["amenity"="doctors"](around:{radius_km*1000},{lat},{lon});
          
          node["healthcare"="hospital"](around:{radius_km*1000},{lat},{lon});
          way["healthcare"="hospital"](around:{radius_km*1000},{lat},{lon});
          relation["healthcare"="hospital"](around:{radius_km*1000},{lat},{lon});
          
          node["healthcare"="clinic"](around:{radius_km*1000},{lat},{lon});
          way["healthcare"="clinic"](around:{radius_km*1000},{lat},{lon});
          relation["healthcare"="clinic"](around:{radius_km*1000},{lat},{lon});
          
          node["healthcare"="doctor"](around:{radius_km*1000},{lat},{lon});
          way["healthcare"="doctor"](around:{radius_km*1000},{lat},{lon});
          relation["healthcare"="doctor"](around:{radius_km*1000},{lat},{lon});
          
          node["healthcare"="pharmacy"](around:{radius_km*1000},{lat},{lon});
          way["healthcare"="pharmacy"](around:{radius_km*1000},{lat},{lon});
          relation["healthcare"="pharmacy"](around:{radius_km*1000},{lat},{lon});
          
          node["emergency"="yes"](around:{radius_km*1000},{lat},{lon});
          way["emergency"="yes"](around:{radius_km*1000},{lat},{lon});
          relation["emergency"="yes"](around:{radius_km*1000},{lat},{lon});
        );
        out center;
        """
        
        print(f"Making comprehensive Overpass API request for {radius_km}km radius...")
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=30)
        print(f"Overpass API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            print(f"Found {len(elements)} healthcare elements from Overpass API")
            
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name', 'Unknown Healthcare Facility')
                
                # Skip entries without proper names
                if name == 'Unknown Healthcare Facility':
                    continue
                
                # Determine facility type for better categorization
                facility_type = determine_facility_type(tags)
                
                # Get comprehensive address information
                address = get_comprehensive_address(tags)
                
                # Get contact information
                phone = tags.get('phone', tags.get('contact:phone', 'Phone not available'))
                website = tags.get('website', tags.get('contact:website', ''))
                
                # Get coordinates
                hosp_lat, hosp_lon = get_coordinates(element)
                
                if hosp_lat is None or hosp_lon is None:
                    continue
                
                # Calculate distance
                distance = calculate_distance(lat, lon, hosp_lat, hosp_lon)
                
                # Get additional healthcare details
                specialization = tags.get('healthcare:speciality', tags.get('speciality', 'General'))
                opening_hours = tags.get('opening_hours', 'Hours not available')
                
                hospitals.append({
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'website': website,
                    'distance_km': round(distance, 2),
                    'latitude': hosp_lat,
                    'longitude': hosp_lon,
                    'facility_type': facility_type,
                    'specialization': specialization,
                    'opening_hours': opening_hours,
                    'fee_details': 'Contact facility for pricing',
                    'data_source': 'OpenStreetMap'
                })
            
            print(f"Processed {len(hospitals)} healthcare facilities from Overpass API")
            
    except Exception as ex:
        print(f"Overpass API error: {ex}")
    
    return hospitals

def determine_facility_type(tags: Dict[str, str]) -> str:
    """Determine the type of healthcare facility"""
    amenity = tags.get('amenity', '')
    healthcare = tags.get('healthcare', '')
    emergency = tags.get('emergency', '')
    
    if emergency == 'yes':
        return 'Emergency Care'
    elif amenity == 'hospital' or healthcare == 'hospital':
        return 'Hospital'
    elif amenity == 'clinic' or healthcare == 'clinic':
        return 'Clinic'
    elif amenity == 'doctors' or healthcare == 'doctor':
        return 'Medical Practice'
    elif amenity == 'pharmacy' or healthcare == 'pharmacy':
        return 'Pharmacy'
    else:
        return 'Healthcare Facility'

def get_comprehensive_address(tags: Dict[str, str]) -> str:
    """Get comprehensive address information from OSM tags"""
    address_parts = []
    
    # Try different address field combinations
    if tags.get('addr:full'):
        address_parts.append(tags.get('addr:full'))
    else:
        # Build address from components
        house_number = tags.get('addr:housenumber', '')
        street = tags.get('addr:street', '')
        city = tags.get('addr:city', '')
        postcode = tags.get('addr:postcode', '')
        
        if house_number and street:
            address_parts.append(f"{house_number} {street}")
        elif street:
            address_parts.append(street)
        
        if city:
            if postcode:
                address_parts.append(f"{postcode} {city}")
            else:
                address_parts.append(city)
    
    return ', '.join(address_parts) if address_parts else 'Address not available'

def get_coordinates(element: Dict[str, Any]) -> tuple:
    """Extract coordinates from OSM element"""
    if 'lat' in element and 'lon' in element:
        return element['lat'], element['lon']
    elif 'center' in element:
        return element['center']['lat'], element['center']['lon']
    return None, None

def get_google_places_hospitals(lat: float, lon: float, radius_km: int) -> List[Dict[str, Any]]:
    """
    Get hospitals from Google Places API (requires API key)
    This is a placeholder - you'll need to add your Google Places API key
    """
    # Note: This requires a Google Places API key
    # Uncomment and modify if you have access to Google Places API
    """
    API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        'location': f'{lat},{lon}',
        'radius': radius_km * 1000,
        'type': 'hospital',
        'key': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            hospitals = []
            for place in data.get('results', []):
                hospitals.append({
                    'name': place['name'],
                    'address': place.get('vicinity', 'Address not available'),
                    'phone': 'Contact for details',
                    'distance_km': calculate_distance(lat, lon, place['geometry']['location']['lat'], place['geometry']['location']['lng']),
                    'latitude': place['geometry']['location']['lat'],
                    'longitude': place['geometry']['location']['lng'],
                    'facility_type': 'Hospital',
                    'data_source': 'Google Places'
                })
            return hospitals
    except Exception as ex:
        print(f"Google Places API error: {ex}")
    """
    return []

def get_nominatim_hospitals(lat: float, lon: float, radius_km: int) -> List[Dict[str, Any]]:
    """
    Get hospitals using Nominatim search (alternative OSM API)
    """
    hospitals = []
    
    try:
        # Search for hospitals in the area
        search_url = "https://nominatim.openstreetmap.org/search"
        
        # Create a bounding box around the location
        # Approximate conversion: 1 degree ≈ 111 km
        lat_offset = radius_km / 111
        lon_offset = radius_km / (111 * math.cos(math.radians(lat)))
        
        viewbox = f"{lon - lon_offset},{lat + lat_offset},{lon + lon_offset},{lat - lat_offset}"
        
        params = {
            'q': 'hospital',
            'viewbox': viewbox,
            'bounded': 1,
            'limit': 50,
            'format': 'json',
            'addressdetails': 1
        }
        
        response = requests.get(search_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for place in data:
                if 'lat' in place and 'lon' in place:
                    hosp_lat = float(place['lat'])
                    hosp_lon = float(place['lon'])
                    distance = calculate_distance(lat, lon, hosp_lat, hosp_lon)
                    
                    if distance <= radius_km:
                        hospitals.append({
                            'name': place.get('display_name', 'Unknown Hospital'),
                            'address': place.get('display_name', 'Address not available'),
                            'phone': 'Contact for details',
                            'distance_km': round(distance, 2),
                            'latitude': hosp_lat,
                            'longitude': hosp_lon,
                            'facility_type': 'Hospital',
                            'data_source': 'Nominatim'
                        })
        
        print(f"Found {len(hospitals)} hospitals from Nominatim")
        
    except Exception as ex:
        print(f"Nominatim API error: {ex}")
    
    return hospitals

def remove_duplicate_hospitals(hospitals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate hospitals based on name and location proximity
    """
    unique_hospitals = []
    seen_names = set()
    
    for hospital in hospitals:
        name = hospital.get('name', '').lower().strip()
        
        # Check for exact name matches
        if name not in seen_names:
            # Check for location proximity with existing hospitals
            is_duplicate = False
            for existing in unique_hospitals:
                if (abs(hospital.get('latitude', 0) - existing.get('latitude', 0)) < 0.001 and
                    abs(hospital.get('longitude', 0) - existing.get('longitude', 0)) < 0.001):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_hospitals.append(hospital)
                seen_names.add(name)
    
    return unique_hospitals

# Example usage function that can be integrated into the main app
def enhanced_scrape_nearby_hospitals(lat: float, lon: float) -> List[Dict[str, Any]]:
    """
    Enhanced version of the original scrape_nearby_hospitals function
    """
    print(f"Starting comprehensive hospital search for location: {lat}, {lon}")
    
    # Get comprehensive hospital data
    hospitals = get_comprehensive_hospitals(lat, lon, radius_km=25)
    
    if not hospitals:
        print("No hospitals found from online sources, using fallback data")
        # Return some sample hospitals as last resort
        return [
            {
                'name': 'City General Hospital',
                'address': '123 Main Street, Downtown',
                'phone': '+1-555-0101',
                'distance_km': 0.5,
                'facility_type': 'Hospital',
                'fee_details': 'Consultation: $50, Emergency: $100',
                'data_source': 'Sample Data'
            },
            {
                'name': 'Metro Medical Center',
                'address': '456 Health Avenue, Midtown',
                'phone': '+1-555-0102',
                'distance_km': 1.2,
                'facility_type': 'Hospital',
                'fee_details': 'Consultation: $60, Emergency: $120',
                'data_source': 'Sample Data'
            }
        ]
    
    print(f"Comprehensive search completed. Found {len(hospitals)} healthcare facilities")
    return hospitals