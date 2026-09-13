"""Smart Clinic Entry Point.

This module provides backwards-compatible access and entry points:
    - python main.py         -> Interactive Terminal CLI
    - python main.py --web   -> Modern Reflex Web Application

Architecture:
    All domain models, business logic, and persistence are located in
    `smart_clinic.core`. The CLI interface is located in `smart_clinic.cli`.
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path
SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

# Re-export core domain entities for 100% backward compatibility
from smart_clinic.core import (
    ClinicManager,
    Person,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
    WaitingQueueIterator,
    User,
    StaffUser,
    DoctorUser,
    USERS_DB,
    authenticate,
    ClinicError,
    DuplicateBookingError,
    InvalidAppointmentTimeError,
    PatientNotFoundError,
    DoctorNotFoundError,
    InvalidFormatError,
    validate_patient_id,
    validate_doctor_id,
    validate_phone,
    parse_patient_type,
    parse_status,
    parse_menu_choice,
    make_triage_calculator,
    find_visits_recursive,
    get_data_path,
    get_report_path,
    DEFAULT_APPOINTMENT_DURATION,
)

# Re-export CLI functions for backward compatibility
from smart_clinic.cli import (
    cli_main,
    opening_screen,
    login_screen,
    run_staff_menu,
    run_doctor_menu,
    run_patient_portal,
    patient_lookup,
    print_section_header,
)

# Shared manager instance for backwards-compatible scripts
clinic_manager = ClinicManager()


def main():
    if "--web" in sys.argv:
        import subprocess
        print("\n" + "=" * 56)
        print("  SMART CLINIC - STARTING MODERN REFLEX WEB APPLICATION  ")
        print("=" * 56)
        print("[INFO] Launching Reflex Web Server on http://localhost:3000 ...\n")
        subprocess.run(["reflex", "run"])
    else:
        cli_main()


if __name__ == "__main__":
    main()
