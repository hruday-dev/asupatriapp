import flet as ft
import requests
import json
import httpx
from datetime import datetime

API_BASE = "http://127.0.0.1:2000/api"

# Profile view handled locally

def main(page: ft.Page):
    page.title = "Patient App"
    token = {"value": None}
    user_id = {"value": None}
    current_view = {"value": "home"}
    user_location = {"lat": 0.0, "lon": 0.0}

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
    
    # Navigation components with modern styling
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_ROUNDED,
                label="Home",
                selected_icon=ft.Icons.HOME_ROUNDED
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                label="Appointments",
                selected_icon=ft.Icons.CALENDAR_TODAY_ROUNDED
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                label="Completed",
                selected_icon=ft.Icons.CHECK_CIRCLE_ROUNDED
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PERSON_ROUNDED,
                label="Profile",
                selected_icon=ft.Icons.PERSON_ROUNDED
            ),
        ],
        on_change=lambda e: change_view(e.control.selected_index),
        height=70,
        bgcolor=ft.Colors.WHITE,
        shadow_color=ft.Colors.BLACK26,
        elevation=8,
        indicator_color=ft.Colors.BLUE_600,
        indicator_shape=ft.RoundedRectangleBorder(radius=20),
    )
    
    # Content areas
    content_area = ft.Container()
    hospitals_list = ft.ListView(expand=1, spacing=10, padding=10)
    appt_list = ft.ListView(expand=1, spacing=10, padding=10)
    completed_appt_list = ft.ListView(expand=1, spacing=10, padding=10)

    # Search components
    search_field = ft.TextField(
        label="Search hospitals or treatments",
        hint_text="Enter hospital name, address, or treatment type...",
        width=300,
        on_submit=lambda e: perform_search()
    )
    search_button = ft.ElevatedButton(
        "🔍 Search",
        on_click=lambda e: perform_search()
    )

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
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    # App header with gradient
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=32, color=ft.Colors.WHITE),
                            ft.Text("Patient Portal", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.START),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.BLUE_600, ft.Colors.INDIGO_700],
                        ),
                        padding=ft.padding.symmetric(horizontal=20, vertical=15),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=8,
                            color=ft.Colors.BLACK38,
                            offset=ft.Offset(0, 2),
                        ),
                    ),
                    ft.Container(
                        content=content_area,
                        expand=True,
                        padding=ft.padding.all(20),
                        bgcolor=ft.Colors.GREY_50,
                    ),
                    nav_bar
                ], spacing=0),
                expand=True,
                bgcolor=ft.Colors.WHITE,
            )
        )
        show_home_view()

    async def change_view(index):
        if token["value"] is None and index != 0:
            content_area.content = ft.Column(
                [
                    ft.Text("Please login first", size=20),
                    ft.ElevatedButton(text="Go to Login", on_click=lambda _: show_login_view())
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            page.update()
            return
            
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

        # Modern welcome card
        welcome_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WAVING_HAND, size=32, color=ft.Colors.AMBER_600),
                    ft.Text("Welcome back, Patient!", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Text("Here's your health overview for today", size=16, color=ft.Colors.GREY_700),
            ], spacing=8),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.only(bottom=20),
        )

        # Stats cards
        stats_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=28, color=ft.Colors.BLUE_600),
                    ft.Text("Today's Appointments", size=12, color=ft.Colors.GREY_600),
                    ft.Text("Loading...", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=100,
                height=80,
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.GREEN_600),
                    ft.Text("Completed", size=12, color=ft.Colors.GREY_600),
                    ft.Text("Loading...", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=100,
                height=80,
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=28, color=ft.Colors.PURPLE_600),
                    ft.Text("Nearby Hospitals", size=12, color=ft.Colors.GREY_600),
                    ft.Text("Loading...", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_900),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=100,
                height=80,
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

        # Search section with modern styling
        search_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SEARCH, size=24, color=ft.Colors.BLUE_600),
                    ft.Text("Find Hospitals & Treatments", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED,
                        tooltip="Refresh hospital search",
                        on_click=lambda e: load_nearby(),
                        icon_color=ft.Colors.BLUE_600,
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=search_field,
                            expand=True,
                        ),
                        ft.ElevatedButton(
                            "🔍 Search",
                            on_click=lambda e: perform_search(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                            ),
                            height=48,
                        )
                    ]),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 2),
                    ),
                    border_radius=ft.border_radius.all(12),
                ),
            ], spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.symmetric(vertical=10),
        )

        content_area.content = ft.Column([
            welcome_card,
            stats_row,
            search_section,
            hospitals_list,
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        load_nearby()
        page.update()

    def show_appointments_view():
        current_view["value"] = "appointments"
        load_appointments()

        # Modern header
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=28, color=ft.Colors.BLUE_600),
                ft.Text("Today's Appointments", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
            margin=ft.margin.only(bottom=20),
        )

        content_area.content = ft.Column([
            header,
            appt_list,
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        page.update()

    def show_completed_view():
        current_view["value"] = "completed"
        load_completed_appointments()

        # Modern header
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=28, color=ft.Colors.GREEN_600),
                ft.Text("Completed Appointments", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2),
            ),
            margin=ft.margin.only(bottom=20),
        )

        content_area.content = ft.Column([
            header,
            completed_appt_list,
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        page.update()

    def show_profile_view():
        current_view["value"] = "profile"
        if not token["value"]:
            content_area.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PERSON_OFF, size=64, color=ft.Colors.GREY_400),
                    ft.Container(height=16),
                    ft.Text("Profile Access Required", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Text("Please login to view your profile information", size=16, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        "Go to Login",
                        on_click=lambda _: show_login_view(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            elevation=4,
                        ),
                        width=200,
                        height=45,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                padding=ft.padding.all(40),
                alignment=ft.alignment.center,
            )
            page.update()
            return

        content_area.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=28, color=ft.Colors.BLUE_600),
                    ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(color=ft.Colors.BLUE_600),
                        ft.Container(width=12),
                        ft.Text("Loading profile information...", size=16, color=ft.Colors.BLUE_600),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.all(20),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=ft.border_radius.all(12),
                ),
            ], spacing=0),
            padding=ft.padding.all(20),
        )
        page.update()
        load_profile_data()

    def load_profile_data():
        try:
            if not token["value"]:
                content_area.content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Please login to view your profile", color=ft.Colors.RED),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                page.update()
                return

            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/profile", headers=headers)

            if r.status_code == 200:
                profile = r.json()
                content_area.content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton(
                            "🔄 Refresh",
                            on_click=lambda _: load_profile_data(),
                            icon=ft.Icons.REFRESH
                        ),
                        ft.ElevatedButton(
                            "Logout",
                            on_click=logout,
                            icon=ft.Icons.LOGOUT
                        ),
                    ]),
                    ft.Divider(),
                    ft.Text("Patient Information:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE),
                                    ft.Text("Personal Details", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Text(f"👤 Name: {profile.get('full_name', 'Not provided')}", size=14),
                                ft.Text(f"📧 Email: {profile.get('email', 'Not provided')}", size=14),
                                ft.Text(f"🆔 User ID: {profile.get('user_id', 'Not provided')}", size=14),
                                ft.Text(f"👥 Type: {profile.get('user_type', 'Not provided')}", size=14),
                                ft.Text(f"📅 Member Since: User #{profile.get('created_at', 'Unknown')}", size=14),
                            ], spacing=5),
                            padding=15
                        ),
                        margin=ft.margin.symmetric(vertical=5)
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.SECURITY, color=ft.Colors.GREEN),
                                    ft.Text("Account Security", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Text("🔐 Password: ••••••••", size=14),
                                ft.Text("✅ Account Status: Active", size=14, color=ft.Colors.GREEN),
                                ft.Text("🔑 Authentication: JWT Token", size=14),
                            ], spacing=5),
                            padding=15
                        ),
                        margin=ft.margin.symmetric(vertical=5)
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.INFO, color=ft.Colors.ORANGE),
                                    ft.Text("App Information", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Text("📱 App Version: 1.0.0", size=14),
                                ft.Text("🏥 Healthcare Provider: Asupatri", size=14),
                                ft.Text("🌐 Service: Patient Portal", size=14),
                            ], spacing=5),
                            padding=15
                        ),
                        margin=ft.margin.symmetric(vertical=5)
                    ),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                page.update()
            else:
                content_area.content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"Error loading profile: {r.json().get('message', 'Unknown error')}", color=ft.Colors.RED),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                page.update()
        except Exception as ex:
            content_area.content = ft.Column([
                ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"Error: {str(ex)}", color=ft.Colors.RED),
            ], expand=True, scroll=ft.ScrollMode.AUTO)
            page.update()

    def logout(e):
        token["value"] = None
        user_id["value"] = None
        page.clean()
        show_login_view()

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

    def scrape_nearby_hospitals(lat, lon):
        """Scrape nearby hospitals from web sources"""
        hospitals = []
        
        print(f"Scraping hospitals for location: {lat}, {lon}")
        
        try:
            # Use Overpass API (OpenStreetMap) - free and no API keys required
            overpass_url = "http://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json][timeout:30];
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
            
            print(f"Making request to Overpass API...")
            response = requests.get(overpass_url, params={'data': overpass_query}, timeout=15)
            print(f"Overpass API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                print(f"Found {len(elements)} hospital elements from Overpass API")
                
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
                return hospitals[:10]  # Return top 10 nearest
            
        except Exception as ex:
            print(f"Overpass API scraping error: {ex}")
        
        # Fallback to our database hospitals
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

    def search_hospitals_and_treatments(query, user_lat, user_lon):
        """Search hospitals by name/address and doctors by specialization"""
        results = []
        query_lower = query.lower()
        db_hospitals = []

        try:
            # Search hospitals from database
            r = requests.get(f"{API_BASE}/hospitals", timeout=5)
            if r.status_code == 200:
                db_hospitals = r.json().get("hospitals", [])
                for h in db_hospitals:
                    # Check if query matches hospital name or address
                    if (query_lower in h['name'].lower() or
                        query_lower in h['address'].lower()):
                        distance = calculate_distance(user_lat, user_lon, h.get('latitude'), h.get('longitude'))
                        results.append({
                            'name': h['name'],
                            'address': h['address'],
                            'phone': h.get('phone', 'Phone not available'),
                            'distance_km': round(distance, 2) if distance != float("inf") else None,
                            'latitude': h.get('latitude'),
                            'longitude': h.get('longitude'),
                            'fee_details': h.get('fee_details', 'Contact hospital for pricing'),
                            'match_type': 'hospital'
                        })

            # Search doctors by specialization
            # First get all doctors, then filter by specialization
            try:
                # We need to get doctors - let's try to get them via hospitals
                doctor_hospitals = []
                for h in db_hospitals:
                    try:
                        r = requests.get(f"{API_BASE}/doctors/hospital/{h['hospital_id']}", timeout=3)
                        if r.status_code == 200:
                            doctors = r.json().get("doctors", [])
                            for d in doctors:
                                if query_lower in d['specialization'].lower():
                                    # Add this hospital if doctor specialization matches
                                    distance = calculate_distance(user_lat, user_lon, h.get('latitude'), h.get('longitude'))
                                    doctor_hospitals.append({
                                        'name': h['name'],
                                        'address': h['address'],
                                        'phone': h.get('phone', 'Phone not available'),
                                        'distance_km': round(distance, 2) if distance != float("inf") else None,
                                        'latitude': h.get('latitude'),
                                        'longitude': h.get('longitude'),
                                        'fee_details': h.get('fee_details', f"Specialization: {d['specialization']}"),
                                        'match_type': 'treatment',
                                        'doctor_name': d.get('user', {}).get('full_name', 'Doctor'),
                                        'specialization': d['specialization']
                                    })
                    except Exception as e:
                        print(f"Error getting doctors for hospital {h['hospital_id']}: {e}")
                        continue

                results.extend(doctor_hospitals)

            except Exception as e:
                print(f"Error searching doctors: {e}")

        except Exception as ex:
            print(f"Database search error: {ex}")

        # Remove duplicates based on hospital name
        seen = set()
        unique_results = []
        for r in results:
            key = r['name'].lower()
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        # Sort by distance
        unique_results.sort(key=lambda x: x.get('distance_km', float('inf')))

        return unique_results[:20]  # Return top 20 results

    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        if None in (lat1, lon1, lat2, lon2):
            return float("inf")
        
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km

    def load_nearby(search_query=None):
        hospitals_list.controls.clear()
        if search_query:
            hospitals_list.controls.append(ft.Text(f"🔍 Searching for '{search_query}'...", color=ft.Colors.BLUE))
        else:
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
                if search_query:
                    hospitals_list.controls.append(ft.Text(f"🔍 Searching for '{search_query}'...", color=ft.Colors.BLUE))
                else:
                    hospitals_list.controls.append(ft.Text("🔍 Searching for nearby hospitals...", color=ft.Colors.BLUE))
                page.update()
                
                print(f"Starting hospital search for coordinates: {lat}, {lon}")
                if search_query:
                    # Search mode: search hospitals and treatments
                    hospitals = search_hospitals_and_treatments(search_query, lat, lon)
                else:
                    # Normal mode: scrape nearby hospitals
                    hospitals = scrape_nearby_hospitals(lat, lon)
                print(f"Hospital search completed. Found {len(hospitals)} hospitals")
                
                hospitals_list.controls.clear()
                
                if hospitals:
                    if search_query:
                        hospitals_list.controls.append(ft.Text(f"🔍 Found {len(hospitals)} results for '{search_query}':", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
                        hospitals_list.controls.append(ft.Text(f"📍 Results sorted by distance from your location", size=12, color=ft.Colors.BLUE))
                    else:
                        hospitals_list.controls.append(ft.Text(f"🏥 Found {len(hospitals)} nearby hospitals:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN))
                        hospitals_list.controls.append(ft.Text(f"📍 Based on your location: {lat:.4f}, {lon:.4f}", size=12, color=ft.Colors.BLUE))
                    
                    for i, h in enumerate(hospitals, 1):
                         distance = h.get('distance_km', '?')
                         phone = h.get('phone', 'N/A')
                         hospitals_list.controls.append(
                             ft.Container(
                                 content=ft.Column([
                                     ft.Row([
                                         ft.Container(
                                             content=ft.Text(f"#{i}", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                             bgcolor=ft.Colors.BLUE_600,
                                             border_radius=ft.border_radius.all(8),
                                             padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                             alignment=ft.alignment.center,
                                         ),
                                         ft.Container(width=10),
                                         ft.Text(h['name'], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True),
                                         ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=24, color=ft.Colors.BLUE_600),
                                     ], alignment=ft.MainAxisAlignment.START),
                                     ft.Container(height=8),
                                     ft.Row([
                                         ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.GREY_600),
                                         ft.Text(h['address'], size=14, color=ft.Colors.GREY_700, expand=True),
                                     ], spacing=5),
                                     ft.Container(height=4),
                                     ft.Row([
                                         ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                                         ft.Text(phone, size=14, color=ft.Colors.GREY_700),
                                     ], spacing=5),
                                     ft.Container(height=4),
                                     ft.Row([
                                         ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREY_600),
                                         ft.Text(h.get('fee_details', 'Contact for pricing'), size=14, color=ft.Colors.GREY_700),
                                     ], spacing=5),
                                     ft.Container(height=8),
                                     ft.Row([
                                         ft.Container(
                                             content=ft.Row([
                                                 ft.Icon(ft.Icons.DIRECTIONS, size=14, color=ft.Colors.BLUE_600),
                                                 ft.Text(f"{distance} km away", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600),
                                             ], spacing=4),
                                             bgcolor=ft.Colors.BLUE_50,
                                             border_radius=ft.border_radius.all(6),
                                             padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                         ),
                                         # Show specialization info for treatment matches
                                         ft.Container(
                                             content=ft.Row([
                                                 ft.Icon(ft.Icons.MEDICAL_SERVICES, size=14, color=ft.Colors.GREEN_600),
                                                 ft.Text(h.get('specialization', ''), size=14, color=ft.Colors.GREEN_700),
                                             ], spacing=4),
                                             bgcolor=ft.Colors.GREEN_50,
                                             border_radius=ft.border_radius.all(6),
                                             padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                         ) if h.get('match_type') == 'treatment' and h.get('specialization') else ft.Container(),
                                     ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                 ], spacing=0),
                                 padding=ft.padding.all(16),
                                 bgcolor=ft.Colors.WHITE,
                                 border_radius=ft.border_radius.all(12),
                                 shadow=ft.BoxShadow(
                                     spread_radius=1,
                                     blur_radius=8,
                                     color=ft.Colors.BLACK12,
                                     offset=ft.Offset(0, 2),
                                 ),
                                 margin=ft.margin.symmetric(vertical=6),
                             )
                         )
                else:
                    if search_query:
                        hospitals_list.controls.append(ft.Text(f"❌ No results found for '{search_query}'", color=ft.Colors.ORANGE, size=16))
                        hospitals_list.controls.append(ft.Text("💡 Try different keywords or check spelling", size=12))
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
                         ft.Container(
                             content=ft.Column([
                                 ft.Row([
                                     ft.Container(
                                         content=ft.Text(f"#{i}", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                         bgcolor=ft.Colors.ORANGE_600,
                                         border_radius=ft.border_radius.all(8),
                                         padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                         alignment=ft.alignment.center,
                                     ),
                                     ft.Container(width=10),
                                     ft.Text(h['name'], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_900, expand=True),
                                     ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=24, color=ft.Colors.ORANGE_600),
                                 ], alignment=ft.MainAxisAlignment.START),
                                 ft.Container(height=8),
                                 ft.Row([
                                     ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.GREY_600),
                                     ft.Text(h['address'], size=14, color=ft.Colors.GREY_700, expand=True),
                                 ], spacing=5),
                                 ft.Container(height=4),
                                 ft.Row([
                                     ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                                     ft.Text(h['phone'], size=14, color=ft.Colors.GREY_700),
                                 ], spacing=5),
                                 ft.Container(height=4),
                                 ft.Row([
                                     ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREY_600),
                                     ft.Text(h.get('fee_details', 'Contact for pricing'), size=14, color=ft.Colors.GREY_700),
                                 ], spacing=5),
                                 ft.Container(height=8),
                                 ft.Container(
                                     content=ft.Row([
                                         ft.Icon(ft.Icons.DIRECTIONS, size=14, color=ft.Colors.ORANGE_600),
                                         ft.Text(f"{h['distance_km']} km away", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600),
                                     ], spacing=4),
                                     bgcolor=ft.Colors.ORANGE_50,
                                     border_radius=ft.border_radius.all(6),
                                     padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                 ),
                             ], spacing=0),
                             padding=ft.padding.all(16),
                             bgcolor=ft.Colors.WHITE,
                             border_radius=ft.border_radius.all(12),
                             shadow=ft.BoxShadow(
                                 spread_radius=1,
                                 blur_radius=8,
                                 color=ft.Colors.BLACK12,
                                 offset=ft.Offset(0, 2),
                             ),
                             margin=ft.margin.symmetric(vertical=6),
                         )
                     )
                
        except Exception as ex:
            print(f"Error in load_nearby: {ex}")
            hospitals_list.controls.clear()
            hospitals_list.controls.append(ft.Text(f"❌ Error: {str(ex)}", color=ft.Colors.RED, size=16))
            hospitals_list.controls.append(ft.Text("💡 Please check your internet connection", size=12))
            hospitals_list.controls.append(ft.Text("🔄 Try clicking the refresh button to retry", size=12))
        
        page.update()

    def perform_search():
        query = search_field.value.strip() if search_field.value else ""
        if query:
            load_nearby(search_query=query)
        else:
            load_nearby()

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
                        # Status color mapping
                        status_color = {
                            'Scheduled': ft.Colors.BLUE_600,
                            'Confirmed': ft.Colors.GREEN_600,
                            'Pending': ft.Colors.ORANGE_600,
                            'Cancelled': ft.Colors.RED_600,
                        }.get(a['status'], ft.Colors.GREY_600)

                        status_bg = {
                            'Scheduled': ft.Colors.BLUE_50,
                            'Confirmed': ft.Colors.GREEN_50,
                            'Pending': ft.Colors.ORANGE_50,
                            'Cancelled': ft.Colors.RED_50,
                        }.get(a['status'], ft.Colors.GREY_50)

                        appt_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.Icons.EVENT, size=24, color=status_color),
                                        ft.Text(f"{a['date']} at {a['time']}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900, expand=True),
                                        ft.Container(
                                            content=ft.Text(a['status'], size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                            bgcolor=status_color,
                                            border_radius=ft.border_radius.all(12),
                                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(f"Patient: {a.get('patient_name', 'Unknown')}", size=14, color=ft.Colors.GREY_700),
                                    ], spacing=5),
                                    ft.Container(height=4),
                                    ft.Row([
                                        ft.Icon(ft.Icons.MEDICAL_SERVICES, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(f"Type: {a.get('appointment_type', 'General')}", size=14, color=ft.Colors.GREY_700),
                                    ], spacing=5),
                                ], spacing=0),
                                padding=ft.padding.all(16),
                                bgcolor=ft.Colors.WHITE,
                                border_radius=ft.border_radius.all(12),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=8,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 2),
                                ),
                                margin=ft.margin.symmetric(vertical=6),
                            )
                        )
            else:
                # Empty state
                appt_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.EVENT_BUSY, size=64, color=ft.Colors.GREY_400),
                            ft.Container(height=16),
                            ft.Text("No appointments scheduled for today", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.Text("Your upcoming appointments will appear here", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        padding=ft.padding.all(40),
                        alignment=ft.alignment.center,
                    )
                )
        else:
            appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED_400),
                        ft.Container(height=16),
                        ft.Text("Failed to load appointments", size=16, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
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
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=ft.Colors.GREEN_600),
                                    ft.Text(f"{a['date']} at {a['time']}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900, expand=True),
                                    ft.Container(
                                        content=ft.Text("Completed", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        bgcolor=ft.Colors.GREEN_600,
                                        border_radius=ft.border_radius.all(12),
                                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                    ),
                                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                                ft.Container(height=8),
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_600),
                                    ft.Text(f"Patient: {a.get('patient_name', 'Unknown')}", size=14, color=ft.Colors.GREY_700),
                                ], spacing=5),
                                ft.Container(height=4),
                                ft.Row([
                                    ft.Icon(ft.Icons.MEDICAL_SERVICES, size=16, color=ft.Colors.GREY_600),
                                    ft.Text(f"Type: {a.get('appointment_type', 'General')}", size=14, color=ft.Colors.GREY_700),
                                ], spacing=5),
                            ], spacing=0),
                            padding=ft.padding.all(16),
                            bgcolor=ft.Colors.WHITE,
                            border_radius=ft.border_radius.all(12),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=8,
                                color=ft.Colors.BLACK12,
                                offset=ft.Offset(0, 2),
                            ),
                            margin=ft.margin.symmetric(vertical=6),
                        )
                    )
            else:
                # Empty state
                completed_appt_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=64, color=ft.Colors.GREY_400),
                            ft.Container(height=16),
                            ft.Text("No completed appointments found", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.Text("Your completed appointments will appear here", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        padding=ft.padding.all(40),
                        alignment=ft.alignment.center,
                    )
                )
        else:
            completed_appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED_400),
                        ft.Container(height=16),
                        ft.Text("Failed to load completed appointments", size=16, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_completed_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
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

        # Modern gradient background
        gradient_bg = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_400, ft.Colors.INDIGO_600, ft.Colors.PURPLE_600],
            ),
            expand=True,
        )

        # Modern login card
        login_card = ft.Container(
            content=ft.Column([
                # Header with icon
                ft.Row([
                    ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=48, color=ft.Colors.WHITE),
                    ft.Column([
                        ft.Text("Patient Portal", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Your Health, Our Priority", size=14, color=ft.Colors.WHITE70),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),

                ft.Container(height=30),  # Spacer

                # Login/Signup tabs with modern styling
                ft.Container(
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        indicator_color=ft.Colors.WHITE,
                        label_color=ft.Colors.WHITE70,
                        unselected_label_color=ft.Colors.WHITE54,
                        tabs=[
                             ft.Tab(
                                 text="Login",
                                 content=ft.Container(
                                     content=ft.Column([
                                         ft.Container(height=20),
                                         ft.Text("Welcome Back", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                         ft.Container(height=10),
                                         email,
                                         ft.Container(height=10),
                                         password,
                                         ft.Container(height=20),
                                         ft.ElevatedButton(
                                             "Login",
                                             on_click=do_login,
                                             width=250,
                                             height=50,
                                             style=ft.ButtonStyle(
                                                 bgcolor=ft.Colors.WHITE,
                                                 color=ft.Colors.BLUE_600,
                                                 elevation=8,
                                                 shadow_color=ft.Colors.BLACK38,
                                             ),
                                             icon=ft.Icons.LOGIN,
                                         ),
                                         ft.Container(height=10),
                                         output,
                                     ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                     padding=ft.padding.all(20),
                                     bgcolor=ft.Colors.WHITE,
                                     border_radius=12,
                                 )
                             ),
                             ft.Tab(
                                 text="Sign Up",
                                 content=ft.Container(
                                     content=ft.Column([
                                         ft.Container(height=20),
                                         ft.Text("Create Your Account", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                         ft.Container(height=10),
                                         signup_full_name,
                                         ft.Container(height=10),
                                         signup_email,
                                         ft.Container(height=10),
                                         signup_password,
                                         ft.Container(height=10),
                                         signup_confirm_password,
                                         ft.Container(height=20),
                                         ft.ElevatedButton(
                                             "Create Account",
                                             on_click=do_signup,
                                             width=250,
                                             height=50,
                                             style=ft.ButtonStyle(
                                                 bgcolor=ft.Colors.WHITE,
                                                 color=ft.Colors.BLUE_600,
                                                 elevation=8,
                                                 shadow_color=ft.Colors.BLACK38,
                                             ),
                                             icon=ft.Icons.PERSON_ADD,
                                         ),
                                         ft.Container(height=10),
                                         signup_output,
                                     ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                     padding=ft.padding.all(20),
                                     bgcolor=ft.Colors.WHITE,
                                     border_radius=12,
                                 )
                             ),
                        ],
                    ),
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=16,
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=16,
                        color=ft.Colors.BLACK38,
                        offset=ft.Offset(0, 4),
                    ),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=ft.padding.all(30),
        )

        page.add(
            ft.Stack([
                gradient_bg,
                ft.Container(
                    content=login_card,
                    alignment=ft.alignment.center,
                    padding=ft.padding.all(20),
                ),
            ], expand=True)
        )
        page.update()

    # Initialize with login view
    show_login_view()

ft.app(target=main)
