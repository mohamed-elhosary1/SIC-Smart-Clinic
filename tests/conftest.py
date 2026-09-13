import sys
from pathlib import Path
from datetime import datetime, timedelta
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from smart_clinic.core import (
    ClinicManager,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
    StaffUser,
    DoctorUser,
    DEFAULT_APPOINTMENT_DURATION,
)

@pytest.fixture
def fresh_manager():
    """Return a fresh in-memory ClinicManager with default base fee."""
    return ClinicManager(base_fee=100.0)

@pytest.fixture
def sample_doctor():
    return Doctor(
        person_id="doctor-1",
        name="Magdi Yacoub",
        phone="01012345678",
        specialty="Cardiology",
        availability=True,
    )

@pytest.fixture
def sample_emergency_patient():
    return EmergencyPatient(
        person_id="patient-1",
        name="Mohamed Salah",
        phone="01099998888",
        age=32,
        case_type="Acute Chest Pain",
    )

@pytest.fixture
def sample_regular_patient():
    return RegularPatient(
        person_id="patient-2",
        name="Omar Marmoush",
        phone="01188887777",
        age=26,
        case_type="Routine Knee Check",
    )

@pytest.fixture
def populated_manager(fresh_manager, sample_doctor, sample_emergency_patient, sample_regular_patient):
    fresh_manager.add_doctor(sample_doctor)
    fresh_manager.register_patient(sample_emergency_patient)
    fresh_manager.register_patient(sample_regular_patient)
    return fresh_manager
