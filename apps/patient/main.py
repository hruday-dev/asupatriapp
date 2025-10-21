import flet as ft
import requests
import json
from datetime import datetime

# Update this with your Render URL after deployment
API_BASE = "https://asupatri-backend.onrender.com/api"
# For local development, use: API_BASE = "http://127.0.0.1:10000/api"

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
            r = requests.post(f"{API_BASE}/login", json={"email": email.value, "password": password.value}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                output.value = "Logged in successfully!"
                output.color = ft.colors.GREEN
                page.update()
                show_main_app()
            else:
                error_msg = "Login failed"
                try:
                    error_data = r.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    if r.status_code >= 500:
                        error_msg = "Server error. Please try again later."
                    elif r.status_code == 404:
                        error_msg = "Login endpoint not found. Check API URL."
                output.value = error_msg
                output.color = ft.colors.RED
                page.update()
        except requests.exceptions.RequestException as ex:
            output.value = f"Network error: {str(ex)}"
            output.color = ft.colors.RED
            page.update()
        except Exception as ex:
            output.value = f"Error: {str(ex)}"
            output.color = ft.colors.RED
            page.update()

    def show_main_app():
        page.clean()
        
        # Navigation components with modern styling (compatible with older Flet versions)
        nav_items = []
        
        def create_nav_item(icon, label, index):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=24, color=ft.colors.BLUE_600 if index == 0 else ft.colors.GREY_600),
                    ft.Text(label, size=12, color=ft.colors.BLUE_600 if index == 0 else ft.colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                bgcolor=ft.colors.BLUE_50 if index == 0 else None,
                border_radius=ft.border_radius.all(8),
                ink=True,
                on_click=lambda _: change_view(index),
            )
        
        nav_items = [
            create_nav_item(ft.icons.HOME_ROUNDED, "Home", 0),
            create_nav_item(ft.icons.CALENDAR_TODAY_ROUNDED, "Appointments", 1),
            create_nav_item(ft.icons.CHECK_CIRCLE_ROUNDED, "Completed", 2),
            create_nav_item(ft.icons.PERSON_ROUNDED, "Profile", 3),
        ]
        
        nav_bar = ft.Container(
            content=ft.Row(nav_items, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
            padding=ft.padding.all(10),
            bgcolor=ft.colors.WHITE,
            shadow_color=ft.colors.BLACK26,
            elevation=8,
        )
        
        page.add(
            ft.Container(
                content=ft.Column([
                    # App header with gradient
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.HEALTH_AND_SAFETY, size=32, color=ft.colors.WHITE),
                            ft.Text("Patient Portal", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.START),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.colors.BLUE_600, ft.colors.INDIGO_700],
                        ),
                        padding=ft.padding.symmetric(horizontal=20, vertical=15),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=8,
                            color=ft.colors.BLACK38,
                            offset=ft.Offset(0, 2),
                        ),
                    ),
                    ft.Container(
                        content=content_area,
                        expand=True,
                        padding=ft.padding.all(20),
                        bgcolor=ft.colors.GREY_50,
                    ),
                    nav_bar
                ], spacing=0),
                expand=True,
                bgcolor=ft.colors.WHITE,
            )
        )
        show_home_view()

    def change_view(index):
        # Update nav items styling
        for i, nav_item in enumerate(nav_items):
            if i == index:
                nav_item.bgcolor = ft.colors.BLUE_50
                nav_item.content.controls[0].color = ft.colors.BLUE_600
                nav_item.content.controls[1].color = ft.colors.BLUE_600
            else:
                nav_item.bgcolor = None
                nav_item.content.controls[0].color = ft.colors.GREY_600
                nav_item.content.controls[1].color = ft.colors.GREY_600
        
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
                    ft.Icon(ft.icons.WAVING_HAND, size=32, color=ft.colors.AMBER_600),
                    ft.Text("Welcome back, Patient!", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Text("Here's your health overview for today", size=16, color=ft.colors.GREY_700),
            ], spacing=8),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.only(bottom=20),
        )

        # Search section with modern styling
        search_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SEARCH, size=24, color=ft.colors.BLUE_600),
                    ft.Text("Find Hospitals & Treatments", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                    ft.IconButton(
                        icon=ft.icons.REFRESH_ROUNDED,
                        tooltip="Refresh hospital search",
                        on_click=lambda e: load_nearby(),
                        icon_color=ft.colors.BLUE_600,
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
                                bgcolor=ft.colors.BLUE_600,
                                color=ft.colors.WHITE,
                            ),
                            height=48,
                        )
                    ]),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.colors.BLACK12,
                        offset=ft.Offset(0, 2),
                    ),
                    border_radius=ft.border_radius.all(12),
                ),
            ], spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.symmetric(vertical=10),
        )

        content_area.content = ft.Column([
            welcome_card,
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
                ft.Icon(ft.icons.CALENDAR_TODAY, size=28, color=ft.colors.BLUE_600),
                ft.Text("Today's Appointments", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.colors.BLACK12,
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
                ft.Icon(ft.icons.CHECK_CIRCLE, size=28, color=ft.colors.GREEN_600),
                ft.Text("Completed Appointments", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_900),
            ], alignment=ft.MainAxisAlignment.START, spacing=10),
            padding=ft.padding.all(20),
            bgcolor=ft.colors.WHITE,
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.colors.BLACK12,
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
                    ft.Icon(ft.icons.PERSON_OFF, size=64, color=ft.colors.GREY_400),
                    ft.Container(height=16),
                    ft.Text("Profile Access Required", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_700, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=8),
                    ft.Text("Please login to view your profile information", size=16, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.ElevatedButton(
                        "Go to Login",
                        on_click=lambda _: show_login_view(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_600,
                            color=ft.colors.WHITE,
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
                    ft.Icon(ft.icons.PERSON, size=28, color=ft.colors.BLUE_600),
                    ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(color=ft.colors.BLUE_600),
                        ft.Container(width=12),
                        ft.Text("Loading profile information...", size=16, color=ft.colors.BLUE_600),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.padding.all(20),
                    bgcolor=ft.colors.BLUE_50,
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
                    ft.Text("Please login to view your profile", color=ft.colors.RED),
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
                            icon=ft.icons.REFRESH
                        ),
                        ft.ElevatedButton(
                            "Logout",
                            on_click=logout,
                            icon=ft.icons.LOGOUT
                        ),
                    ]),
                    ft.Divider(),
                    ft.Text("Patient Information:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.icons.PERSON, color=ft.colors.BLUE),
                                    ft.Text("Personal Details", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Text(f"👤 Name: {profile.get('full_name', 'Not provided')}", size=14),
                                ft.Text(f"📧 Email: {profile.get('email', 'Not provided')}", size=14),
                                ft.Text(f"🆔 User ID: {profile.get('user_id', 'Not provided')}", size=14),
                                ft.Text(f"👥 Type: {profile.get('user_type', 'Not provided')}", size=14),
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
                    ft.Text(f"Error loading profile: {r.json().get('message', 'Unknown error')}", color=ft.colors.RED),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                page.update()
        except Exception as ex:
            content_area.content = ft.Column([
                ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"Error: {str(ex)}", color=ft.colors.RED),
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
                "https://ipapi.co/json/",
                "http://ip-api.com/json/",
                "http://ipinfo.io/json"
            ]
            
            for service in services:
                try:
                    print(f"Trying location service: {service}")
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Location service response: {data}")
                        
                        # Handle different response formats
                        if service == "https://ipapi.co/json/":
                            if 'latitude' in data and 'longitude' in data:
                                user_location["lat"] = data.get('latitude')
                                user_location["lon"] = data.get('longitude')
                                print(f"Got location from ipapi.co: {user_location}")
                                return True
                        elif service == "http://ip-api.com/json/":
                            if data.get('status') == 'success':
                                user_location["lat"] = data.get('lat')
                                user_location["lon"] = data.get('lon')
                                print(f"Got location from ip-api: {user_location}")
                                return True
                        elif service == "http://ipinfo.io/json":
                            if 'loc' in data:
                                lat, lon = data['loc'].split(',')
                                user_location["lat"] = float(lat)
                                user_location["lon"] = float(lon)
                                print(f"Got location from ipinfo: {user_location}")
                                return True
                except requests.exceptions.RequestException as e:
                    print(f"Network error with {service}: {e}")
                    continue
                except Exception as e:
                    print(f"Error with {service}: {e}")
                    continue
            
            # Fallback to demo coordinates (Pune, India)
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
            hospitals_list.controls.append(ft.Text(f"🔍 Searching for '{search_query}'...", color=ft.colors.BLUE))
        else:
            hospitals_list.controls.append(ft.Text("🌍 Getting your location...", color=ft.colors.BLUE))
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
                hospitals_list.controls.append(ft.Text(f"📍 Your Location: {lat:.4f}, {lon:.4f}", color=ft.colors.GREEN, size=14))
                if search_query:
                    hospitals_list.controls.append(ft.Text(f"🔍 Searching for '{search_query}'...", color=ft.colors.BLUE))
                else:
                    hospitals_list.controls.append(ft.Text("🔍 Searching for nearby hospitals...", color=ft.colors.BLUE))
                page.update()
                
                # Use sample hospitals for now
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
                
                hospitals_list.controls.clear()
                hospitals_list.controls.append(ft.Text(f"🏥 Found {len(sample_hospitals)} nearby hospitals:", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN))
                hospitals_list.controls.append(ft.Text(f"📍 Based on your location: {lat:.4f}, {lon:.4f}", size=12, color=ft.colors.BLUE))
                
                for i, h in enumerate(sample_hospitals, 1):
                    distance = h.get('distance_km', '?')
                    phone = h.get('phone', 'N/A')
                    hospitals_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"#{i}", size=12, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                                        bgcolor=ft.colors.BLUE_600,
                                        border_radius=ft.border_radius.all(8),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Container(width=10),
                                    ft.Text(h['name'], size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900, expand=True),
                                    ft.Icon(ft.icons.LOCAL_HOSPITAL, size=24, color=ft.colors.BLUE_600),
                                ], alignment=ft.MainAxisAlignment.START),
                                ft.Container(height=8),
                                ft.Row([
                                    ft.Icon(ft.icons.LOCATION_ON, size=16, color=ft.colors.GREY_600),
                                    ft.Text(h['address'], size=14, color=ft.colors.GREY_700, expand=True),
                                ], spacing=5),
                                ft.Container(height=4),
                                ft.Row([
                                    ft.Icon(ft.icons.PHONE, size=16, color=ft.colors.GREY_600),
                                    ft.Text(phone, size=14, color=ft.colors.GREY_700),
                                ], spacing=5),
                                ft.Container(height=4),
                                ft.Row([
                                    ft.Icon(ft.icons.ATTACH_MONEY, size=16, color=ft.colors.GREY_600),
                                    ft.Text(h.get('fee_details', 'Contact for pricing'), size=14, color=ft.colors.GREY_700),
                                ], spacing=5),
                                ft.Container(height=8),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.icons.DIRECTIONS, size=14, color=ft.colors.BLUE_600),
                                        ft.Text(f"{distance} km away", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_600),
                                    ], spacing=4),
                                    bgcolor=ft.colors.BLUE_50,
                                    border_radius=ft.border_radius.all(6),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                ),
                            ], spacing=0),
                            padding=ft.padding.all(16),
                            bgcolor=ft.colors.WHITE,
                            border_radius=ft.border_radius.all(12),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=8,
                                color=ft.colors.BLACK12,
                                offset=ft.Offset(0, 2),
                            ),
                            margin=ft.margin.symmetric(vertical=6),
                        )
                    )
            else:
                hospitals_list.controls.clear()
                hospitals_list.controls.append(ft.Text("❌ Could not get your location", color=ft.colors.RED, size=16))
                hospitals_list.controls.append(ft.Text("📍 Using sample hospitals instead...", color=ft.colors.ORANGE))
                
        except Exception as ex:
            print(f"Error in load_nearby: {ex}")
            hospitals_list.controls.clear()
            hospitals_list.controls.append(ft.Text(f"❌ Error: {str(ex)}", color=ft.colors.RED, size=16))
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
        
        if not token["value"] or not user_id["value"]:
            appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.LOGIN_REQUIRED, size=48, color=ft.colors.ORANGE_400),
                        ft.Container(height=16),
                        ft.Text("Please login to view appointments", size=16, color=ft.colors.ORANGE_600, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
            page.update()
            return
        
        try:
            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/appointments/{user_id['value']}?today=true", headers=headers, timeout=10)
            
            if r.status_code == 200:
                appointments = r.json().get("appointments", [])
                active_appointments = [a for a in appointments if a.get('status') != 'Completed']
                
                if active_appointments:
                    for a in active_appointments:
                        status_color = {
                            'Scheduled': ft.colors.BLUE_600,
                            'Confirmed': ft.colors.GREEN_600,
                            'Pending': ft.colors.ORANGE_600,
                            'Cancelled': ft.colors.RED_600,
                        }.get(a.get('status'), ft.colors.GREY_600)

                        appt_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.icons.EVENT, size=24, color=status_color),
                                        ft.Text(f"{a.get('date', 'Unknown date')} at {a.get('time', 'Unknown time')}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900, expand=True),
                                        ft.Container(
                                            content=ft.Text(a.get('status', 'Unknown'), size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                            bgcolor=status_color,
                                            border_radius=ft.border_radius.all(12),
                                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Icon(ft.icons.LOCAL_HOSPITAL, size=16, color=ft.colors.GREY_600),
                                        ft.Text(f"Hospital: {a.get('hospital_name', 'Not specified')}", size=14, color=ft.colors.GREY_700),
                                    ], spacing=5),
                                ], spacing=0),
                                padding=ft.padding.all(16),
                                bgcolor=ft.colors.WHITE,
                                border_radius=ft.border_radius.all(12),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=8,
                                    color=ft.colors.BLACK12,
                                    offset=ft.Offset(0, 2),
                                ),
                                margin=ft.margin.symmetric(vertical=6),
                            )
                        )
                else:
                    appt_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.EVENT_BUSY, size=64, color=ft.colors.GREY_400),
                                ft.Container(height=16),
                                ft.Text("No appointments scheduled for today", size=18, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=8),
                                ft.Text("Your upcoming appointments will appear here", size=14, color=ft.colors.GREY_500, text_align=ft.TextAlign.CENTER),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                            padding=ft.padding.all(40),
                            alignment=ft.alignment.center,
                        )
                    )
            else:
                error_msg = "Failed to load appointments"
                if r.status_code == 401:
                    error_msg = "Session expired. Please login again."
                elif r.status_code == 404:
                    error_msg = "Appointments endpoint not found."
                elif r.status_code >= 500:
                    error_msg = "Server error. Please try again later."
                
                appt_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.ERROR, size=48, color=ft.colors.RED_400),
                            ft.Container(height=16),
                            ft.Text(error_msg, size=16, color=ft.colors.RED_600, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.ElevatedButton(
                                "Retry",
                                on_click=lambda e: load_appointments(),
                                style=ft.ButtonStyle(bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        padding=ft.padding.all(40),
                        alignment=ft.alignment.center,
                    )
                )
        except requests.exceptions.RequestException as ex:
            appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WIFI_OFF, size=48, color=ft.colors.ORANGE_400),
                        ft.Container(height=16),
                        ft.Text("Network error. Please check your connection.", size=16, color=ft.colors.ORANGE_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE_600, color=ft.colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
        except Exception as ex:
            appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.BUG_REPORT, size=48, color=ft.colors.RED_400),
                        ft.Container(height=16),
                        ft.Text(f"Error: {str(ex)}", size=16, color=ft.colors.RED_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
        page.update()

    def load_completed_appointments():
        completed_appt_list.controls.clear()
        
        if not token["value"] or not user_id["value"]:
            completed_appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.LOGIN_REQUIRED, size=48, color=ft.colors.ORANGE_400),
                        ft.Container(height=16),
                        ft.Text("Please login to view appointments", size=16, color=ft.colors.ORANGE_600, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
            page.update()
            return
        
        try:
            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/appointments/{user_id['value']}", headers=headers, timeout=10)
            
            if r.status_code == 200:
                appointments = r.json().get("appointments", [])
                completed_appts = [a for a in appointments if a.get('status') == 'Completed']
                
                if completed_appts:
                    for a in completed_appts:
                        completed_appt_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Icon(ft.icons.CHECK_CIRCLE, size=24, color=ft.colors.GREEN_600),
                                        ft.Text(f"{a.get('date', 'Unknown date')} at {a.get('time', 'Unknown time')}", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_900, expand=True),
                                        ft.Container(
                                            content=ft.Text("Completed", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                                            bgcolor=ft.colors.GREEN_600,
                                            border_radius=ft.border_radius.all(12),
                                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                                    ft.Container(height=8),
                                    ft.Row([
                                        ft.Icon(ft.icons.LOCAL_HOSPITAL, size=16, color=ft.colors.GREY_600),
                                        ft.Text(f"Hospital: {a.get('hospital_name', 'Not specified')}", size=14, color=ft.colors.GREY_700),
                                    ], spacing=5),
                                ], spacing=0),
                                padding=ft.padding.all(16),
                                bgcolor=ft.colors.WHITE,
                                border_radius=ft.border_radius.all(12),
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=8,
                                    color=ft.colors.BLACK12,
                                    offset=ft.Offset(0, 2),
                                ),
                                margin=ft.margin.symmetric(vertical=6),
                            )
                        )
                else:
                    completed_appt_list.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=64, color=ft.colors.GREY_400),
                                ft.Container(height=16),
                                ft.Text("No completed appointments found", size=18, color=ft.colors.GREY_600, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=8),
                                ft.Text("Your completed appointments will appear here", size=14, color=ft.colors.GREY_500, text_align=ft.TextAlign.CENTER),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                            padding=ft.padding.all(40),
                            alignment=ft.alignment.center,
                        )
                    )
            else:
                error_msg = "Failed to load completed appointments"
                if r.status_code == 401:
                    error_msg = "Session expired. Please login again."
                elif r.status_code == 404:
                    error_msg = "Appointments endpoint not found."
                elif r.status_code >= 500:
                    error_msg = "Server error. Please try again later."
                
                completed_appt_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.ERROR, size=48, color=ft.colors.RED_400),
                            ft.Container(height=16),
                            ft.Text(error_msg, size=16, color=ft.colors.RED_600, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.ElevatedButton(
                                "Retry",
                                on_click=lambda e: load_completed_appointments(),
                                style=ft.ButtonStyle(bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        padding=ft.padding.all(40),
                        alignment=ft.alignment.center,
                    )
                )
        except requests.exceptions.RequestException as ex:
            completed_appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WIFI_OFF, size=48, color=ft.colors.ORANGE_400),
                        ft.Container(height=16),
                        ft.Text("Network error. Please check your connection.", size=16, color=ft.colors.ORANGE_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_completed_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE_600, color=ft.colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
        except Exception as ex:
            completed_appt_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.BUG_REPORT, size=48, color=ft.colors.RED_400),
                        ft.Container(height=16),
                        ft.Text(f"Error: {str(ex)}", size=16, color=ft.colors.RED_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_completed_appointments(),
                            style=ft.ButtonStyle(bgcolor=ft.colors.RED_600, color=ft.colors.WHITE),
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
                signup_output.color = ft.colors.RED
                page.update()
                return
            
            # Validate required fields
            if not all([signup_email.value, signup_password.value, signup_full_name.value]):
                signup_output.value = "Please fill in all fields"
                signup_output.color = ft.colors.RED
                page.update()
                return
            
            r = requests.post(f"{API_BASE}/register", json={
                "email": signup_email.value,
                "password": signup_password.value,
                "user_type": "Patient",
                "full_name": signup_full_name.value
            }, timeout=10)
            
            if r.status_code == 201:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                signup_output.value = "Account created successfully!"
                signup_output.color = ft.colors.GREEN
                page.update()
                show_main_app()
            else:
                error_msg = "Registration failed"
                try:
                    error_data = r.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    if r.status_code >= 500:
                        error_msg = "Server error. Please try again later."
                    elif r.status_code == 404:
                        error_msg = "Registration endpoint not found. Check API URL."
                signup_output.value = error_msg
                signup_output.color = ft.colors.RED
                page.update()
        except requests.exceptions.RequestException as ex:
            signup_output.value = f"Network error: {str(ex)}"
            signup_output.color = ft.colors.RED
            page.update()
        except Exception as ex:
            signup_output.value = f"Error: {str(ex)}"
            signup_output.color = ft.colors.RED
            page.update()

    def show_login_view():
        page.clean()

        # Modern gradient background
        gradient_bg = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.BLUE_400, ft.colors.INDIGO_600, ft.colors.PURPLE_600],
            ),
            expand=True,
        )

        # Modern login card
        login_card = ft.Container(
            content=ft.Column([
                # Header with icon
                ft.Row([
                    ft.Icon(ft.icons.HEALTH_AND_SAFETY, size=48, color=ft.colors.WHITE),
                    ft.Column([
                        ft.Text("Patient Portal", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                        ft.Text("Your Health, Our Priority", size=14, color=ft.colors.WHITE70),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),

                ft.Container(height=30),  # Spacer

                # Login/Signup tabs with modern styling
                ft.Container(
                    content=ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        indicator_color=ft.colors.WHITE,
                        label_color=ft.colors.WHITE70,
                        unselected_label_color=ft.colors.WHITE54,
                        tabs=[
                             ft.Tab(
                                 text="Login",
                                 content=ft.Container(
                                     content=ft.Column([
                                         ft.Container(height=20),
                                         ft.Text("Welcome Back", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
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
                                                 bgcolor=ft.colors.WHITE,
                                                 color=ft.colors.BLUE_600,
                                                 elevation=8,
                                                 shadow_color=ft.colors.BLACK38,
                                             ),
                                             icon=ft.icons.LOGIN,
                                         ),
                                         ft.Container(height=10),
                                         output,
                                     ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                     padding=ft.padding.all(20),
                                     bgcolor=ft.colors.WHITE,
                                     border_radius=12,
                                 )
                             ),
                             ft.Tab(
                                 text="Sign Up",
                                 content=ft.Container(
                                     content=ft.Column([
                                         ft.Container(height=20),
                                         ft.Text("Create Your Account", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
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
                                                 bgcolor=ft.colors.WHITE,
                                                 color=ft.colors.BLUE_600,
                                                 elevation=8,
                                                 shadow_color=ft.colors.BLACK38,
                                             ),
                                             icon=ft.icons.PERSON_ADD,
                                         ),
                                         ft.Container(height=10),
                                         signup_output,
                                     ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                     padding=ft.padding.all(20),
                                     bgcolor=ft.colors.WHITE,
                                     border_radius=12,
                                 )
                             ),
                        ],
                    ),
                    bgcolor=ft.colors.WHITE10,
                    border_radius=16,
                    shadow=ft.BoxShadow(
                        spread_radius=2,
                        blur_radius=16,
                        color=ft.colors.BLACK38,
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