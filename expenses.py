from datetime import date
from nicegui import ui
import database


CATEGORIES = [
    "Food & Dining",
    "Shopping",
    "Transport",
    "Bills & Utilities",
    "Rent",
    "Health",
    "Education",
    "Entertainment",
    "Travel",
    "Salary",
    "Business",
    "Other",
]


def render_expenses(user_id):
    ui.label("Add transaction").classes("page-title")
    ui.label("Record money coming in or going out.").classes("page-subtitle")

    with ui.card().classes("content-card form-card"):
        kind = ui.radio(
            ["Expense", "Income"],
            value="Expense"
        ).props("inline").classes("kind-selector")

        amount = ui.number(
            "Amount (₹)", value=None, min=0.01, step=0.01
        ).props("outlined").classes("full-input")

        category = ui.select(
            CATEGORIES, value="Food & Dining", label="Category"
        ).props("outlined").classes("full-input")

        tx_date = ui.input(
            "Date", value=date.today().isoformat()
        ).props("outlined type=date").classes("full-input")

        note = ui.textarea(
            "Description",
            placeholder="Add a short note about this transaction"
        ).props("outlined autogrow").classes("full-input")

        def save():
            try:
                value = float(amount.value)
                if value <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                ui.notify("Enter an amount greater than zero.", type="warning")
                return

            if not tx_date.value:
                ui.notify("Please choose a date.", type="warning")
                return

            database.add_transaction(
                user_id,
                kind.value,
                value,
                category.value,
                tx_date.value,
                note.value or ""
            )

            ui.notify("Transaction saved successfully.", type="positive")
            ui.navigate.to("/transactions")

        with ui.row().classes("w-full justify-end"):
            ui.button("Save transaction", icon="check", on_click=save).classes("primary-button")