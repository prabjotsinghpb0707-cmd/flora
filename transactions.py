from nicegui import ui
import database
from expenses import CATEGORIES


def render_transactions(user_id):
    ui.label("Transactions").classes("page-title")
    ui.label("Search, review and manage your financial activity.").classes("page-subtitle")

    with ui.row().classes("filter-row w-full items-center"):
        search = ui.input(
            "Search category or description",
            placeholder="Search transactions..."
        ).props("outlined clearable").classes("search-input")

        kind = ui.select(
            ["All", "Income", "Expense"],
            value="All",
            label="Type"
        ).props("outlined").classes("filter-select")

    listing = ui.column().classes("w-full gap-2")

    def refresh():
        listing.clear()
        rows = database.get_transactions(
            user_id, kind.value, search.value or ""
        )

        with listing:
            if not rows:
                ui.label("No transactions match your search.").classes("empty-state")
                return

            for item in rows:
                with ui.row().classes("transaction-item w-full items-center"):
                    with ui.column().classes("flex-grow gap-1"):
                        ui.label(item["category"]).classes("strong-text")
                        ui.label(
                            f'{item["tx_date"]}  ·  {item["kind"]}'
                        ).classes("small-text")
                        if item["note"]:
                            ui.label(item["note"]).classes("muted-text")

                    sign = "+" if item["kind"] == "Income" else "−"
                    color = "green-text" if item["kind"] == "Income" else "red-text"
                    ui.label(f"{sign}₹{item['amount']:,.2f}").classes(
                        f"amount-text {color}"
                    )

                    ui.button(
                        icon="edit",
                        on_click=lambda row=item: edit_dialog(row)
                    ).props("flat round color=primary").tooltip("Edit")

                    ui.button(
                        icon="delete",
                        on_click=lambda row_id=item["id"]: delete_item(row_id)
                    ).props("flat round color=negative").tooltip("Delete")

    def delete_item(transaction_id):
        with ui.dialog() as dialog, ui.card().classes("dialog-card"):
            ui.label("Delete transaction?").classes("card-heading")
            ui.label("This action cannot be undone.").classes("muted-text")

            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                def confirm_delete():
                    database.delete_transaction(user_id, transaction_id)
                    dialog.close()
                    ui.notify("Transaction deleted.", type="positive")
                    refresh()

                ui.button("Delete", on_click=confirm_delete).props("color=negative")

        dialog.open()

    def edit_dialog(row):
        with ui.dialog() as dialog, ui.card().classes("dialog-card"):
            ui.label("Edit transaction").classes("card-heading")

            edit_kind = ui.select(
                ["Expense", "Income"],
                value=row["kind"],
                label="Type"
            ).props("outlined").classes("full-input")

            edit_amount = ui.number(
                "Amount (₹)",
                value=float(row["amount"]),
                min=0.01,
                step=0.01
            ).props("outlined").classes("full-input")

            edit_category = ui.select(
                CATEGORIES,
                value=row["category"] if row["category"] in CATEGORIES else "Other",
                label="Category"
            ).props("outlined").classes("full-input")

            edit_date = ui.input(
                "Date", value=row["tx_date"]
            ).props("outlined type=date").classes("full-input")

            edit_note = ui.textarea(
                "Description", value=row["note"] or ""
            ).props("outlined autogrow").classes("full-input")

            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                def save_edit():
                    try:
                        value = float(edit_amount.value)
                        if value <= 0:
                            raise ValueError
                    except (TypeError, ValueError):
                        ui.notify("Enter a valid amount.", type="warning")
                        return

                    database.update_transaction(
                        user_id,
                        row["id"],
                        edit_kind.value,
                        value,
                        edit_category.value,
                        edit_date.value,
                        edit_note.value or ""
                    )
                    dialog.close()
                    ui.notify("Transaction updated.", type="positive")
                    refresh()

                ui.button("Save changes", on_click=save_edit).classes("primary-button")

        dialog.open()

    kind.on_value_change(lambda _: refresh())
    search.on_value_change(lambda _: refresh())
    refresh()