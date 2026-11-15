import hashlib
import hmac
import os
import re

from nicegui import ui, app
import database


def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 260000
    )
    return salt.hex() + ":" + hashed.hex()


def check_password(password, stored):
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 260000
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def valid_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def render_login():
    with ui.column().classes("auth-page"):
        with ui.card().classes("auth-card"):
            ui.label("FLOARA").classes("auth-logo")
            ui.label("Welcome back").classes("auth-title")
            ui.label("Sign in to manage your money.").classes("auth-subtitle")

            email = ui.input("Email address").props(
                "outlined type=email autocomplete=email"
            ).classes("auth-input")

            password = ui.input("Password", password=True).props(
                "outlined autocomplete=current-password"
            ).classes("auth-input")

            def login():
                user = database.get_user_by_email(email.value or "")

                if not user or not check_password(
                    password.value or "", user["password_hash"]
                ):
                    ui.notify(
                        "Email or password is incorrect.",
                        type="negative"
                    )
                    return

                app.storage.user["user_id"] = user["id"]
                ui.navigate.to("/dashboard")

            ui.button("Sign in", on_click=login).classes(
                "primary-button auth-submit"
            )

            with ui.row().classes("auth-switch"):
                ui.label("New to FLOARA?").classes("muted-text")
                ui.link("Create an account", "/signup").classes("auth-link")


def render_signup():
    with ui.column().classes("auth-page"):
        with ui.card().classes("auth-card signup-card"):
            ui.label("FLOARA").classes("auth-logo")
            ui.label("Create your account").classes("auth-title")
            ui.label("A clearer way to manage your finances.").classes("auth-subtitle")

            name = ui.input("Full name").props(
                "outlined autocomplete=name"
            ).classes("auth-input")

            email = ui.input("Email address").props(
                "outlined type=email autocomplete=email"
            ).classes("auth-input")

            password = ui.input("Create password", password=True).props(
                "outlined autocomplete=new-password"
            ).classes("auth-input")

            confirm = ui.input("Confirm password", password=True).props(
                "outlined autocomplete=new-password"
            ).classes("auth-input")

            def register():
                clean_name = (name.value or "").strip()
                clean_email = (email.value or "").strip().lower()
                new_password = password.value or ""

                if not clean_name or not clean_email or not new_password:
                    ui.notify("Please complete all fields.", type="warning")
                    return

                if not valid_email(clean_email):
                    ui.notify("Enter a valid email address.", type="warning")
                    return

                if len(new_password) < 8:
                    ui.notify(
                        "Password must contain at least 8 characters.",
                        type="warning"
                    )
                    return

                if new_password != (confirm.value or ""):
                    ui.notify("Passwords do not match.", type="negative")
                    return

                user_id = database.create_user(
                    clean_name,
                    clean_email,
                    hash_password(new_password)
                )

                if not user_id:
                    ui.notify(
                        "An account with this email already exists.",
                        type="negative"
                    )
                    return

                app.storage.user["user_id"] = user_id
                ui.notify("Your account has been created.", type="positive")
                ui.navigate.to("/dashboard")

            ui.button("Create account", on_click=register).classes(
                "primary-button auth-submit"
            )

            with ui.row().classes("auth-switch"):
                ui.label("Already have an account?").classes("muted-text")
                ui.link("Sign in", "/").classes("auth-link")


def change_user_password(user_id, old_password, new_password):
    user = database.get_user(user_id)
    if not user or len(new_password) < 8:
        return False

    full_user = database.get_user_by_email(user["email"])
    if not full_user or not check_password(
        old_password, full_user["password_hash"]
    ):
        return False

    database.update_password(user_id, hash_password(new_password))
    return True