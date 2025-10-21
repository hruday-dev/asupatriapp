import flet as ft
import requests
import json
from datetime import datetime
from profile_view import create_profile_view
import folium
import tempfile
import os
import math

API_BASE = "http://127.0.0.1:2000/api"

def calculate_distance(lat1, lon1, lat2, lon2):
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

def scrape_nearby_hospitals(lat, lon):
    """Improved hospital scraping with better coverage"""
    hospitals = []
    
    print(f"Scraping hospitals for location: {lat}, {lon}")
    
    try:
        # Use Overpass API with comprehensive healthcare search
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:45];
        (
          node["amenity"="hospital"](around:25000,{lat},{lon});
          way["amenity"="hospital"](around:25000,{lat},{lon});
          relation["amenity"="hospital"](around:25000,{lat},{lon});
          node["amenity"="clinic"](around:25000,{lat},{lon});
          way["amenity"="clinic"](around:25000,{lat},{lon});
          relation["amenity"="clinic"](around:25000,{lat},{lon});
          node["amenity"="doctors"](around:25000,{lat},{lon});
          way["amenity"="doctors"](around:25000,{lat},{lon});
          relation["amenity"="doctors"](around:25000,{lat},{lon});
          node["healthcare"="hospital"](around:25000,{lat},{lon});
          way["healthcare"="hospital"](around:25000,{lat},{lon});
          relation["healthcare"="hospital"](around:25000,{lat},{lon});
          node["healthcare"="clinic"](around:25000,{lat},{lon});
          way["healthcare"="clinic"](around:25000,{lat},{lon});
          relation["healthcare"="clinic"](around:25000,{lat},{lon});
        );
        out center;
        """
        
        print(f"Making comprehensive request to Overpass API...")
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=30)
        print(f"Overpass API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            print(f"Found {len(elements)} healthcare elements from Overpass API")
            
            for element in elements:
                tags = element.get('tags', {})
                name = tags.get('name', 'Unknown Hospital')
                
                # Skip if no name
                if name == 'Unknown Hospital':
                    continue
                
                # Get address from various possible fields
                addr = (tags.get('addr:full') or 
                       tags.get('addr:street') or 
                       tags.get('addr:housename') or 
                       'Address not available')
                
                phone = tags.get('phone', 'Phone not available')
                
                # Get coordinates
                hosp_lat = None
                hosp_lon = None
                
                if 'lat' in element and 'lon' in element:
                    hosp_lat = element['lat']
                    hosp_lon = element['lon']
                elif 'center' in element:
                    hosp_lat = element['center']['lat']
                    hosp_lon = element['center']['lon']
                
                if hosp_lat is None or hosp_lon is None:
                    continue
                
                # Calculate distance
                distance = calculate_distance(lat, lon, hosp_lat, hosp_lon)
                
                hospitals.append({
                    'name': name,
                    'address': addr,
                    'phone': phone,
                    'distance_km': round(distance, 2),
                    'latitude': hosp_lat,
                    'longitude': hosp_lon,
                    'fee_details': 'Contact hospital for pricing'
                })
            
            print(f"Processed {len(hospitals)} hospitals from Overpass API")
            
            # Sort by distance
            hospitals.sort(key=lambda x: x['distance_km'])
            return hospitals[:15]  # Return top 15 nearest
        
    except Exception as ex:
        print(f"Overpass API scraping error: {ex}")
    
    # Fallback to database hospitals
    print("Falling back to database hospitals...")
    try:
        r = requests.get(f"{API_BASE}/hospitals/nearby", params={"lat": lat, "lon": lon}, timeout=5)
        print(f"Database API response status: {r.status_code}")
        if r.status_code == 200:
            db_hospitals = r.json().get("hospitals", [])
            print(f"Found {len(db_hospitals)} hospitals from database")
            return db_hospitals
    except Exception as ex:
        print(f"Database API error: {ex}")
    
    # Final fallback - create some sample hospitals
    print("Using sample hospitals as final fallback...")
    sample_hospitals = [
        {
            'name': 'City General Hospital',
            'address': '123 Main Street, Downtown',
            'phone': '+1-555-0101',
            'distance_km': 0.5,
            'fee_details': 'Consultation: $50, Emergency: $100'
        },
        {
            'name': 'Metro Medical Center',
            'address': '456 Health Avenue, Midtown',
            'phone': '+1-555-0102',
            'distance_km': 1.2,
            'fee_details': 'Consultation: $60, Emergency: $120'
        },
        {
            'name': 'Sunrise Hospital',
            'address': '789 Wellness Blvd, Uptown',
            'phone': '+1-555-0103',
            'distance_km': 2.1,
            'fee_details': 'Consultation: $45, Emergency: $90'
        }
    ]
    return sample_hospitals

def main(page: ft.Page):
    page.title = "Patient App"
    token = {"value": None}
    user_id = {"value": None}
    current_view = {"value": "home"}
    user_location = {"lat": None, "lon": None}
    theme_mode = {"value": ft.ThemeMode.LIGHT}
    hospitals_data = {"value": []}  # Store hospitals for map
    view_mode = {"value": "list"}  # "list" or "map"

    # Login components
    email = ft.TextField(label="Email")
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    output = ft.Text()

    # Sign-up components
    signup_email = ft.TextField(label="Email")
    signup_password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    signup_confirm_password = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True)
    signup_full_name = ft.TextField(label="Full Name")
    signup_output = ft.Text()
    
    # Navigation components
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_TODAY, label="Appointments"),
            ft.NavigationBarDestination(icon=ft.Icons.CHECK_CIRCLE, label="Completed"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Profile"),
        ],
        on_change=lambda e: change_view(e.control.selected_index),
        height=60
    )
    
    # Content areas
    content_area = ft.Container(animate_opacity=300)
    hospitals_list = ft.ListView(expand=1, spacing=10, padding=10)
    hospitals_map = ft.Container()  # For map view
    appt_list = ft.ListView(expand=1, spacing=10, padding=10)
    completed_appt_list = ft.ListView(expand=1, spacing=10, padding=10)

    # Stats texts
    stats_texts = {
        "appointments": ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
        "completed": ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
        "hospitals": ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
    }

    def do_login(e):
        try:
            r = requests.post(f"{API_BASE}/login", json={"email": email.value, "password": password.value})
            if r.status_code == 200:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                output.value = "Logged in"
                page.update()
                show_main_app()
            else:
                output.value = r.json().get("message", "Login failed")
                page.update()
        except Exception as ex:
            output.value = str(ex)
            page.update()

    def show_main_app():
        page.theme_mode = theme_mode["value"]
        page.clean()
        page.add(
            ft.Column([
                ft.Container(
                    content=content_area,
                    expand=True,
                    padding=10
                ),
                nav_bar
            ], expand=True)
        )
        show_home_view()

    def logout(e):
        token["value"] = None
        user_id["value"] = None
        page.clean()
        show_login_view()

    def change_view(index):
        content_area.opacity = 0
        page.update()
        if index == 0:
            show_home_view()
        elif index == 1:
            show_appointments_view()
        elif index == 2:
            show_completed_view()
        elif index == 3:
            show_profile_view()

    def show_home_view():
        current_view["value"] = "home"
        content_area.content = ft.Column([
            ft.Text("Welcome, Patient!", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Today's Overview", size=18),
            ft.Divider(),
            ft.Text("Quick Stats:", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CALENDAR_TODAY, size=30, color=ft.Colors.BLUE),
                            ft.Text("Today's Appointments", size=14),
                            stats_texts["appointments"],
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    ),
                    margin=ft.margin.symmetric(horizontal=5)
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, size=30, color=ft.Colors.GREEN),
                            ft.Text("Completed Today", size=14),
                            stats_texts["completed"],
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    ),
                    margin=ft.margin.symmetric(horizontal=5)
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=30, color=ft.Colors.ORANGE),
                            ft.Text("Nearby Hospitals", size=14),
                            stats_texts["hospitals"],
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    ),
                    margin=ft.margin.symmetric(horizontal=5)
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            ft.Divider(),
            ft.Row([
                ft.Text("Nearby Hospitals:", size=16, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh hospital search",
                    on_click=lambda e: load_nearby()
                ),
                ft.IconButton(
                    icon=ft.Icons.MAP,
                    tooltip="Toggle Map/List View",
                    on_click=toggle_view_mode
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            hospitals_list if view_mode["value"] == "list" else hospitals_map,
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        load_nearby()
        load_stats()
        content_area.opacity = 1
        page.update()

    def show_appointments_view():
        current_view["value"] = "appointments"
        load_appointments()
        content_area.content = ft.Column([
            ft.Text("Today's Appointments", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            appt_list,
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        content_area.opacity = 1
        page.update()

    def show_completed_view():
        current_view["value"] = "completed"
        load_completed_appointments()
        content_area.content = ft.Column([
            ft.Text("Completed Appointments", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            completed_appt_list,
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        content_area.opacity = 1
        page.update()

    def show_profile_view():
        current_view["value"] = "profile"
        profile_content_area, profile_show_func = create_profile_view(page, token, user_id, API_BASE, logout, theme_mode)
        content_area.content = profile_content_area.content
        profile_show_func()

    def toggle_theme(e):
        theme_mode["value"] = ft.ThemeMode.DARK if theme_mode["value"] == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.theme_mode = theme_mode["value"]
        page.update()

    def toggle_view_mode(e):
        view_mode["value"] = "map" if view_mode["value"] == "list" else "list"
        update_hospitals_view()
        page.update()

    def update_hospitals_view():
        if view_mode["value"] == "list":
            content_area.content.controls[-1] = hospitals_list
        else:
            if hospitals_data["value"]:
                map_file = generate_map_html(hospitals_data["value"], user_location["lat"], user_location["lon"])
                hospitals_map.content = ft.Column([
                    ft.WebView(url=f"file://{map_file}", expand=True, height=300),
                    ft.Text("Click on a hospital marker for details", size=12, color=ft.Colors.GREY),
                    create_hospital_list_for_map()
                ], expand=True)
            else:
                hospitals_map.content = ft.Text("No hospital data available for map")
            content_area.content.controls[-1] = hospitals_map

    def create_hospital_list_for_map():
        list_view = ft.ListView(expand=1, spacing=5, padding=10)
        for h in hospitals_data["value"]:
            list_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(h['name'], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"📍 {h['address']}", size=12),
                            ft.Text(f"📞 {h.get('phone', 'N/A')}", size=12),
                            ft.Text(f"💰 {h.get('fee_details', 'Contact for pricing')}", size=12),
                            ft.Text(f"📏 {h.get('distance_km', '?')} km away", size=12, color=ft.Colors.BLUE),
                            ft.ElevatedButton("Book Appointment", on_click=lambda e, hospital=h: show_hospital_details(hospital))
                        ], spacing=2),
                        padding=10
                    ),
                    margin=ft.margin.symmetric(vertical=2)
                )
            )
        return list_view

    def show_hospital_details(hospital):
        # Show a dialog with hospital details and booking option
        dlg = ft.AlertDialog(
            title=ft.Text(hospital['name']),
            content=ft.Column([
                ft.Text(f"Address: {hospital['address']}"),
                ft.Text(f"Phone: {hospital.get('phone', 'N/A')}"),
                ft.Text(f"Distance: {hospital.get('distance_km', '?')} km"),
                ft.Text(f"Fees: {hospital.get('fee_details', 'Contact for pricing')}"),
            ], tight=True),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(dlg)),
                ft.ElevatedButton("Book Appointment", on_click=lambda e: book_appointment(hospital, dlg))
            ]
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    def book_appointment(hospital, dlg):
        # Placeholder for booking logic
        dlg.open = False
        snack = ft.SnackBar(ft.Text(f"Booking for {hospital['name']} - Feature coming soon!"))
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def get_user_location():
        """Get user's current location using IP-based geolocation"""
        try:
            # Try multiple IP geolocation services for better reliability
            services = [
                "http://ip-api.com/json/",
                "https://ipapi.co/json/",
                "http://ipinfo.io/json"
            ]
            
            for service in services:
                try:
                    print(f"Trying location service: {service}")
                    response = requests.get(service, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Location service response: {data}")
                        
                        # Handle different response formats
                        if service == "http://ip-api.com/json/":
                            if data.get('status') == 'success':
                                user_location["lat"] = data.get('lat')
                                user_location["lon"] = data.get('lon')
                                print(f"Got location from ip-api: {user_location}")
                                return True
                        elif service == "https://ipapi.co/json/":
                            if 'latitude' in data and 'longitude' in data:
                                user_location["lat"] = data.get('latitude')
                                user_location["lon"] = data.get('longitude')
                                print(f"Got location from ipapi.co: {user_location}")
                                return True
                        elif service == "http://ipinfo.io/json":
                            if 'loc' in data:
                                lat, lon = data['loc'].split(',')
                                user_location["lat"] = float(lat)
                                user_location["lon"] = float(lon)
                                print(f"Got location from ipinfo: {user_location}")
                                return True
                except Exception as e:
                    print(f"Error with {service}: {e}")
                    continue
            
            # Fallback to demo coordinates
            print("All location services failed, using demo coordinates")
            user_location["lat"] = 18.5204
            user_location["lon"] = 73.8567
            return True
            
        except Exception as ex:
            print(f"Location error: {ex}")
            # Fallback to demo coordinates
            user_location["lat"] = 18.5204
            user_location["lon"] = 73.8567
            return False

    def generate_map_html(hospitals, user_lat, user_lon):
        """Generate HTML for folium map with hospital markers"""
        if not hospitals or user_lat is None or user_lon is None:
            return "<html><body><h3>No hospitals or location data available</h3></body></html>"
        
        # Create map centered on user location
        m = folium.Map(location=[user_lat, user_lon], zoom_start=12)
        
        # Add user location marker
        folium.Marker(
            [user_lat, user_lon],
            popup="Your Location",
            icon=folium.Icon(color='blue', icon='user')
        ).add_to(m)
        
        # Add hospital markers
        for h in hospitals:
            lat = h.get('latitude')
            lon = h.get('longitude')
            if lat is not None and lon is not None:
                popup_content = f"""
                <b>{h['name']}</b><br>
                {h['address']}<br>
                Phone: {h.get('phone', 'N/A')}<br>
                Distance: {h.get('distance_km', '?')} km<br>
                <button onclick="alert('Hospital: {h['name']}')">View Details</button>
                """
                folium.Marker(
                    [lat, lon],
                    popup=popup_content,
                    icon=folium.Icon(color='red', icon='plus')
                ).add_to(m)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            m.save(f.name)
            return f.name

    def load_nearby():
        hospitals_list.controls.clear()
        hospitals_list.controls.append(ft.Text("🌍 Getting your location...", color=ft.Colors.BLUE))
        page.update()
        
        try:
            print("Starting location detection...")
            # Get user's real location
            location_success = get_user_location()
            print(f"Location detection result: {location_success}")
            print(f"User location: {user_location}")
            
            if location_success and user_location["lat"] is not None:
                lat, lon = user_location["lat"], user_location["lon"]
                hospitals_list.controls.clear()
                hospitals_list.controls.append(ft.Text(f"📍 Your Location: {lat:.4f}, {lon:.4f}", color=ft.Colors.GREEN, size=14))
                hospitals_list.controls.append(ft.Text("🔍 Searching for nearby hospitals...", color=ft.Colors.BLUE))
                page.update()
                
                print(f"Starting hospital search for coordinates: {lat}, {lon}")
                # Scrape hospitals from web sources
                hospitals = scrape_nearby_hospitals(lat, lon)
                print(f"Hospital search completed. Found {len(hospitals)} hospitals")
                
                # Store for map
                hospitals_data["value"] = hospitals
                
                hospitals_list.controls.clear()
                update_hospitals_view()
                
                if hospitals:
                    hospitals_list.controls.append(ft.Text(f"🏥 Found {len(hospitals)} nearby hospitals:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
                    hospitals_list.controls.append(ft.Text(f"📍 Based on your location: {lat:.4f}, {lon:.4f}", size=12, color=ft.Colors.BLUE))
                    
                    for i, h in enumerate(hospitals, 1):
                        distance = h.get('distance_km', '?')
                        phone = h.get('phone', 'N/A')
                        hospitals_list.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text(f"#{i}", size=12, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
                                            ft.Text(h['name'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                        ]),
                                        ft.Text(f"📍 {h['address']}", size=12),
                                        ft.Text(f"📞 {phone}", size=12),
                                        ft.Text(f"💰 {h.get('fee_details', 'Contact for pricing')}", size=12),
                                        ft.Text(f"📏 {distance} km away", size=12, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
                                    ], spacing=2),
                                    padding=10
                                ),
                                margin=ft.margin.symmetric(vertical=2)
                            )
                        )
                else:
                    hospitals_list.controls.append(ft.Text("❌ No hospitals found nearby", color=ft.Colors.ORANGE, size=16))
                    hospitals_list.controls.append(ft.Text("💡 This might be due to:", size=12))
                    hospitals_list.controls.append(ft.Text("• Limited hospital data in your area", size=12))
                    hospitals_list.controls.append(ft.Text("• Internet connection issues", size=12))
                    hospitals_list.controls.append(ft.Text("• Location services not available", size=12))
            else:
                hospitals_list.controls.clear()
                hospitals_list.controls.append(ft.Text("❌ Could not get your location", color=ft.Colors.RED, size=16))
                hospitals_list.controls.append(ft.Text("📍 Using sample hospitals instead...", color=ft.Colors.ORANGE))
                
                # Use sample hospitals as fallback
                sample_hospitals = [
                    {
                        'name': 'City General Hospital',
                        'address': '123 Main Street, Downtown',
                        'phone': '+1-555-0101',
                        'distance_km': 0.5,
                        'fee_details': 'Consultation: $50, Emergency: $100'
                    },
                    {
                        'name': 'Metro Medical Center',
                        'address': '456 Health Avenue, Midtown',
                        'phone': '+1-555-0102',
                        'distance_km': 1.2,
                        'fee_details': 'Consultation: $60, Emergency: $120'
                    },
                    {
                        'name': 'Sunrise Hospital',
                        'address': '789 Wellness Blvd, Uptown',
                        'phone': '+1-555-0103',
                        'distance_km': 2.1,
                        'fee_details': 'Consultation: $45, Emergency: $90'
                    }
                ]
                
                hospitals_list.controls.append(ft.Text(f"🏥 Sample hospitals (for demonstration):", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE))
                
                for i, h in enumerate(sample_hospitals, 1):
                    hospitals_list.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(f"#{i}", size=12, color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD),
                                        ft.Text(h['name'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                    ]),
                                    ft.Text(f"📍 {h['address']}", size=12),
                                    ft.Text(f"📞 {h['phone']}", size=12),
                                    ft.Text(f"💰 {h['fee_details']}", size=12),
                                    ft.Text(f"📏 {h['distance_km']} km away", size=12, color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD),
                                ], spacing=2),
                                padding=10
                            ),
                            margin=ft.margin.symmetric(vertical=2)
                        )
                    )
                
        except Exception as ex:
            print(f"Error in load_nearby: {ex}")
            hospitals_list.controls.clear()
            hospitals_list.controls.append(ft.Text(f"❌ Error: {str(ex)}", color=ft.Colors.RED, size=16))
            hospitals_list.controls.append(ft.Text("💡 Please check your internet connection", color=ft.Colors.BLUE, size=12))
            hospitals_list.controls.append(ft.Text("🔄 Try clicking the refresh button to retry", color=ft.Colors.BLUE, size=12))   
        
        page.update()

    def load_stats():
        headers = {"Authorization": f"Bearer {token['value']}"}
        r = requests.get(f"{API_BASE}/appointments/{user_id['value']}?today=true", headers=headers)
        today_count = 0
        completed_today = 0
        if r.status_code == 200:
            appointments = r.json().get("appointments", [])
            today_count = len([a for a in appointments if a['status'] != 'Completed'])
            completed_today = len([a for a in appointments if a['status'] == 'Completed'])
        stats_texts["appointments"].value = str(today_count)
        stats_texts["completed"].value = str(completed_today)
        stats_texts["hospitals"].value = "Nearby"  # Since hospitals are loaded separately
        page.update()

    def load_appointments():
        appt_list.controls.clear()
        headers = {"Authorization": f"Bearer {token['value']}"}
        # Add today=true parameter to get only today's appointments
        r = requests.get(f"{API_BASE}/appointments/{user_id['value']}?today=true", headers=headers)
        if r.status_code == 200:
            appointments = r.json().get("appointments", [])
            if appointments:
                for a in appointments:
                    if a['status'] != 'Completed':
                        status_color = ft.Colors.BLUE if a['status'] == 'Scheduled' else ft.Colors.ORANGE
                        appt_list.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.BLUE),
                                            ft.Text(f"{a['date']} at {a['time']}", size=16, weight=ft.FontWeight.BOLD),
                                        ]),
                                        ft.Text(f"Status: {a['status']}", color=status_color),
                                        ft.Text(f"Doctor: {a.get('doctor_name', 'Unknown')}", size=14),
                                        ft.Text(f"Hospital: {a.get('hospital_name', 'Unknown')}", size=14),
                                    ], spacing=5),
                                    padding=15
                                ),
                                margin=ft.margin.symmetric(vertical=5)
                            )
                        )
            else:
                appt_list.controls.append(ft.Text("No appointments scheduled for today", color=ft.Colors.GREY))
        else:
            appt_list.controls.append(ft.Text("Failed to load appointments", color=ft.Colors.RED))
        page.update()

    def load_completed_appointments():
        completed_appt_list.controls.clear()
        headers = {"Authorization": f"Bearer {token['value']}"}
        # Get all appointments and filter for completed ones
        r = requests.get(f"{API_BASE}/appointments/{user_id['value']}", headers=headers)
        if r.status_code == 200:
            appointments = r.json().get("appointments", [])
            completed_appts = [a for a in appointments if a['status'] == 'Completed']
            if completed_appts:
                for a in completed_appts:
                    completed_appt_list.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                                        ft.Text(f"{a['date']} at {a['time']}", size=16, weight=ft.FontWeight.BOLD),
                                    ]),
                                    ft.Text(f"Status: {a['status']}", color=ft.Colors.GREEN),
                                    ft.Text(f"Doctor: {a.get('doctor_name', 'Unknown')}", size=14),
                                    ft.Text(f"Hospital: {a.get('hospital_name', 'Unknown')}", size=14),
                                ], spacing=5),
                                padding=15
                            ),
                            margin=ft.margin.symmetric(vertical=5)
                        )
                    )
            else:
                completed_appt_list.controls.append(ft.Text("No completed appointments found", color=ft.Colors.GREY))
        else:
            completed_appt_list.controls.append(ft.Text("Failed to load completed appointments", color=ft.Colors.RED))
        page.update()

    def do_signup(e):
        try:
            # Validate passwords match
            if signup_password.value != signup_confirm_password.value:
                signup_output.value = "Passwords do not match"
                signup_output.color = ft.Colors.RED
                page.update()
                return
            
            # Validate required fields
            if not all([signup_email.value, signup_password.value, signup_full_name.value]):
                signup_output.value = "Please fill in all fields"
                signup_output.color = ft.Colors.RED
                page.update()
                return
            
            r = requests.post(f"{API_BASE}/register", json={
                "email": signup_email.value,
                "password": signup_password.value,
                "user_type": "Patient",
                "full_name": signup_full_name.value
            })
            
            if r.status_code == 201:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                signup_output.value = "Account created successfully!"
                signup_output.color = ft.Colors.GREEN
                page.update()
                show_main_app()
            else:
                signup_output.value = r.json().get("message", "Registration failed")
                signup_output.color = ft.Colors.RED
                page.update()
        except Exception as ex:
            signup_output.value = str(ex)
            signup_output.color = ft.Colors.RED
            page.update()

    def show_login_view():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=40, color=ft.Colors.BLUE),
                    ft.Text("Patient App", size=24, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Login", size=18, weight=ft.FontWeight.BOLD),
                        email,
                        password,
                        ft.ElevatedButton("Login", on_click=do_login, width=200),
                        output,
                        ft.TextButton("Don't have an account? Sign Up", on_click=lambda e: show_signup_view()),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def show_signup_view():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=40, color=ft.Colors.BLUE),
                    ft.Text("Patient App", size=24, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Create Account", size=18, weight=ft.FontWeight.BOLD),
                        signup_full_name,
                        signup_email,
                        signup_password,
                        signup_confirm_password,
                        ft.ElevatedButton("Sign Up", on_click=do_signup, width=200),
                        signup_output,
                        ft.TextButton("Already have an account? Login", on_click=lambda e: show_login_view()),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    # Initialize with login view
    show_login_view()

ft.app(target=main)