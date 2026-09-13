"""CLI Menus, authentication screens, and main execution loop."""

import sys
from smart_clinic.core import (
    ClinicManager,
    User,
    StaffUser,
    DoctorUser,
    authenticate,
    ClinicError,
    parse_menu_choice,
)
from .actions import (
    print_section_header,
    action_register_patient,
    action_add_doctor,
    action_book_appointment,
    action_update_visit_status,
    action_show_queue,
    action_toggle_doctor_availability,
    action_delete_appointment,
    action_daily_report,
    action_save_data,
    action_reset_data,
    action_export_report,
    action_patient_history,
    action_view_own_appointments,
    action_view_own_queue_position,
    action_view_own_history,
    action_cloud_sync,
)

def run_staff_menu(manager: ClinicManager, current_user: StaffUser):
    """Staff Menu - 13 operations covering administration, reporting, and maintenance."""
    while True:
        menu_title = f"CLINIC MAIN MENU - {current_user.display_role()}"
        print("\n+" + "=" * 54 + "+")
        print("|" + menu_title.center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] Register Patient     : Add new patient record   |")
        print("|  [2] Add Doctor           : Register medical doctor  |")
        print("|  [3] Book Appointment     : Schedule 30-min visit    |")
        print("|  [4] Update Visit Status  : Manage appointment state |")
        print("|  [5] Show Waiting Queue   : View prioritized queue   |")
        print("|  [6] Toggle Doctor Status : Set available / busy     |")
        print("|  [7] Delete Appointment   : Remove record & free slot|")
        print("|  [8] Daily Report         : View clinic statistics   |")
        print("|  [9] Save Data Now        : Save database to JSON    |")
        print("|  [10] Reset Clinic Data   : Clear all saved records  |")
        print("|  [11] Export Report       : Save daily report to txt |")
        print("|  [12] Patient History     : View completed visits    |")
        print("|  [13] Cloud Sync & Recovery: Push / Pull Cloud state  |")
        print("|  [14] Logout / Switch User                           |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-14 or action name): ").strip()
        choice = parse_menu_choice(raw_choice)

        if choice == "1":
            action_register_patient(manager)
        elif choice == "2":
            action_add_doctor(manager)
        elif choice == "3":
            action_book_appointment(manager)
        elif choice == "4":
            action_update_visit_status(manager)
        elif choice == "5":
            action_show_queue(manager)
        elif choice == "6":
            action_toggle_doctor_availability(manager)
        elif choice == "7":
            action_delete_appointment(manager)
        elif choice == "8":
            action_daily_report(manager)
        elif choice == "9":
            action_save_data(manager)
        elif choice == "10":
            action_reset_data(manager)
        elif choice == "11":
            action_export_report(manager)
        elif choice == "12":
            action_patient_history(manager)
        elif choice in ("13", "sync", "cloud", "cloud sync"):
            action_cloud_sync(manager)
        elif choice == "14":
            print(f"\nLogging out {current_user.display_role()} ({current_user.username})...")
            manager.save_to_file("clinic_data.json", silent=True)
            return
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please select from 1 to 14.\n")


def run_doctor_menu(manager: ClinicManager, current_user: DoctorUser):
    """Doctor Portal - Scoped clinical actions for medical staff."""
    while True:
        menu_title = f"DOCTOR PORTAL - Dr. {current_user.username}"
        print("\n+" + "=" * 54 + "+")
        print("|" + menu_title.center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] Show Waiting Queue   : View prioritized queue   |")
        print("|  [2] Update Visit Status  : Set status of visit      |")
        print("|  [3] Daily Report         : View clinic statistics   |")
        print("|  [4] Patient History      : View completed visits    |")
        print("|  [5] Logout / Switch User                            |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-5): ").strip().lower()

        if raw_choice in ("1", "queue", "show queue"):
            action_show_queue(manager)
        elif raw_choice in ("2", "update", "status"):
            action_update_visit_status(manager)
        elif raw_choice in ("3", "report", "daily report"):
            action_daily_report(manager)
        elif raw_choice in ("4", "history", "patient history"):
            action_patient_history(manager)
        elif raw_choice in ("5", "logout", "exit", "quit"):
            print(f"\nLogging out Dr. {current_user.username}...")
            manager.save_to_file("clinic_data.json", silent=True)
            return
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please select from 1 to 5.\n")


