import os

from nicegui import ui, app

import database
import auth
import dashboard
import expenses
import transactions
import budgets
import reports
import settings


CUSTOM_CSS = """
<style>
:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --background: #f5f8ff;
    --surface: #ffffff;
    --text: #172554;
    --muted: #64748b;
    --border: #e2e8f0;
}

body {
    background: var(--background) !important;
    color: var(--text) !important;
    font-family: Inter, Arial, sans-serif;
}

* {
    box-sizing: border-box;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Authentication pages */
.auth-page {
    min-height: 100vh;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 25px;
    background:
        radial-gradient(circle at 10% 10%, #dbeafe 0, transparent 32%),
        radial-gradient(circle at 90% 90%, #e0e7ff 0, transparent 30%),
        #f5f8ff;
}

.auth-card {
    width: 100%;
    max-width: 440px;
    padding: 34px !important;
    background: #ffffff !important;
    border: 1px solid #e5eaf3 !important;
    border-radius: 20px !important;
    box-shadow: 0 15px 50px rgba(30, 64, 175, .09) !important;
    animation: fadeUp .45s ease both;
}

.signup-card {
    max-width: 470px;
}

.auth-logo {
    color: #2563eb !important;
    font-size: 27px !important;
    font-weight: 900 !important;
    letter-spacing: 4px;
    text-align: center;
    width: 100%;
}

.auth-title {
    color: #172554 !important;
    font-size: 27px !important;
    font-weight: 800 !important;
    text-align: center;
    width: 100%;
    margin-top: 17px;
}

.auth-subtitle {
    color: #64748b !important;
    text-align: center;
    width: 100%;
    margin-bottom: 18px;
}

.auth-input,
.full-input {
    width: 100%;
}

.auth-switch {
    width: 100%;
    justify-content: center;
    align-items: center;
    margin-top: 16px;
    gap: 5px;
}

.auth-link {
    color: #2563eb !important;
    font-weight: 700;
    text-decoration: none;
}

.auth-link:hover {
    color: #1d4ed8 !important;
    text-decoration: underline;
}

.muted-text {
    color: #64748b !important;
    font-size: 13px;
}

.auth-submit {
    width: 100%;
    margin-top: 12px;
}

/* Main app layout */
.app-layout {
    min-height: 100vh;
    width: 100%;
    align-items: stretch;
    gap: 0 !important;
}

.sidebar {
    width: 245px;
    min-width: 245px;
    min-height: 100vh;
    padding: 23px 15px;
    background: #ffffff !important;
    border-right: 1px solid #e5eaf3;
}

.brand {
    color: #2563eb !important;
    font-size: 27px !important;
    font-weight: 900 !important;
    letter-spacing: 3px;
}

.brand-caption {
    color: #94a3b8 !important;
    font-size: 10px !important;
    font-weight: 700;
    letter-spacing: 1.7px;
}

.nav-button {
    width: 100%;
    min-height: 45px;
    justify-content: flex-start;
    text-align: left;
    color: #475569 !important;
    border-radius: 10px !important;
    padding-left: 12px;
    transition: background .2s ease, color .2s ease;
}

.nav-button:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}

.nav-button .q-icon {
    color: #64748b;
}

.nav-section {
    color: #94a3b8 !important;
    font-size: 10px !important;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-top: 20px;
}

.sidebar-profile {
    padding: 12px;
    border-radius: 12px;
    background: #f5f8ff;
    border: 1px solid #e5eaf3;
}

.main-panel {
    min-width: 0;
    flex: 1;
    padding: 28px;
    gap: 17px;
}

.topbar {
    width: 100%;
    padding-bottom: 15px;
    border-bottom: 1px solid #e5eaf3;
}

.topbar-title {
    color: #172554 !important;
    font-size: 14px !important;
    font-weight: 700;
}

.topbar-caption {
    color: #94a3b8 !important;
    font-size: 11px !important;
}

/* Headings */
.page-title {
    color: #172554 !important;
    font-size: 29px !important;
    font-weight: 800 !important;
    animation: fadeUp .35s ease both;
}

.page-subtitle {
    color: #64748b !important;
    font-size: 14px !important;
    line-height: 1.6;
}

.section-title {
    color: #1e3a8a !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    margin-top: 8px;
}

.card-heading {
    color: #172554 !important;
    font-size: 16px !important;
    font-weight: 800 !important;
}

/* Dashboard cards */
.dashboard-cards {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    width: 100%;
    gap: 15px;
}

.stat-card,
.content-card {
    background: #ffffff !important;
    border: 1px solid #e5eaf3 !important;
    border-radius: 15px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, .035) !important;
    animation: fadeUp .4s ease both;
}

.stat-card {
    width: 100%;
    padding: 19px !important;
    min-width: 0;
    transition: transform .2s ease, box-shadow .2s ease;
}

.stat-card:hover,
.content-card:hover {
    box-shadow: 0 8px 23px rgba(37, 99, 235, .08) !important;
}

.stat-title {
    color: #64748b !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}

.stat-number {
    color: #172554 !important;
    font-size: clamp(21px, 2vw, 28px) !important;
    font-weight: 850 !important;
    overflow-wrap: anywhere;
    margin-top: 7px;
}

.stat-hint {
    color: #94a3b8 !important;
    font-size: 11px !important;
    margin-top: 5px;
}

.stat-blue { border-left: 4px solid #3b82f6 !important; }
.stat-green { border-left: 4px solid #16a34a !important; }
.stat-red { border-left: 4px solid #ef4444 !important; }
.stat-purple { border-left: 4px solid #8b5cf6 !important; }

.content-card {
    padding: 20px !important;
    min-width: 0;
}

.form-card {
    max-width: 760px;
}

.transaction-item {
    padding: 13px 15px;
    border: 1px solid #e8edf5;
    background: #ffffff;
    border-radius: 11px;
    margin-bottom: 6px;
}

.strong-text {
    color: #172554 !important;
    font-weight: 750 !important;
    font-size: 14px;
}

.small-text {
    color: #64748b !important;
    font-size: 12px !important;
}

.amount-text {
    font-size: 14px !important;
    font-weight: 800 !important;
}

.green-text {
    color: #15803d !important;
    font-weight: 650;
}

.red-text {
    color: #dc2626 !important;
    font-weight: 650;
}

.empty-state {
    color: #64748b !important;
    padding: 22px 10px;
    line-height: 1.6;
}

/* Forms */
.q-field__label {
    color: #475569 !important;
    font-weight: 600 !important;
}

.q-field__native,
.q-field__input,
.q-field input,
.q-field textarea {
    color: #172554 !important;
}

.q-field__marginal,
.q-field__append,
.q-field__prepend {
    color: #64748b !important;
}

.q-field--outlined .q-field__control {
    background: #ffffff !important;
    border-radius: 9px !important;
}

.q-field--outlined .q-field__control:before {
    border-color: #cbd5e1 !important;
}

.q-field--outlined .q-field__control:hover:before {
    border-color: #60a5fa !important;
}

.q-field--focused .q-field__control:after {
    border-color: #2563eb !important;
}

.q-placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

.kind-selector {
    color: #172554 !important;
    margin-bottom: 15px;
}

.filter-row {
    gap: 12px;
    flex-wrap: wrap;
}

.search-input {
    flex: 1;
    min-width: 230px;
}

.filter-select {
    width: 170px;
}

.month-input {
    width: 220px;
}

.dialog-card {
    min-width: 320px;
    max-width: 95vw;
    padding: 22px !important;
    background: #ffffff !important;
    border-radius: 15px !important;
}

.budget-progress {
    border-radius: 20px;
    height: 9px;
}

.budget-summary {
    padding: 10px 0;
}

/* Buttons */
.primary-button {
    background: #2563eb !important;
    color: #ffffff !important;
    font-weight: 750 !important;
    border-radius: 9px !important;
    min-height: 42px;
    padding: 0 18px;
    box-shadow: 0 3px 10px rgba(37, 99, 235, .14);
    transition: background .2s ease, transform .2s ease;
}

.primary-button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px);
}

.q-btn {
    text-transform: none !important;
}

/* Separators and charts */
.q-separator {
    background: #e5eaf3 !important;
}

.echarts {
    background: #ffffff;
    border-radius: 10px;
}

/* Mobile layout */
@media (max-width: 850px) {
    .app-layout {
        flex-direction: column !important;
    }

    .sidebar {
        width: 100% !important;
        min-width: 0;
        min-height: auto;
        padding: 13px;
        border-right: none;
        border-bottom: 1px solid #e5eaf3;
    }

    .sidebar .nav-section,
    .sidebar .sidebar-profile {
        display: none;
    }

    .main-panel {
        padding: 17px;
    }

    .page-title {
        font-size: 24px !important;
    }

    .dashboard-cards {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 480px) {
    .dashboard-cards {
        grid-template-columns: 1fr;
    }

    .auth-card {
        padding: 23px !important;
    }

    .main-panel {
        padding: 13px;
    }
}
</style>
"""


