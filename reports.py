from nicegui import ui
import database


def render_reports(user_id):
    ui.label("Reports & analytics").classes("page-title")
    ui.label("Understand your income and spending patterns.").classes("page-subtitle")

    monthly = list(reversed(database.get_monthly_totals(user_id)))
    categories = database.get_category_totals(user_id)

    if monthly:
        total_income = sum(float(row["income"] or 0) for row in monthly)
        total_expenses = sum(float(row["expenses"] or 0) for row in monthly)

        with ui.row().classes("dashboard-cards"):
            with ui.card().classes("stat-card stat-green"):
                ui.label("Income in shown period").classes("stat-title")
                ui.label(f"₹{total_income:,.2f}").classes("stat-number")

            with ui.card().classes("stat-card stat-red"):
                ui.label("Expenses in shown period").classes("stat-title")
                ui.label(f"₹{total_expenses:,.2f}").classes("stat-number")

        with ui.card().classes("content-card w-full"):
            ui.label("Monthly income vs expenses").classes("card-heading")

            ui.echart({
                "tooltip": {"trigger": "axis"},
                "legend": {
                    "data": ["Income", "Expenses"],
                    "textStyle": {"color": "#475569"}
                },
                "grid": {
                    "left": "3%", "right": "4%",
                    "bottom": "8%", "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": [row["month"] for row in monthly],
                    "axisLabel": {"color": "#475569"}
                },
                "yAxis": {
                    "type": "value",
                    "axisLabel": {"color": "#475569"}
                },
                "series": [
                    {
                        "name": "Income",
                        "type": "bar",
                        "data": [float(row["income"] or 0) for row in monthly],
                        "itemStyle": {
                            "color": "#16a34a",
                            "borderRadius": [5, 5, 0, 0]
                        }
                    },
                    {
                        "name": "Expenses",
                        "type": "bar",
                        "data": [float(row["expenses"] or 0) for row in monthly],
                        "itemStyle": {
                            "color": "#2563eb",
                            "borderRadius": [5, 5, 0, 0]
                        }
                    }
                ]
            }).classes("w-full h-80")
    else:
        ui.label("Add transactions to generate monthly reports.").classes("empty-state")

    with ui.card().classes("content-card w-full"):
        ui.label("Expense breakdown by category").classes("card-heading")

        if categories:
            ui.echart({
                "tooltip": {"trigger": "item"},
                "legend": {
                    "bottom": 0,
                    "textStyle": {"color": "#475569"}
                },
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "68%"],
                    "label": {"color": "#334155"},
                    "data": [
                        {
                            "name": row["category"],
                            "value": float(row["total"])
                        }
                        for row in categories
                    ]
                }]
            }).classes("w-full h-80")

            for row in categories:
                with ui.row().classes("transaction-item w-full justify-between"):
                    ui.label(row["category"]).classes("strong-text")
                    ui.label(f"₹{row['total']:,.2f}").classes("amount-text")
        else:
            ui.label("No expense categories to report yet.").classes("empty-state")