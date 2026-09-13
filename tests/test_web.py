import pytest
from smart_clinic.web.state import State
from smart_clinic.web import styles

def test_web_state_attributes():
    state = State()
    assert hasattr(state, "auth_role")
    assert hasattr(state, "patient_lookup_input")
    assert hasattr(state, "patient_search_query")
    assert hasattr(state, "doctor_profile")

def test_web_styles_theme():
    assert hasattr(styles, "PRIMARY")
    assert hasattr(styles, "SURFACE")
    assert hasattr(styles, "FONT_HEADLINE")
    assert styles.PRIMARY is not None
