from datetime import datetime, timedelta
import pytest

from smart_clinic.core.models import (
    Person,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
    WaitingQueueIterator,
    DEFAULT_APPOINTMENT_DURATION,
)
from smart_clinic.core.exceptions import InvalidFormatError

def test_person_base():
    p = Person("person-1", "Test Name", "01012345678")
    assert p.person_id == "person-1"
    assert p.name == "Test Name"
    assert p.phone == "01012345678"
    assert "Test Name" in str(p)

def test_patient_id_validation():
    with pytest.raises(InvalidFormatError):
        Patient("invalid_id", "Ahmed", "01012345678", 30, "Headache")

def test_patient_priority_levels():
    ep = EmergencyPatient("patient-10", "Emergency Patient", "01012345678", 40, "Trauma")
    rp = RegularPatient("patient-11", "Regular Patient", "01012345678", 25, "Consultation")
    assert ep.priority_level() == 1
    assert rp.priority_level() == 2
    assert "Emergency" in ep.display_profile()
    assert "Regular" in rp.display_profile()

def test_doctor_properties():
    doc = Doctor("doctor-1", "Dr. Sherif", "01234567890", "Neurology", availability=True)
    assert doc.specialty == "Neurology"
    assert doc.availability is True
    assert "Dr. Sherif" in doc.display_profile()

def test_appointment_duration_and_overlap():
    doc = Doctor("doctor-1", "Dr. Aly", "01000000000", "General")
    pat1 = RegularPatient("patient-1", "Pat 1", "01000000001", 20, "Checkup")
    pat2 = RegularPatient("patient-2", "Pat 2", "01000000002", 22, "Checkup")

    t1 = datetime(2026, 9, 20, 10, 0)
    appt1 = Appointment(pat1, doc, t1, status="confirmed", fee=100.0)
    
    assert appt1.end_time == t1 + DEFAULT_APPOINTMENT_DURATION
    
    # Overlapping appointment: starts 15 mins later
    t2 = datetime(2026, 9, 20, 10, 15)
    appt2 = Appointment(pat2, doc, t2, status="pending", fee=100.0)
    assert appt1.overlaps_with(appt2) is True
    assert appt1.overlaps_with(t2) is True

    # Non-overlapping appointment: starts at 10:30
    t3 = datetime(2026, 9, 20, 10, 30)
    appt3 = Appointment(pat2, doc, t3, status="pending", fee=100.0)
    assert appt1.overlaps_with(appt3) is False
    assert appt1.overlaps_with(t3) is False

def test_waiting_queue_iterator():
    doc = Doctor("doctor-1", "Dr. Aly", "01000000000", "General")
    p1 = RegularPatient("patient-1", "Regular 1", "01000000001", 20, "Flu")
    p2 = EmergencyPatient("patient-2", "Emergency 1", "01000000002", 22, "Cardiac")
    p3 = RegularPatient("patient-3", "Regular 2", "01000000003", 24, "Fever")

    a1 = Appointment(p1, doc, datetime(2026, 9, 20, 9, 0), "pending")
    a2 = Appointment(p2, doc, datetime(2026, 9, 20, 9, 30), "pending")
    a3 = Appointment(p3, doc, datetime(2026, 9, 20, 10, 0), "pending")

    # Order in queue: Emergency first (p2), then chronological regulars (p1, p3)
    queue = sorted([a1, a2, a3], key=lambda a: (a.patient.priority_level(), a.time))
    iterator = WaitingQueueIterator(queue)
    items = list(iterator)

    assert len(items) == 3
    assert items[0].patient.person_id == "patient-2"
    assert items[1].patient.person_id == "patient-1"
    assert items[2].patient.person_id == "patient-3"
