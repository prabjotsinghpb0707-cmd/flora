from nicegui import ui
import database
from auth import change_user_password


def render_settings(user_id):
    user = database.get_user(user_id)

    ui.label("Settings").classes("page-title")
    ui.label("Manage your profile and account security.").classes("page-subtitle")

    if not user:
        ui.label("Account not found.").classes("empty-state")
        return

    with ui.card().classes("content-card w-full"):
        ui.label("Profile information").classes("card-heading")

        name = ui.input(
            "Full name", value=user["name"]
        ).props("outlined").classes("full-input")

        ui.input(
            "Email address", value=user["email"]
        ).props("outlined readonly").classes("full-input")

        ui.label(f"Member since: {user['created_at']}").classes("muted-text")

        def save_profile():
            if not (name.value or "").strip():
                ui.notify("Name cannot be empty.", type="warning")
                return

            database.update_profile(user_id, name.value)
            ui.notify("Profile updated.", type="positive")

        ui.button("Save profile", on_click=save_profile).classes("primary-button")

    with ui.card().classes("content-card w-full"):
        ui.label("Change password").classes("card-heading")

        old_password = ui.input(
            "Current password", password=True
        ).props("outlined").classes("full-input")

        new_password = ui.input(
            "New password", password=True
        ).props("outlined").classes("full-input")

        confirm = ui.input(
            "Confirm new password", password=True
        ).props("outlined").classes("full-input")

        def update():
            if new_password.value != confirm.value:
                ui.notify("New passwords do not match.", type="negative")
                return

            success = change_user_password(
                user_id,
                old_password.value or "",
                new_password.value or ""
            )

            if success:
                ui.notify("Password changed successfully.", type="positive")
                old_password.value = ""
                new_password.value = ""
                confirm.value = ""
            else:
                ui.notify(
                    "Current password is incorrect or the new password is too short.",
                    type="negative"
                )

        ui.button("Update password", on_click=update).classes("primary-button")