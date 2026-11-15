from datetime import date
from nicegui import ui
import database


CATEGORIES = [
    "Food & Dining", "Shopping", "Transport",
    "Bills & Utilities", "Rent", "Health",
    "Education", "Entertainment", "Travel", "Other"
]


def render_budgets(user_id):
    ui.label("Budget planner").classes("page-title")
    ui.label("Set monthly limits and keep your spending on track.").classes("page-subtitle")

    month = ui.input(
        "Select month", value=date.today().strftime("%Y-%m")
    ).props("outlined type=month").classes("month-input")

    with ui.card().classes("content-card form-card"):
        ui.label("Create or update a budget").classes("card-heading")

        category = ui.select(
            CATEGORIES,
            value="Food & Dining",
            label="Category"
        ).props("outlined").classes("full-input")

        amount = ui.number(
            "Monthly budget (₹)", value=None, min=0.01, step=100
        ).props("outlined").classes("full-input")

        def save():
            try:
                value = float(amount.value)
                if value <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                ui.notify("Enter a budget greater than zero.", type="warning")
                return

            if not month.value:
                ui.notify("Select a month.", type="warning")
                return

            database.save_budget(
                user_id, month.value, category.value, value
            )
            ui.notify("Budget saved.", type="positive")
            refresh()

        ui.button("Save budget", on_click=save).classes("primary-button")

    ui.label("Budget overview").classes("section-title")
    budget_list = ui.column().classes("w-full gap-3")

    def refresh():
        budget_list.clear()
        rows = database.get_budgets(user_id, month.value or "")

        with budget_list:
            if not rows:
                ui.label("No budgets set for this month yet.").classes("empty-state")
                return

            total_limit = sum(float(row["amount"]) for row in rows)
            total_spent = sum(
                database.get_budget_spent(
                    user_id, month.value, row["category"]
                )
                for row in rows
            )

            with ui.card().classes("content-card w-full"):
                ui.label("Total planned budget").classes("stat-title")
                ui.label(f"₹{total_limit:,.2f}").classes("stat-number")
                ui.label(f"Total spent: ₹{total_spent:,.2f}").classes("muted-text")
                remaining = total_limit - total_spent
                ui.label(
                    f"Remaining: ₹{remaining:,.2f}"
                ).classes("green-text" if remaining >= 0 else "red-text")

            for row in rows:
                limit = float(row["amount"])
                spent = database.get_budget_spent(
                    user_id, month.value, row["category"]
                )
                progress = min(spent / limit, 1) if limit else 0
                remaining = limit - spent

                with ui.card().classes("content-card w-full"):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label(row["category"]).classes("strong-text")
                        ui.label(f"{progress * 100:.0f}% used").classes("muted-text")

                    ui.linear_progress(value=progress).classes("budget-progress")

                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label(f"Spent ₹{spent:,.2f}").classes("small-text")
                        ui.label(f"Limit ₹{limit:,.2f}").classes("small-text")

                    if remaining >= 0:
                        ui.label(f"₹{remaining:,.2f} remaining").classes("green-text")
                    else:
                        ui.label(
                            f"Over budget by ₹{-remaining:,.2f}"
                        ).classes("red-text")

                    ui.button(
                        "Remove budget",
                        icon="delete",
                        on_click=lambda budget_id=row["id"]: remove_budget(budget_id)
                    ).props("flat color=negative")

    def remove_budget(budget_id):
        database.delete_budget(user_id, budget_id)
        ui.notify("Budget removed.", type="positive")
        refresh()

    month.on_value_change(lambda _: refresh())
    refresh()