def get_user_id():
    return app.storage.user.get("user_id")


def logout():
    app.storage.user.pop("user_id", None)
    ui.navigate.to("/")


def render_shell(user_id, page_title, render_content):
    user = database.get_user(user_id)

    if not user:
        app.storage.user.pop("user_id", None)
        ui.navigate.to("/")
        return

    with ui.row().classes("app-layout no-wrap"):
        with ui.column().classes("sidebar gap-2"):
            ui.label("FLOARA").classes("brand")
            ui.label("PERSONAL FINANCE").classes("brand-caption")

            ui.separator()

            ui.label("WORKSPACE").classes("nav-section")

            navigation = [
                ("dashboard", "Dashboard", "/dashboard"),
                ("add_circle_outline", "Add transaction", "/expenses"),
                ("receipt_long", "Transactions", "/transactions"),
                ("account_balance_wallet", "Budget planner", "/budgets"),
                ("analytics", "Reports & analytics", "/reports"),
            ]

            for icon_name, label, path in navigation:
                ui.button(
                    label,
                    icon=icon_name,
                    on_click=lambda destination=path: ui.navigate.to(destination)
                ).props("flat").classes("nav-button")

            ui.label("PREFERENCES").classes("nav-section")

            ui.button(
                "Settings",
                icon="settings",
                on_click=lambda: ui.navigate.to("/settings")
            ).props("flat").classes("nav-button")

            ui.space()

            with ui.column().classes("sidebar-profile w-full gap-1"):
                ui.label(user["name"]).classes("strong-text")
                ui.label(user["email"]).classes("small-text")
                ui.button(
                    "Sign out",
                    icon="logout",
                    on_click=logout
                ).props("flat color=primary").classes("w-full")

        with ui.column().classes("main-panel"):
            with ui.row().classes("topbar justify-between items-center"):
                ui.label(page_title).classes("topbar-title")
                ui.label("FLOARA  /  PERSONAL FINANCE").classes("topbar-caption")

            render_content()


