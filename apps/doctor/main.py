import flet as ft
import requests
from datetime import date

API_BASE = "http://127.0.0.1:2000/api"

def main(page: ft.Page):
    page.title = "Hospital App"
    token = {"value": None}
    user_id = {"value": None}
    current_view = {"value": "home"}
    theme_mode = {"value": ft.ThemeMode.LIGHT}
    user_type = {"value": None}
    hospital_info = {"value": None}

    # Login components
    email = ft.TextField(label="Email")
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    output = ft.Text()

    # Sign-up components
    signup_email = ft.TextField(label="Email")
    signup_password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    signup_confirm_password = ft.TextField(label="Confirm Password", password=True, can_reveal_password=True)
    signup_full_name = ft.TextField(label="Full Name")
    signup_user_type = ft.Dropdown(
        label="User Type",
        options=[
            ft.dropdown.Option("Hospital Admin"),
            ft.dropdown.Option("Doctor"),
            ft.dropdown.Option("Patient")
        ],
        value="Hospital Admin"
    )
    signup_hospital_dropdown = ft.Dropdown(
        label="Select Hospital",
        options=[],
        disabled=True
    )
    signup_hospital_location = ft.TextField(label="Hospital Location", read_only=True)
    signup_output = ft.Text()
    
    # Event handlers for signup form
    def handle_user_type_change(e):
        if signup_user_type.value == "Hospital Admin":
            signup_hospital_dropdown.disabled = False
        else:
            signup_hospital_dropdown.disabled = True
            signup_hospital_dropdown.value = None
            signup_hospital_location.value = ""
        page.update()

    def handle_hospital_change(e):
        if signup_hospital_dropdown.value:
            try:
                r = requests.get(f"{API_BASE}/hospitals")
                if r.status_code == 200:
                    hospitals = r.json().get("hospitals", [])
                    selected_hospital = next((h for h in hospitals if str(h["hospital_id"]) == signup_hospital_dropdown.value), None)
                    if selected_hospital:
                        signup_hospital_location.value = selected_hospital["address"]
            except Exception as ex:
                print(f"Error loading hospital details: {ex}")
        else:
            signup_hospital_location.value = ""
        page.update()
    
    # Assign event handlers
    signup_user_type.on_change = handle_user_type_change
    signup_hospital_dropdown.on_change = handle_hospital_change
    
    # Navigation components with modern styling
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_ROUNDED,
                label="Home",
                selected_icon=ft.Icons.HOME_ROUNDED
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PEOPLE_ROUNDED,
                label="Doctors",
                selected_icon=ft.Icons.PEOPLE_ROUNDED
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_ROUNDED,
                label="Add Doctor",
                selected_icon=ft.Icons.ADD_CIRCLE_ROUNDED
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
        indicator_color=ft.Colors.INDIGO_600,
        indicator_shape=ft.RoundedRectangleBorder(radius=20),
    )
    
    # Content areas
    content_area = ft.Container(animate_opacity=300)
    appt_list = ft.ListView(expand=1, spacing=10, padding=10)
    completed_appt_list = ft.ListView(expand=1, spacing=10, padding=10)
    hospitals_list = ft.ListView(expand=1, spacing=10, padding=10)

    # Stats texts
    stats_texts = {
        "appointments": ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
        "completed": ft.Text("Loading...", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
        "reviews": ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
    }

    def do_login(e):
        try:
            r = requests.post(f"{API_BASE}/login", json={"email": email.value, "password": password.value})
            if r.status_code == 200:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                user_type["value"] = data["user"]["user_type"]
                output.value = "Logged in"
                page.update()
                
                # Load profile to get hospital info
                load_user_profile()
                
                # Check if first-time login for hospital admin
                if user_type["value"] == "Hospital Admin" and hospital_info["value"] and hospital_info["value"].get("is_first_login"):
                    show_hospital_setup_wizard()
                else:
                    show_main_app()
            else:
                output.value = r.json().get("message", "Login failed")
                page.update()
        except Exception as ex:
            output.value = str(ex)
            page.update()

    def load_user_profile():
        try:
            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/profile", headers=headers)
            if r.status_code == 200:
                profile = r.json()
                hospital_info["value"] = profile
        except Exception as ex:
            print(f"Error loading profile: {ex}")

    def show_hospital_setup_wizard():
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=40, color=ft.Colors.BLUE),
                    ft.Text("Hospital Setup", size=24, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Welcome to your Hospital Dashboard!", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Let's set up your hospital by adding doctors.", size=14),
                        ft.Divider(),
                        ft.Text("Add Your First Doctor", size=16, weight=ft.FontWeight.BOLD),
                        ft.TextField(label="Doctor Email"),
                        ft.TextField(label="Doctor Password", password=True, can_reveal_password=True),
                        ft.TextField(label="Doctor Full Name"),
                        ft.TextField(label="Specialization"),
                        ft.TextField(label="Qualifications"),
                        ft.TextField(label="Experience (years)"),
                        ft.ElevatedButton("Add Doctor", on_click=add_first_doctor, width=200),
                        ft.ElevatedButton("Skip for Now", on_click=lambda e: show_main_app(), width=200),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def add_first_doctor(e):
        # This will be implemented later
        show_main_app()

    def show_main_app():
        page.theme_mode = theme_mode["value"]
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column([
                    # App header with gradient
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=32, color=ft.Colors.WHITE),
                            ft.Text("Hospital Portal", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.START),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.INDIGO_600, ft.Colors.BLUE_700],
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

    def change_view(index):
        content_area.opacity = 0
        page.update()
        if index == 0:
            show_home_view()
        elif index == 1:
            show_doctors_view()
        elif index == 2:
            show_add_doctor_view()
        elif index == 3:
            show_profile_view()

    def show_home_view():
        current_view["value"] = "home"
        welcome_text = "Welcome, Hospital Admin!" if user_type["value"] == "Hospital Admin" else "Welcome!"

        # Modern welcome card
        welcome_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WAVING_HAND, size=32, color=ft.Colors.AMBER_600),
                    ft.Text(welcome_text, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Text("Here's your hospital overview", size=16, color=ft.Colors.GREY_700),
            ], spacing=8),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4),
            ),
            margin=ft.margin.only(bottom=20),
        )

        # Hospital info card
        hospital_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=24, color=ft.Colors.INDIGO_600),
                    ft.Text("Hospital Details", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BUSINESS, size=20, color=ft.Colors.GREY_600),
                            ft.Text(f"{hospital_info['value'].get('hospital_name', 'Not assigned') if hospital_info['value'] else 'Not assigned'}",
                                   size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800, expand=True),
                        ], spacing=8),
                        ft.Container(height=8),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON, size=20, color=ft.Colors.GREY_600),
                            ft.Text(f"{hospital_info['value'].get('hospital_address', 'Not available') if hospital_info['value'] else 'Not available'}",
                                   size=14, color=ft.Colors.GREY_700, expand=True),
                        ], spacing=8),
                    ], spacing=0),
                ),
            ], spacing=0),
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

        # Stats cards with modern styling
        stats_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PEOPLE, size=32, color=ft.Colors.BLUE_600),
                    ft.Text("Total Doctors", size=14, color=ft.Colors.GREY_600),
                    stats_texts["appointments"],
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=110,
                height=100,
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=32, color=ft.Colors.GREEN_600),
                    ft.Text("Available Today", size=14, color=ft.Colors.GREY_600),
                    stats_texts["completed"],
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=110,
                height=100,
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.MEDICAL_SERVICES, size=32, color=ft.Colors.PURPLE_600),
                    ft.Text("Departments", size=14, color=ft.Colors.GREY_600),
                    stats_texts["reviews"],
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                width=110,
                height=100,
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=8,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

        content_area.content = ft.Column([
            welcome_card,
            hospital_card,
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ANALYTICS, size=24, color=ft.Colors.INDIGO_600),
                        ft.Text("Quick Stats", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                    ], alignment=ft.MainAxisAlignment.START, spacing=10),
                    ft.Container(height=16),
                    stats_row,
                ], spacing=0),
                padding=ft.padding.all(20),
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.border_radius.all(12),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=12,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 4),
                ),
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        load_hospital_stats()
        content_area.opacity = 1
        page.update()

    def load_hospital_stats():
        # Placeholder for hospital stats
        stats_texts["appointments"].value = "0"
        stats_texts["completed"].value = "0"
        stats_texts["reviews"].value = "0"
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

    def show_doctors_view():
        current_view["value"] = "doctors"
        load_doctors()

        # Modern header
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PEOPLE, size=28, color=ft.Colors.INDIGO_600),
                ft.Text("Hospital Doctors", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
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
            appt_list,  # Reusing this list for doctors
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)
        content_area.opacity = 1
        page.update()

    def show_add_doctor_view():
        current_view["value"] = "add_doctor"
        content_area.content = ft.Column([
            ft.Text("Add New Doctor", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.TextField(label="Doctor Email"),
            ft.TextField(label="Doctor Password", password=True, can_reveal_password=True),
            ft.TextField(label="Doctor Full Name"),
            ft.TextField(label="Specialization"),
            ft.TextField(label="Qualifications"),
            ft.TextField(label="Experience (years)"),
            ft.ElevatedButton("Add Doctor", on_click=add_doctor),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        content_area.opacity = 1
        page.update()

    def show_profile_view():
        current_view["value"] = "profile"
        content_area.content = ft.Column([
            ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Loading profile information...", color=ft.Colors.BLUE),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        page.update()
        load_profile_data()

    def load_doctors():
        appt_list.controls.clear()
        try:
            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/doctors", headers=headers)
            if r.status_code == 200:
                doctors = r.json().get("doctors", [])
                if doctors:
                    for doctor in doctors:
                        # Status styling
                        status_color = ft.Colors.GREEN_600 if doctor['is_available'] else ft.Colors.RED_600
                        status_bg = ft.Colors.GREEN_50 if doctor['is_available'] else ft.Colors.RED_50
                        status_text = "Available" if doctor['is_available'] else "Not Available"

                        appt_list.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.CircleAvatar(
                                            content=ft.Icon(ft.Icons.PERSON, size=24, color=ft.Colors.WHITE),
                                            radius=24,
                                            bgcolor=ft.Colors.INDIGO_600,
                                        ),
                                        ft.Container(width=12),
                                        ft.Column([
                                            ft.Text(doctor['full_name'], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                                            ft.Text(doctor['specialization'], size=14, color=ft.Colors.GREY_600),
                                        ], spacing=2, expand=True),
                                        ft.Container(
                                            content=ft.Text(status_text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                            bgcolor=status_color,
                                            border_radius=ft.border_radius.all(12),
                                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.START, spacing=0),
                                    ft.Container(height=12),
                                    ft.Row([
                                        ft.Icon(ft.Icons.SCHOOL, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(f"Qualifications: {doctor.get('qualifications', 'Not specified')}", size=14, color=ft.Colors.GREY_700, expand=True),
                                    ], spacing=5),
                                    ft.Container(height=6),
                                    ft.Row([
                                        ft.Icon(ft.Icons.WORK, size=16, color=ft.Colors.GREY_600),
                                        ft.Text(f"Experience: {doctor.get('experience_years', 'N/A')} years", size=14, color=ft.Colors.GREY_700),
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
                                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.GREY_400),
                                ft.Container(height=16),
                                ft.Text("No doctors found", size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=8),
                                ft.Text("Doctors will appear here once added to the system", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
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
                            ft.Text("Failed to load doctors", size=16, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            ft.ElevatedButton(
                                "Retry",
                                on_click=lambda e: load_doctors(),
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
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
                        ft.Icon(ft.Icons.ERROR, size=48, color=ft.Colors.RED_400),
                        ft.Container(height=16),
                        ft.Text("Error loading doctors", size=16, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.Text(f"{str(ex)}", size=12, color=ft.Colors.RED_500, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=12),
                        ft.ElevatedButton(
                            "Retry",
                            on_click=lambda e: load_doctors(),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
        page.update()

    def add_doctor(e):
        # Placeholder for add doctor functionality
        print("Add doctor functionality to be implemented")

    def load_profile_data():
        try:
            headers = {"Authorization": f"Bearer {token['value']}"}
            r = requests.get(f"{API_BASE}/profile", headers=headers)
            
            if r.status_code == 200:
                profile = r.json()
                
                # Create profile content
                profile_content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Doctor Information:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE),
                                    ft.Text("Personal Details", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Row([
                                    ft.CircleAvatar(
                                        content=ft.Icon(ft.Icons.PERSON, size=30),
                                        radius=30,
                                        bgcolor=ft.Colors.BLUE_100
                                    ),
                                    ft.Column([
                                        ft.Text(f"👤 Name: {profile.get('full_name', 'Not provided')}", size=14),
                                        ft.Text(f"📧 Email: {profile.get('email', 'Not provided')}", size=14),
                                        ft.Text(f"🆔 User ID: {profile.get('user_id', 'Not provided')}", size=14),
                                        ft.Text(f"👥 Type: {profile.get('user_type', 'Not provided')}", size=14),
                                        ft.Text(f"📅 Member Since: User #{profile.get('created_at', 'Unknown')}", size=14),
                                    ], spacing=2),
                                ], spacing=10),
                            ], spacing=5),
                            padding=15
                        ),
                        margin=ft.margin.symmetric(vertical=5)
                    ),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.MEDICAL_SERVICES, color=ft.Colors.GREEN),
                                    ft.Text("Medical Information", size=16, weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Divider(),
                                ft.Text(f"🩺 Specialization: {profile.get('specialization', 'Not specified')}", size=14),
                                ft.Text(f"🎓 Qualifications: {profile.get('qualifications', 'Not provided')}", size=14),
                                ft.Text(f"🏥 Hospital: {profile.get('hospital_name', 'Not assigned')}", size=14),
                                ft.Text(f"📍 Hospital Address: {profile.get('hospital_address', 'Not available')}", size=14),
                                ft.Text(f"✅ Availability: {'Available' if profile.get('is_available') else 'Not Available'}", 
                                       size=14, color=ft.Colors.GREEN if profile.get('is_available') else ft.Colors.RED),
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
                                ft.Text("🌐 Service: Doctor Portal", size=14),
                                ft.Switch(
                                    label="Dark Mode",
                                    value=theme_mode["value"] == ft.ThemeMode.DARK,
                                    on_change=toggle_theme
                                ),
                            ], spacing=5),
                            padding=15
                        ),
                        margin=ft.margin.symmetric(vertical=5)
                    ),
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            "🔄 Refresh Profile", 
                            on_click=lambda e: load_profile_data(),
                            style=ft.ButtonStyle(color=ft.Colors.BLUE)
                        ),
                        ft.ElevatedButton(
                            "🚪 Logout", 
                            on_click=logout,
                            style=ft.ButtonStyle(color=ft.Colors.RED)
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                
                content_area.content = profile_content
                
            else:
                content_area.content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("❌ Failed to load profile", color=ft.Colors.RED, size=16),
                    ft.Text(f"Error: {r.status_code}", color=ft.Colors.RED),
                    ft.ElevatedButton("🔄 Retry", on_click=lambda e: load_profile_data()),
                    ft.ElevatedButton("🚪 Logout", on_click=logout),
                ], expand=True, scroll=ft.ScrollMode.AUTO)
                
        except Exception as ex:
            content_area.content = ft.Column([
                ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("❌ Error loading profile", color=ft.Colors.RED, size=16),
                ft.Text(f"Error: {str(ex)}", color=ft.Colors.RED),
                ft.ElevatedButton("🔄 Retry", on_click=lambda e: load_profile_data()),
                ft.ElevatedButton("🚪 Logout", on_click=logout),
            ], expand=True, scroll=ft.ScrollMode.AUTO)

        content_area.opacity = 1
        page.update()

    def logout(e):
        token["value"] = None
        user_id["value"] = None
        page.clean()
        show_login_view()

    def toggle_theme(e):
        theme_mode["value"] = ft.ThemeMode.DARK if theme_mode["value"] == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.theme_mode = theme_mode["value"]
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
                                        ft.Text(f"Patient: {a.get('patient_name', 'Unknown')}", size=14),
                                        ft.ElevatedButton("Mark Completed", on_click=lambda e, aid=a['id']: mark_completed(aid)),
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
                                    ft.Text(f"Patient: {a.get('patient_name', 'Unknown')}", size=14),
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

    def mark_completed(aid):
        # Placeholder: reload appointments (assuming API updates status)
        load_appointments()

    def do_signup(e):
        try:
            # Validate passwords match
            if signup_password.value != signup_confirm_password.value:
                signup_output.value = "Passwords do not match"
                signup_output.color = ft.Colors.RED
                page.update()
                return
            
            # Validate required fields
            if not all([signup_email.value, signup_password.value, signup_full_name.value, signup_user_type.value]):
                signup_output.value = "Please fill in all fields"
                signup_output.color = ft.Colors.RED
                page.update()
                return
            
            # For hospital admin, validate hospital selection
            if signup_user_type.value == "Hospital Admin" and not signup_hospital_dropdown.value:
                signup_output.value = "Please select a hospital"
                signup_output.color = ft.Colors.RED
                page.update()
                return
            
            # Prepare registration data
            reg_data = {
                "email": signup_email.value,
                "password": signup_password.value,
                "user_type": signup_user_type.value,
                "full_name": signup_full_name.value
            }
            
            # Add hospital_id for hospital admin
            if signup_user_type.value == "Hospital Admin":
                reg_data["hospital_id"] = signup_hospital_dropdown.value
            
            r = requests.post(f"{API_BASE}/register", json=reg_data)
            
            if r.status_code == 201:
                data = r.json()
                token["value"] = data["access_token"]
                user_id["value"] = data["user"]["user_id"]
                user_type["value"] = data["user"]["user_type"]
                signup_output.value = "Account created successfully!"
                signup_output.color = ft.Colors.GREEN
                page.update()
                
                # Load profile and check if first-time login for hospital admin
                load_user_profile()
                if user_type["value"] == "Hospital Admin" and hospital_info["value"] and hospital_info["value"].get("is_first_login"):
                    show_hospital_setup_wizard()
                else:
                    show_main_app()
            else:
                signup_output.value = r.json().get("message", "Registration failed")
                signup_output.color = ft.Colors.RED
                page.update()
        except Exception as ex:
            signup_output.value = str(ex)
            signup_output.color = ft.Colors.RED
            page.update()

    def load_nearby():
        hospitals_list.controls.clear()
        hospitals_list.controls.append(ft.Text("Loading nearby hospitals...", color=ft.Colors.BLUE))
        page.update()
        
        try:
            # demo coordinates; replace with device location
            lat, lon = 18.5204, 73.8567
            r = requests.get(f"{API_BASE}/hospitals/nearby", params={"lat": lat, "lon": lon})
            
            if r.status_code == 200:
                hospitals = r.json().get("hospitals", [])
                hospitals_list.controls.clear()
                
                if hospitals:
                    for h in hospitals:
                        distance = h.get('distance_km', '?')
                        phone = h.get('phone', 'N/A')
                        hospitals_list.controls.append(
                            ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text(h['name'], size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"📍 {h['address']}", size=12),
                                        ft.Text(f"📞 {phone}", size=12),
                                        ft.Text(f"💰 {h.get('fee_details', 'Contact for pricing')}", size=12),
                                        ft.Text(f"📏 {distance} km away", size=12, color=ft.Colors.BLUE),
                                    ], spacing=2),
                                    padding=10
                                ),
                                margin=ft.margin.symmetric(vertical=2)
                            )
                        )
                else:
                    hospitals_list.controls.append(ft.Text("No hospitals found nearby", color=ft.Colors.ORANGE))
            else:
                hospitals_list.controls.clear()
                hospitals_list.controls.append(ft.Text(f"Error loading hospitals: {r.status_code}", color=ft.Colors.RED))
        except Exception as ex:
            hospitals_list.controls.clear()
            hospitals_list.controls.append(ft.Text(f"Failed to load hospitals: {str(ex)}", color=ft.Colors.RED))
        
        page.update()

    def show_login_view():
        page.clean()

        # Modern gradient background
        gradient_bg = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.INDIGO_600, ft.Colors.BLUE_700, ft.Colors.CYAN_600],
            ),
            expand=True,
        )

        # Modern login card
        login_card = ft.Container(
            content=ft.Column([
                # Header with icon
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=48, color=ft.Colors.WHITE),
                    ft.Column([
                        ft.Text("Hospital Portal", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Manage your healthcare facility", size=14, color=ft.Colors.WHITE70),
                    ], spacing=0),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),

                ft.Container(height=30),  # Spacer

                # Login form with modern styling
                ft.Container(
                    content=ft.Column([
                        ft.Container(height=20),
                        ft.Text("Welcome Back", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Container(height=10),
                        ft.Container(
                            content=email,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(4),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=8,
                                color=ft.Colors.BLACK26,
                                offset=ft.Offset(0, 2),
                            ),
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=password,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=ft.border_radius.all(12),
                            padding=ft.padding.all(4),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=8,
                                color=ft.Colors.BLACK26,
                                offset=ft.Offset(0, 2),
                            ),
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Login",
                            on_click=do_login,
                            width=250,
                            height=50,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.WHITE,
                                color=ft.Colors.INDIGO_600,
                                elevation=8,
                                shadow_color=ft.Colors.BLACK38,
                            ),
                            icon=ft.Icons.LOGIN,
                        ),
                        ft.Container(height=10),
                        output,
                        ft.Container(height=10),
                        ft.TextButton(
                            "Don't have an account? Sign Up",
                            on_click=lambda e: show_signup_view(),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE),
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    padding=ft.padding.all(20),
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=ft.border_radius.all(16),
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

    def show_signup_view():
        load_hospitals_for_signup()
        page.clean()
        page.add(
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCAL_HOSPITAL, size=40, color=ft.Colors.BLUE),
                    ft.Text("Hospital App", size=24, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Create Account", size=18, weight=ft.FontWeight.BOLD),
                        signup_full_name,
                        signup_email,
                        signup_password,
                        signup_confirm_password,
                        signup_user_type,
                        signup_hospital_dropdown,
                        signup_hospital_location,
                        ft.ElevatedButton("Sign Up", on_click=do_signup, width=200),
                        signup_output,
                        ft.TextButton("Already have an account? Login", on_click=lambda e: show_login_view()),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
            ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        page.update()

    def load_hospitals_for_signup():
        try:
            r = requests.get(f"{API_BASE}/hospitals")
            if r.status_code == 200:
                hospitals = r.json().get("hospitals", [])
                signup_hospital_dropdown.options = [
                    ft.dropdown.Option(key=str(h["hospital_id"]), text=h["name"])
                    for h in hospitals
                ]
                page.update()
        except Exception as ex:
            print(f"Error loading hospitals: {ex}")

    # Initialize with login view
    show_login_view()

ft.app(target=main)
