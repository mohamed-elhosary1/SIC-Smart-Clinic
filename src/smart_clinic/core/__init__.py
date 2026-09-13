"""Smart Clinic Core Package."""

from .exceptions import (
    ClinicError,
    InvalidAppointmentTimeError,
    DuplicateBookingError,
    PatientNotFoundError,
    DoctorNotFoundError,
    InvalidFormatError,
)
from .auth import (
    User,
    StaffUser,
    DoctorUser,
    USERS_DB,
    authenticate,
)
from .models import (
    Person,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
    WaitingQueueIterator,
    DEFAULT_APPOINTMENT_DURATION,
)
from .validators import (
    validate_patient_id,
    validate_doctor_id,
    validate_phone,
    parse_patient_type,
    parse_status,
    parse_menu_choice,
)
from .triage import (
    make_triage_calculator,
    find_visits_recursive,
)
from .persistence import (
    get_data_path,
    get_report_path,
    REPO_ROOT,
    DATA_DIR,
)
from .manager import ClinicManager

__all__ = [
    "ClinicError",
    "InvalidAppointmentTimeError",
    "DuplicateBookingError",
    "PatientNotFoundError",
    "DoctorNotFoundError",
    "InvalidFormatError",
    "User",
    "StaffUser",
    "DoctorUser",
    "USERS_DB",
    "authenticate",
    "Person",
    "Patient",
    "EmergencyPatient",
    "RegularPatient",
    "Doctor",
    "Appointment",
    "WaitingQueueIterator",
    "DEFAULT_APPOINTMENT_DURATION",
    "validate_patient_id",
    "validate_doctor_id",
    "validate_phone",
    "parse_patient_type",
    "parse_status",
    "parse_menu_choice",
    "make_triage_calculator",
    "find_visits_recursive",
    "get_data_path",
    "get_report_path",
    "REPO_ROOT",
    "DATA_DIR",
    "ClinicManager",
]