def require_login():
    user_id = get_user_id()
    if not user_id:
        ui.navigate.to("/")
        return None

    if not database.get_user(user_id):
        app.storage.user.pop("user_id", None)
        ui.navigate.to("/")
        return None

    return user_id


@ui.page("/")
def login_page():
    if get_user_id():
        ui.navigate.to("/dashboard")
        return
    auth.render_login()


@ui.page("/signup")
def signup_page():
    if get_user_id():
        ui.navigate.to("/dashboard")
        return
    auth.render_signup()


@ui.page("/dashboard")
def dashboard_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Dashboard",
            lambda: dashboard.render_dashboard(user_id)
        )


@ui.page("/expenses")
def expenses_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Add transaction",
            lambda: expenses.render_expenses(user_id)
        )


@ui.page("/transactions")
def transactions_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Transactions",
            lambda: transactions.render_transactions(user_id)
        )


@ui.page("/budgets")
def budgets_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Budget planner",
            lambda: budgets.render_budgets(user_id)
        )


@ui.page("/reports")
def reports_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Reports & analytics",
            lambda: reports.render_reports(user_id)
        )


@ui.page("/settings")
def settings_page():
    user_id = require_login()
    if user_id:
        render_shell(
            user_id, "Settings",
            lambda: settings.render_settings(user_id)
        )


database.init_db()
ui.add_head_html(CUSTOM_CSS, shared=True)

ui.run(
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8080")),
    title="FLOARA Expense",
    storage_secret=os.getenv(
        "STORAGE_SECRET",
        "replace-this-with-a-long-random-secret-before-deployment"
    ),
)