def run_patient_portal(manager: ClinicManager, patient_id: str):
    """Patient Portal - Read-only view scoped to the entered Patient ID."""
    patient = manager.patients[patient_id]

    while True:
        portal_title = f"PATIENT LOOKUP - {patient.name}"
        print("\n+" + "=" * 54 + "+")
        print("|" + portal_title.center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] My Appointments     : View scheduled visits     |")
        print("|  [2] My Queue Position   : Check current wait status |")
        print("|  [3] My Visit History    : Completed medical visits  |")
        print("|  [4] Back to Main Screen                              |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-4): ").strip().lower()

        if raw_choice in ("1", "appointments", "my appointments"):
            action_view_own_appointments(manager, patient_id)
        elif raw_choice in ("2", "queue", "my queue", "position"):
            action_view_own_queue_position(manager, patient_id)
        elif raw_choice in ("3", "history", "my history", "visits"):
            action_view_own_history(manager, patient_id)
        elif raw_choice in ("4", "back", "return", "exit"):
            print(f"\nGoodbye, {patient.name}!\n")
            return
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please choose from 1 to 4.\n")


def patient_lookup(manager: ClinicManager) -> None:
    """Passwordless patient lookup by assigned Patient ID."""
    print("\n+" + "=" * 54 + "+")
    print("|" + "PATIENT LOOKUP".center(54) + "|")
    print("+" + "-" * 54 + "+")

    while True:
        p_id = input("\n  Enter your Patient ID (e.g. patient-123) [or 'cancel']: ").strip()
        if p_id.lower() == "cancel":
            return

        if p_id not in manager.patients:
            print(f"\n[ERROR] Patient ID '{p_id}' not found. Please check your ID and try again.\n")
            continue

        run_patient_portal(manager, p_id)
        return


def login_screen(manager: ClinicManager) -> User | None:
    """Authentication screen for administrative and medical staff (Staff / Doctor)."""
    print("\n+" + "=" * 54 + "+")
    print("|" + "STAFF / DOCTOR LOGIN".center(54) + "|")
    print("+" + "-" * 54 + "+")

    while True:
        try:
            username = input("\n  Username [or 'cancel' to go back]: ").strip()
            if username.lower() == "cancel":
                return None
            if not username:
                print("\n[ERROR] Username cannot be empty. Please try again.")
                continue
            password = input("  Password: ").strip()
            user = authenticate(username, password)
            print(f"\n[SUCCESS] Welcome, {user.display_role()} ({user.username})!\n")
            return user
        except ClinicError as err:
            print(f"\n[ERROR] {err} Try again.")


def opening_screen(manager: ClinicManager) -> User | None:
    """Opening Screen: Staff/Doctor Login, Patient ID Lookup, or Exit."""
    while True:
        print("\n+" + "=" * 54 + "+")
        print("|" + "SMART CLINIC SYSTEM".center(54) + "|")
        print("|" + "Samsung Innovation Campus".center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] Staff / Doctor Login                             |")
        print("|  [2] Patient Lookup (Enter your Patient ID)           |")
        print("|  [3] Exit                                             |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-3): ").strip()

        if raw_choice in ("1", "login", "staff", "doctor"):
            user = login_screen(manager)
            if user is not None:
                return user
        elif raw_choice in ("2", "lookup", "patient"):
            patient_lookup(manager)
        elif raw_choice in ("3", "exit", "quit", "q"):
            print("\nExiting Smart Clinic Queue System. Goodbye!\n")
            raise SystemExit
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please select 1, 2, or 3.\n")


# =========================================================
# MAIN APPLICATION ENTRY POINT
# =========================================================

def main():
    """Application main entry point with auto-loading and graceful shutdown."""
    manager = ClinicManager(base_fee=100.0)

    # 1. Automatic database loading upon startup
    manager.load_from_file("clinic_data.json")

    # 2. Main interactive application loop
    try:
        while True:
            current_user = opening_screen(manager)
            if current_user is None:
                continue

            manager.set_current_user(current_user)

            if isinstance(current_user, StaffUser):
                run_staff_menu(manager, current_user)
            elif isinstance(current_user, DoctorUser):
                run_doctor_menu(manager, current_user)

            manager.set_current_user(None)
    except (KeyboardInterrupt, SystemExit):
        # Auto-save clinic database upon program interruption or exit
        print("\n\n[INFO] Program interrupted. Auto-saving clinic database before exit...")
        manager.save_to_file("clinic_data.json", silent=True)
        print("[SUCCESS] All clinic records saved safely. Goodbye!\n")




def cli_main():
    """Main CLI execution loop."""
    manager = ClinicManager()

    # 1. Automatic database loading upon startup
    manager.load_from_file()

    # 2. Main interactive application loop
    try:
        while True:
            current_user = opening_screen(manager)
            if current_user is None:
                continue

            manager.set_current_user(current_user)

            if isinstance(current_user, StaffUser):
                run_staff_menu(manager, current_user)
            elif isinstance(current_user, DoctorUser):
                run_doctor_menu(manager, current_user)

            manager.set_current_user(None)
    except (KeyboardInterrupt, SystemExit):
        print("\n\n[INFO] Program interrupted. Auto-saving clinic database before exit...")
        manager.save_to_file(silent=True)
        print("[SUCCESS] All clinic records saved safely. Goodbye!\n")
