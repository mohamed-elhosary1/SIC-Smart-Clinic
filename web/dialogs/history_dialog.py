import reflex as rx
from web import styles
from web.state import State


def history_row(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(item["date_str"], font_size="13px", font_weight="500")),
        rx.table.cell(rx.hstack(rx.text("Dr. ", font_size="13px", font_weight="600"), rx.text(item["doctor_name"], font_size="13px", font_weight="600"), spacing="0")),
        rx.table.cell(rx.text(item["specialty"], font_size="13px", color=styles.ON_SURFACE_VARIANT)),
        rx.table.cell(rx.text(item["case_type"], font_size="13px")),
        rx.table.cell(rx.text(item["fee_str"], font_size="13px", font_weight="700", color=styles.PRIMARY_CONTAINER)),
        rx.table.cell(rx.badge("COMPLETED", size="1", color_scheme="green", variant="surface")),
    )


def history_dialog() -> rx.Component:
    """Render Patient Medical History Modal with Memoization status."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon("file-text", size=20, color=styles.PRIMARY_CONTAINER),
                        width="36px",
                        height="36px",
                        border_radius="8px",
                        background_color=styles.SURFACE_CONTAINER,
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.hstack(
                                rx.text("Medical History: ", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                rx.text(State.history_patient_name, font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                spacing="0",
                            ),
                            rx.badge(State.history_patient_id, size="1", color_scheme="gray"),
                            # Subtle Memoization Cache Hit indicator
                            rx.cond(
                                State.history_is_cache_hit,
                                rx.badge("⚡ CACHE HIT (Memoized)", size="1", color_scheme="teal", variant="solid"),
                                rx.badge("COMPUTED RECURSIVELY", size="1", color_scheme="indigo", variant="surface"),
                            ),
                            align_items="center",
                            spacing="2",
                        ),
                        rx.text(
                            "Completed clinical consultations filtered via recursive memoization",
                            font_size="13px",
                            color=styles.ON_SURFACE_VARIANT,
                        ),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=18, color=styles.OUTLINE),
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            on_click=State.close_history_modal,
                        )
                    ),
                    align_items="center",
                    width="100%",
                ),
                padding="18px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_bottom=f"1px solid {styles.BORDER}",
            ),
            rx.box(
                rx.cond(
                    State.history_visits.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Date & Time"),
                                rx.table.column_header_cell("Attending Doctor"),
                                rx.table.column_header_cell("Specialty"),
                                rx.table.column_header_cell("Case / Note"),
                                rx.table.column_header_cell("Billed Fee"),
                                rx.table.column_header_cell("Status"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(State.history_visits, history_row),
                        ),
                        width="100%",
                        variant="surface",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("folder-open", size=32, color=styles.OUTLINE),
                            rx.text("No completed visit records found for this patient.", font_size="14px", color=styles.ON_SURFACE_VARIANT),
                            spacing="2",
                            padding="32px",
                            align_items="center",
                        ),
                        width="100%",
                    ),
                ),
                padding="20px",
                max_height="60vh",
                overflow_y="auto",
            ),
            rx.box(
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Close",
                        style=styles.BTN_SECONDARY,
                        size="3",
                        on_click=State.close_history_modal,
                    ),
                    width="100%",
                ),
                padding="16px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_top=f"1px solid {styles.BORDER}",
            ),
            max_width="800px",
            padding="0",
            border_radius="16px",
            overflow="hidden",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
        ),
        open=State.history_modal_open,
        on_open_change=State.close_history_modal,
    )
