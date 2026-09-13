import reflex as rx

config = rx.Config(
    app_name="web",
    telemetry_enabled=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                accent_color="indigo",
            )
        ),
    ],
)
