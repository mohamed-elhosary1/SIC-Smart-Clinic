import pytest
from smart_clinic.core.auth import (
    StaffUser,
    DoctorUser,
    authenticate,
    USERS_DB,
)
from smart_clinic.core.exceptions import ClinicError

def test_staff_user_permissions():
    staff = StaffUser("staff", "staff123")
    assert staff.display_role() == "Staff"
    assert staff.has_permission("register_patient") is True
    assert staff.has_permission("book_appointment") is True
    assert staff.has_permission("cancel_appointment") is True
    assert staff.has_permission("view_reports") is True

def test_doctor_user_permissions():
    doc = DoctorUser("doctor", "doc123")
    assert doc.display_role() == "Doctor"
    assert doc.has_permission("view_queue") is True
    assert doc.has_permission("update_visit_status") is True
    assert doc.has_permission("register_patient") is False

def test_authenticate_success():
    staff = authenticate("staff", "staff123")
    assert staff is not None
    assert isinstance(staff, StaffUser)

    doctor = authenticate("doctor", "doc123")
    assert doctor is not None
    assert isinstance(doctor, DoctorUser)

def test_authenticate_failure():
    with pytest.raises(ClinicError):
        authenticate("staff", "wrong_password")
    with pytest.raises(ClinicError):
        authenticate("nonexistent_user", "pass")
    with pytest.raises(ClinicError):
        authenticate("", "")
