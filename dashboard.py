from datetime import date
from nicegui import ui
import database


def money(value):
    return f"₹{value:,.2f}"


def render_dashboard(user_id):
    data = database.get_dashboard_data(user_id)
    month = date.today().strftime("%Y-%m")
    budgets = database.get_budgets(user_id, month)
    categories = database.get_category_totals(user_id, month)

    ui.label("Dashboard").classes("page-title")
    ui.label("Your financial overview at a glance.").classes("page-subtitle")

    with ui.row().classes("dashboard-cards"):
        stat_card("Total balance", money(data["balance"]), "Available balance", "blue")
        stat_card("Total income", money(data["income"]), "All recorded income", "green")
        stat_card("Total expenses", money(data["expenses"]), "All recorded expenses", "red")
        stat_card("Transactions", str(data["count"]), "All recorded entries", "purple")

    ui.label("This month").classes("section-title")

    with ui.row().classes("dashboard-cards"):
        stat_card("Monthly income", money(data["monthly_income"]), month, "green")
        stat_card("Monthly expenses", money(data["monthly_expenses"]), month, "red")
        stat_card("Monthly savings", money(data["monthly_savings"]), "Income minus expenses", "blue")

    with ui.grid(columns=2).classes("w-full gap-4"):
        with ui.card().classes("content-card"):
            ui.label("Expense breakdown").classes("card-heading")

            if categories:
                ui.echart({
                    "tooltip": {"trigger": "item"},
                    "legend": {
                        "bottom": 0,
                        "textStyle": {"color": "#475569"}
                    },
                    "series": [{
                        "type": "pie",
                        "radius": ["42%", "70%"],
                        "avoidLabelOverlap": True,
                        "label": {"color": "#334155"},
                        "data": [
                            {
                                "name": row["category"],
                                "value": float(row["total"])
                            }
                            for row in categories
                        ]
                    }]
                }).classes("w-full h-72")
            else:
                ui.label("Your expense chart will appear after you add expenses.").classes("empty-state")

        with ui.card().classes("content-card"):
            ui.label("Monthly budget progress").classes("card-heading")

            if budgets:
                for budget in budgets:
                    limit = float(budget["amount"])
                    spent = database.get_budget_spent(
                        user_id, month, budget["category"]
                    )
                    progress = min(spent / limit, 1) if limit else 0
                    remaining = limit - spent

                    with ui.column().classes("w-full gap-1 budget-summary"):
                        with ui.row().classes("w-full justify-between"):
                            ui.label(budget["category"]).classes("strong-text")
                            ui.label(f"{progress * 100:.0f}%").classes("muted-text")

                        ui.linear_progress(value=progress).classes("budget-progress")

                        with ui.row().classes("w-full justify-between"):
                            ui.label(f"Spent {money(spent)}").classes("small-text")
                            if remaining >= 0:
                                ui.label(f"Left {money(remaining)}").classes("small-text green-text")
                            else:
                                ui.label(f"Over by {money(-remaining)}").classes("small-text red-text")
            else:
                ui.label("No budgets set for this month.").classes("empty-state")
                ui.button(
                    "Create a budget",
                    on_click=lambda: ui.navigate.to("/budgets")
                ).classes("primary-button")

    with ui.card().classes("content-card w-full"):
        with ui.row().classes("w-full justify-between items-center"):
            ui.label("Recent transactions").classes("card-heading")
            ui.link("View all", "/transactions").classes("auth-link")

        if data["recent"]:
            for item in data["recent"]:
                with ui.row().classes("transaction-item w-full items-center"):
                    with ui.column().classes("flex-grow gap-1"):
                        ui.label(item["category"]).classes("strong-text")
                        ui.label(
                            f'{item["tx_date"]}  ·  {item["kind"]}'
                        ).classes("small-text")

                    sign = "+" if item["kind"] == "Income" else "−"
                    color = "green-text" if item["kind"] == "Income" else "red-text"
                    ui.label(f"{sign}{money(item['amount'])}").classes(
                        f"amount-text {color}"
                    )
        else:
            ui.label("No transactions yet. Add your first income or expense.").classes("empty-state")

    with ui.row().classes("w-full justify-end"):
        ui.button(
            "Add transaction",
            icon="add",
            on_click=lambda: ui.navigate.to("/expenses")
        ).classes("primary-button")


def stat_card(title, value, hint, color):
    with ui.card().classes(f"stat-card stat-{color}"):
        ui.label(title).classes("stat-title")
        ui.label(value).classes("stat-number")
        ui.label(hint).classes("stat-hint")