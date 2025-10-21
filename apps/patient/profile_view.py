import flet as ft
import requests

def create_profile_view(page, token, user_id, API_BASE, logout_callback, theme_mode):
    """Create and return the profile view components"""

    content_area = ft.Container(animate_opacity=300)

    def show_profile_view():
        content_area.content = ft.Column([
            ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Loading profile information...", color=ft.Colors.BLUE),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
        page.update()
        load_profile_data()

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
                    ft.Text("Patient Information:", size=16, weight=ft.FontWeight.BOLD),
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
                                         ft.Text(f"📅 Member Since: {profile.get('created_at', 'Unknown')}", size=14),
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
                            on_click=logout_callback,
                            style=ft.ButtonStyle(color=ft.Colors.RED)
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ], expand=True, scroll=ft.ScrollMode.AUTO)

                content_area.content = profile_content
                content_area.opacity = 1

            else:
                content_area.content = ft.Column([
                    ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("❌ Failed to load profile", color=ft.Colors.RED, size=16),
                    ft.Text(f"Error: {r.status_code}", color=ft.Colors.RED),
                    ft.ElevatedButton("🔄 Retry", on_click=lambda e: load_profile_data()),
                    ft.ElevatedButton("🚪 Logout", on_click=logout_callback),
                ], expand=True, scroll=ft.ScrollMode.AUTO)

        except Exception as ex:
            content_area.content = ft.Column([
                ft.Text("Profile", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("❌ Error loading profile", color=ft.Colors.RED, size=16),
                ft.Text(f"Error: {str(ex)}", color=ft.Colors.RED),
                ft.ElevatedButton("🔄 Retry", on_click=lambda e: load_profile_data()),
                ft.ElevatedButton("🚪 Logout", on_click=logout_callback),
            ], expand=True, scroll=ft.ScrollMode.AUTO)

        page.update()

    def toggle_theme(e):
        theme_mode["value"] = ft.ThemeMode.DARK if theme_mode["value"] == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.theme_mode = theme_mode["value"]
        page.update()

    return content_area, show_profile_view