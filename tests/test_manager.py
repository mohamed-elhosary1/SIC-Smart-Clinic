from datetime import datetime, timedelta
import pytest

from smart_clinic.core.exceptions import (
    ClinicError,
    DuplicateBookingError,
    InvalidAppointmentTimeError,
    PatientNotFoundError,
    DoctorNotFoundError,
)
from smart_clinic.core.models import (
    EmergencyPatient,
    RegularPatient,
    Doctor,
)

def test_add_and_get_patient(fresh_manager, sample_regular_patient):
    fresh_manager.register_patient(sample_regular_patient)
    retrieved = fresh_manager.patients.get(sample_regular_patient.person_id)
    assert retrieved is not None
    assert retrieved.name == sample_regular_patient.name

    with pytest.raises(DuplicateBookingError):
        fresh_manager.register_patient(sample_regular_patient)

def test_add_and_get_doctor(fresh_manager, sample_doctor):
    fresh_manager.add_doctor(sample_doctor)
    retrieved = fresh_manager.doctors.get(sample_doctor.person_id)
    assert retrieved is not None
    assert retrieved.name == sample_doctor.name

    with pytest.raises(DuplicateBookingError):
        fresh_manager.add_doctor(sample_doctor)

def test_book_appointment_and_overlap_collision(populated_manager, sample_doctor, sample_regular_patient, sample_emergency_patient):
    slot = datetime(2026, 9, 25, 11, 0)
    appt = populated_manager.book_appointment(
        patient_id=sample_regular_patient.person_id,
        doctor_id=sample_doctor.person_id,
        time=slot,
    )
    assert appt is not None
    assert appt.status == "pending"
    assert appt.fee == 100.0

    # Collision test: same doctor, same time slot
    with pytest.raises(DuplicateBookingError):
        populated_manager.book_appointment(
            patient_id=sample_emergency_patient.person_id,
            doctor_id=sample_doctor.person_id,
            time=slot,
        )

    # Partial collision test: 15 mins inside 30-min window
    with pytest.raises(DuplicateBookingError):
        populated_manager.book_appointment(
            patient_id=sample_emergency_patient.person_id,
            doctor_id=sample_doctor.person_id,
            time=slot + timedelta(minutes=15),
        )

def test_triage_fee_closure_pricing(populated_manager, sample_doctor, sample_emergency_patient):
    # Emergency patient pricing: base fee + emergency surcharge computed via closure
    slot = datetime(2026, 9, 26, 14, 0)
    appt = populated_manager.book_appointment(
        patient_id=sample_emergency_patient.person_id,
        doctor_id=sample_doctor.person_id,
        time=slot,
    )
    # Emergency triage fee: 100 + 50 (first emergency) = 150.0
    assert appt.fee >= 150.0

def test_waiting_queue_prioritization(populated_manager, sample_doctor, sample_regular_patient, sample_emergency_patient):
    # Regular patient booked at 09:00
    populated_manager.book_appointment(
        patient_id=sample_regular_patient.person_id,
        doctor_id=sample_doctor.person_id,
        time=datetime(2026, 9, 27, 9, 0),
    )
    # Emergency patient booked later at 11:00
    populated_manager.book_appointment(
        patient_id=sample_emergency_patient.person_id,
        doctor_id=sample_doctor.person_id,
        time=datetime(2026, 9, 27, 11, 0),
    )

    queue = populated_manager.sort_queue_by_priority()
    assert len(queue) == 2
    # Emergency patient MUST be first in the queue
    assert queue[0].patient.person_id == sample_emergency_patient.person_id
    assert queue[1].patient.person_id == sample_regular_patient.person_id

def test_cancel_appointment(populated_manager, sample_doctor, sample_regular_patient):
    slot = datetime(2026, 9, 28, 10, 0)
    appt = populated_manager.book_appointment(
        patient_id=sample_regular_patient.person_id,
        doctor_id=sample_doctor.person_id,
        time=slot,
    )
    assert slot in populated_manager.booked_date[sample_doctor.person_id]

    populated_manager.update_visit_status(0, "cancelled")
    assert appt.status == "cancelled"
    assert slot not in populated_manager.booked_date[sample_doctor.person_id]
