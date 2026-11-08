from __future__ import annotations

from typing import Any

import streamlit as st


VAT_RATE = 0.15
SERVICES = {
    "Classic Manicure & Pedicure": {"price": 150.0, "per_nail": False},
    "Hand Nail Cleaning": {"price": 70.0, "per_nail": False},
    "Quick Care / Express": {"price": 60.0, "per_nail": False},
    "Classic Regular Nail Polish": {"price": 50.0, "per_nail": False},
    "Gel Polish": {"price": 140.0, "per_nail": False},
    "Nail Art": {"price": 15.0, "per_nail": True},
    "Paraffin Hand Treatment": {"price": 80.0, "per_nail": False},
    "Acrylic Extensions": {"price": 250.0, "per_nail": False},
    "Nail Repair": {"price": 20.0, "per_nail": True},
}
DAYS = ["Saturday", "Sunday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def format_sar(amount: float) -> str:
    return f"SAR {amount:,.2f}"


def display_introduction() -> None:
    st.title("Luna Nails")
    st.subheader("Book your appointment")
    st.write(
        "Choose your nail services and a time that works for you. "
        "Your invoice will include 15% VAT."
    )


def get_customer_info() -> tuple[str, str]:
    st.header("1. Your details")
    name = st.text_input("Customer name", placeholder="Enter your name")
    phone = st.text_input("Phone number", placeholder="Enter your phone number")
    return name, phone


def get_service_selections() -> tuple[list[dict[str, Any]], float]:
    st.header("2. Choose your services")

    service = st.selectbox(
        "Service",
        options=list(SERVICES),
        format_func=lambda name: (
            f"{name} — {format_sar(SERVICES[name]['price'])} per nail"
            if SERVICES[name]["per_nail"]
            else f"{name} — {format_sar(SERVICES[name]['price'])}"
        ),
        key="service_choice",
    )

    nail_count: int | None = None
    if SERVICES[service]["per_nail"]:
        raw_nail_count = st.text_input(
            "Number of nails",
            placeholder="Enter a number from 1 to 10",
            key="nail_count",
        ).strip()
        if raw_nail_count:
            try:
                nail_count = int(raw_nail_count)
            except ValueError:
                nail_count = None

    add_error = None
    if st.button("Add Service", type="primary", use_container_width=True):
        if SERVICES[service]["per_nail"]:
            raw_nail_count = st.session_state.get("nail_count", "").strip()
            try:
                nail_count = int(raw_nail_count)
            except (TypeError, ValueError):
                nail_count = None

            if nail_count is None or not 1 <= nail_count <= 10:
                add_error = "Please enter a number of nails from 1 to 10"

        if add_error is None:
            price = SERVICES[service]["price"]
            if SERVICES[service]["per_nail"]:
                price *= nail_count
            st.session_state.setdefault("selected_services", []).append(
                {
                    "name": service,
                    "nails": nail_count if SERVICES[service]["per_nail"] else None,
                    "price": price,
                }
            )
            st.session_state.pop("invoice", None)
            st.success(f"{service} added.")

    if add_error:
        st.error(add_error)

    selected_services = st.session_state.setdefault("selected_services", [])
    st.subheader("Added services")
    if selected_services:
        for item in selected_services:
            label = item["name"]
            if item["nails"] is not None:
                label += f" ({item['nails']} nails)"
            st.write(f"{label} — {format_sar(item['price'])}")
    else:
        st.caption("No services added yet.")

    service_total = sum(item["price"] for item in selected_services)
    if selected_services:
        st.write(f"**Service total: {format_sar(service_total)}**")
    return selected_services, service_total


def reset_time_choice() -> None:
    st.session_state["time_choice"] = None


def times_for_day(day: str | None) -> list[str]:
    if day is None:
        return []
    first_hour = 13 if day == "Friday" else 10
    times = []
    for hour in range(first_hour, 22):
        hour_12 = hour % 12 or 12
        suffix = "PM" if hour >= 12 else "AM"
        times.append(f"{hour_12}:00 {suffix}")
    return times


def get_appointment_selection() -> tuple[str | None, str | None]:
    st.header("3. Choose an appointment")
    day = st.selectbox(
        "Day",
        options=DAYS,
        index=None,
        placeholder="Choose a day",
        key="day_choice",
        on_change=reset_time_choice,
    )
    time_options = times_for_day(day)
    time = st.selectbox(
        "Time",
        options=time_options,
        index=None,
        placeholder="Choose a time" if day else "Choose a day first",
        key="time_choice",
        disabled=day is None,
    )
    return day, time


def process_booking(
    service_total: float, day_choice: str | None, time_choice: str | None
) -> dict[str, Any]:
    tax = service_total * VAT_RATE
    return {
        "day": day_choice,
        "time": time_choice,
        "tax": tax,
        "total": service_total + tax,
    }


def display_invoice(
    name: str,
    phone: str,
    booking: dict[str, Any],
    services: list[dict[str, Any]],
    service_total: float,
) -> None:
    st.divider()
    st.header("Luna Nails Booking Invoice")
    customer_col, appointment_col = st.columns(2)
    with customer_col:
        st.write(f"**Customer:** {name.strip()}")
        st.write(f"**Phone:** {phone.strip()}")
    with appointment_col:
        st.write(f"**Appointment day:** {booking['day']}")
        st.write(f"**Appointment time:** {booking['time']}")

    st.subheader("Services")
    for item in services:
        label = item["name"]
        if item["nails"] is not None:
            label += f" ({item['nails']} nails)"
        st.write(f"{label} — {format_sar(item['price'])}")

    st.divider()
    st.write(f"**Service total:** {format_sar(service_total)}")
    st.write(f"**VAT (15%):** {format_sar(booking['tax'])}")
    st.subheader(f"Total: {format_sar(booking['total'])}")
    st.write("Thank you for choosing Luna Nails!")


def main() -> None:
    st.set_page_config(page_title="Luna Nails Booking", page_icon=None)
    display_introduction()

    name, phone = get_customer_info()
    services, service_total = get_service_selections()
    day_choice, time_choice = get_appointment_selection()

    if st.button("Show Invoice", type="primary", use_container_width=True):
        errors = []
        if not name.strip():
            errors.append("Please enter your name")
        if not phone.strip():
            errors.append("Please enter your phone number")
        if not services:
            errors.append("Please add at least one service")
        selected_service = st.session_state.get("service_choice")
        if (
            selected_service in SERVICES
            and SERVICES[selected_service]["per_nail"]
        ):
            raw_nail_count = st.session_state.get("nail_count", "").strip()
            try:
                current_nail_count = int(raw_nail_count)
            except (TypeError, ValueError):
                current_nail_count = None
            if current_nail_count is None or not 1 <= current_nail_count <= 10:
                errors.append("Please enter a number of nails from 1 to 10")
        if not day_choice:
            errors.append("Please choose a day")
        if not time_choice:
            errors.append("Please choose a time")

        if errors:
            st.session_state.pop("invoice", None)
            for error in errors:
                st.error(error)
        else:
            st.session_state["invoice"] = {
                "name": name.strip(),
                "phone": phone.strip(),
                "services": [
                    dict(item)
                    for item in services
                ],
                "service_total": service_total,
                "booking": process_booking(
                    service_total, day_choice, time_choice
                ),
            }

    invoice = st.session_state.get("invoice")
    if invoice:
        current_services = [dict(item) for item in services]
        is_current = (
            invoice["name"] == name.strip()
            and invoice["phone"] == phone.strip()
            and invoice["services"] == current_services
            and invoice["booking"]["day"] == day_choice
            and invoice["booking"]["time"] == time_choice
        )
        if is_current:
            display_invoice(
                invoice["name"],
                invoice["phone"],
                invoice["booking"],
                invoice["services"],
                invoice["service_total"],
            )
        else:
            st.session_state.pop("invoice", None)


if __name__ == "__main__":
    main()
