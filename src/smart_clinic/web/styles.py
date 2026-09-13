"""
Smart Clinic - Healthcare SaaS Design System Tokens & Styles
Based on Stitch 'Clinical Intelligence' design reference.
"""

# Core Healthcare SaaS Color Palette
PRIMARY = "#00236f"
PRIMARY_CONTAINER = "#1e3a8a"
ON_PRIMARY = "#ffffff"

SECONDARY = "#006a61"
SECONDARY_TEAL = "#0d9488"
SECONDARY_CONTAINER = "#86f2e4"
ON_SECONDARY_CONTAINER = "#006f66"

SURFACE = "#f8f9ff"
SURFACE_CONTAINER_LOWEST = "#ffffff"
SURFACE_CONTAINER_LOW = "#eff4ff"
SURFACE_CONTAINER = "#e5eeff"
SURFACE_CONTAINER_HIGH = "#dce9ff"

ON_SURFACE = "#0b1c30"
ON_SURFACE_VARIANT = "#444651"

OUTLINE = "#757682"
OUTLINE_VARIANT = "#c5c5d3"
BORDER = "#e2e8f0"

# Triage & State Matrix
ERROR = "#dc2626"
ERROR_CONTAINER = "#ffdad6"
ON_ERROR_CONTAINER = "#93000a"

REGULAR = "#0284c7"
REGULAR_CONTAINER = "#f0f9ff"

COMPLETED = "#16a34a"
COMPLETED_CONTAINER = "#f0fdf4"

PENDING = "#d97706"
PENDING_CONTAINER = "#fffbeb"

IN_PROGRESS = "#3b82f6"
IN_PROGRESS_CONTAINER = "#eff6ff"

# Fonts
FONT_HEADLINE = "'Hanken Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_BODY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

# Card Styles
CARD_STYLE = {
    "background_color": SURFACE_CONTAINER_LOWEST,
    "border": f"1px solid {BORDER}",
    "border_radius": "14px",
    "box_shadow": "0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)",
    "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "box_shadow": "0 8px 20px -4px rgba(15, 23, 42, 0.08)",
        "border_color": "#cbd5e1",
    },
}

ELEVATED_CARD_STYLE = {
    "background_color": SURFACE_CONTAINER_LOWEST,
    "border": f"1px solid {BORDER}",
    "border_radius": "16px",
    "box_shadow": "0 10px 15px -3px rgba(15, 23, 42, 0.06), 0 4px 6px -4px rgba(15, 23, 42, 0.03)",
    "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "transform": "translateY(-4px)",
        "box_shadow": "0 16px 25px -4px rgba(15, 23, 42, 0.1)",
    },
}

# Button Styles with Rich Micro-Interactions
BTN_PRIMARY = {
    "background_color": PRIMARY_CONTAINER,
    "color": ON_PRIMARY,
    "border_radius": "10px",
    "font_weight": "600",
    "font_family": FONT_BODY,
    "cursor": "pointer",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "background_color": "#172554",
        "transform": "translateY(-2px)",
        "box_shadow": "0 4px 14px rgba(30, 58, 138, 0.3)",
    },
    "_active": {
        "transform": "scale(0.97)",
    },
}

BTN_TEAL = {
    "background_color": SECONDARY_TEAL,
    "color": ON_PRIMARY,
    "border_radius": "10px",
    "font_weight": "600",
    "font_family": FONT_BODY,
    "cursor": "pointer",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "background_color": "#0f766e",
        "transform": "translateY(-2px)",
        "box_shadow": "0 4px 14px rgba(13, 148, 136, 0.3)",
    },
    "_active": {
        "transform": "scale(0.97)",
    },
}

BTN_SECONDARY = {
    "background_color": SURFACE_CONTAINER_LOW,
    "color": ON_SURFACE,
    "border": f"1px solid {BORDER}",
    "border_radius": "10px",
    "font_weight": "500",
    "font_family": FONT_BODY,
    "cursor": "pointer",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "background_color": SURFACE_CONTAINER,
        "transform": "translateY(-2px)",
        "box_shadow": "0 2px 8px rgba(0,0,0,0.06)",
    },
    "_active": {
        "transform": "scale(0.97)",
    },
}

BTN_DESTRUCTIVE = {
    "background_color": ERROR,
    "color": ON_PRIMARY,
    "border_radius": "10px",
    "font_weight": "600",
    "font_family": FONT_BODY,
    "cursor": "pointer",
    "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
    "_hover": {
        "background_color": "#b91c1c",
        "transform": "translateY(-2px)",
        "box_shadow": "0 4px 14px rgba(220, 38, 38, 0.3)",
    },
    "_active": {
        "transform": "scale(0.97)",
    },
}

# Input Styles
INPUT_STYLE = {
    "background_color": SURFACE_CONTAINER_LOWEST,
    "border": f"1px solid {BORDER}",
    "border_radius": "8px",
    "font_family": FONT_BODY,
    "color": ON_SURFACE,
    "height": "38px",
    "_focus": {"border_color": PRIMARY_CONTAINER, "box_shadow": f"0 0 0 1px {PRIMARY_CONTAINER}"},
}
