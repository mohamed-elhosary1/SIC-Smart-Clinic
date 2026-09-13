"""Interactive CLI Action Handlers for patient registration, booking, triage, and reports."""

import random
from datetime import datetime, timedelta
from typing import Optional

from smart_clinic.core import (
    ClinicManager,
    Patient,
    EmergencyPatient,
    RegularPatient,
    Doctor,
    Appointment,
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
)

def print_section_header(title: str, width: int = 54):
    """Print standard section header enclosed within a fixed-width ASCII frame."""
    print("\n+" + "-" * width + "+")
    print("|" + title.center(width) + "|")
    print("+" + "-" * width + "+")


def action_register_patient(manager: ClinicManager):
    """Register a new patient record through staff menu."""
    print_section_header("REGISTER PATIENT")
    if manager.current_user is not None and not manager.current_user.has_permission("register_patient"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return None

    while True:
        raw_type = input("  Patient Type   (1: Regular, 2: Emergency) [Default: 1]: ").strip()
        p_type = parse_patient_type(raw_type)
        if p_type:
            break
        print("\n[ERROR] Please enter '1' / 'Regular' or '2' / 'Emergency'. Try again.\n")

    p_id = manager.generate_unique_patient_id()

    while True:
        name = input("  Full Name      [or 'cancel' to exit]: ").strip()
        if name.lower() == "cancel":
            return None
        if name:
            break
        print("\n[ERROR] Patient name cannot be empty. Please try again.\n")

    while True:
        phone = input("  Phone Number   (11 digits, e.g. 01012345678) [or 'cancel']: ").strip()
        if phone.lower() == "cancel":
            return None
        if not validate_phone(phone):
            print(f"\n[ERROR] Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.\n")
            continue
        break

    while True:
        age_input = input("  Patient Age    [or 'cancel']: ").strip()
        if age_input.lower() == "cancel":
            return None
        try:
            age = int(age_input)
            if age <= 0 or age > 130:
                raise ValueError
            break
        except ValueError:
            print(f"\n[ERROR] Age must be a valid positive integer between 1 and 130. Got '{age_input}'. Please try again.\n")

    case_type = input("  Diagnosis/Case [or 'cancel']: ").strip()
    if case_type.lower() == "cancel":
        return None

    try:
        if p_type == "2":
            new_p = EmergencyPatient(p_id, name, phone, age, case_type)
        else:
            new_p = RegularPatient(p_id, name, phone, age, case_type)
        manager.register_patient(new_p)
        manager.save_to_file("clinic_data.json", silent=True)

        p_type_label = "Emergency (High Priority)" if p_type == "2" else "Regular"
        print(f"\n[SUCCESS] Patient registered successfully!")
        print(f"  Profile: {new_p.display_profile()}")
        print("+" + "-" * 54 + "+")
        print("|" + "REGISTRATION DETAILS".center(54) + "|")
        print("+" + "-" * 54 + "+")
        id_badge = f">>> YOUR ASSIGNED PATIENT ID: {p_id} <<<"
        print("|" + id_badge.center(54) + "|")
        print("+" + "-" * 54 + "+")
        print(f"|  Patient Name  : {new_p.name:<35} |")
        print(f"|  Patient Type  : {p_type_label:<35} |")
        print(f"|  Phone Number  : {new_p.phone:<35} |")
        print(f"|  Age           : {str(new_p.age):<35} |")
        print(f"|  Diagnosis     : {(new_p.case_type or 'General Checkup'):<35} |")
        print("+" + "-" * 54 + "+\n")
        return new_p
    except ClinicError as err:
        print(f"\n[ERROR] Registration failed: {err}\n")
        return None


def action_add_doctor(manager: ClinicManager):
    """Add a new medical doctor to the clinic."""
    print_section_header("ADD DOCTOR")
    if manager.current_user is not None and not manager.current_user.has_permission("add_doctor"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    while True:
        d_id = input("  Doctor ID      (Press Enter for auto-id, or doctor-<num>) [or 'cancel']: ").strip()
        if d_id.lower() == "cancel":
            return
        if not d_id:
            d_id = manager.generate_unique_doctor_id()
            print(f"\n[INFO] Generated Doctor ID: {d_id}\n")
            break
        if not validate_doctor_id(d_id):
            print(f"\n[ERROR] Invalid doctor ID format: '{d_id}'. Expected 'doctor-<number>'. Please try again.\n")
            continue
        if d_id in manager.doctors:
            print(f"\n[ERROR] Doctor with ID '{d_id}' already exists. Please enter a different ID.\n")
            continue
        break

    while True:
        name = input("  Doctor Name    [or 'cancel']: ").strip()
        if name.lower() == "cancel":
            return
        if name:
            break
        print("\n[ERROR] Doctor name cannot be empty. Please try again.\n")

    while True:
        phone = input("  Phone Number   (11 digits, e.g. 01112345678) [or 'cancel']: ").strip()
        if phone.lower() == "cancel":
            return
        if not validate_phone(phone):
            print(f"\n[ERROR] Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.\n")
            continue
        break

    specialty = input("  Specialty      [or 'cancel']: ").strip()
    if specialty.lower() == "cancel":
        return

    try:
        new_doc = Doctor(d_id, name, phone, specialty)
        manager.add_doctor(new_doc)
        manager.save_to_file("clinic_data.json", silent=True)
        print(f"\n[SUCCESS] Doctor added successfully!")
        print(f"  Profile: {new_doc.display_profile()}\n")
    except ClinicError as err:
        print(f"\n[ERROR] Failed adding doctor: {err}\n")


def action_book_appointment(manager: ClinicManager):
    """Book a new appointment with default 30-minute busy slot allocation."""
    print_section_header("BOOK APPOINTMENT (30-MIN TIME SLOTS)")
    if manager.current_user is not None and not manager.current_user.has_permission("book_appointment"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.patients:
        print("\n[INFO] No patients registered yet. Please register a patient first.\n")
        return
    if not manager.doctors:
        print("\n[INFO] No doctors registered yet. Please add a doctor first.\n")
        return

    # 1. Patient Selection
    print("\nAvailable Patients:")
    p_keys = list(manager.patients.keys())
    for idx, p_key in enumerate(p_keys, 1):
        p = manager.patients[p_key]
        print(f"  [{idx}] {p.person_id}: {p.name} ({p.display_profile()})")

    while True:
        p_input = input("\n  Select Patient (Number or ID) [or 'cancel']: ").strip()
        if p_input.lower() == "cancel":
            return
        if p_input.isdigit() and 1 <= int(p_input) <= len(p_keys):
            p_id = p_keys[int(p_input) - 1]
            break
        elif p_input in manager.patients:
            p_id = p_input
            break
        print("\n[ERROR] Invalid patient selection. Please try again.")

    # 2. Doctor Selection
    print("\nAvailable Doctors:")
    d_keys = list(manager.doctors.keys())
    for idx, d_key in enumerate(d_keys, 1):
        d = manager.doctors[d_key]
        status = "Available" if d.availability else "Unavailable"
        print(f"  [{idx}] {d.person_id}: Dr. {d.name} ({d.specialty}) - [{status}]")

    while True:
        d_input = input("\n  Select Doctor (Number or ID) [or 'cancel']: ").strip()
        if d_input.lower() == "cancel":
            return
        if d_input.isdigit() and 1 <= int(d_input) <= len(d_keys):
            d_id = d_keys[int(d_input) - 1]
            break
        elif d_input in manager.doctors:
            d_id = d_input
            break
        print("\n[ERROR] Invalid doctor selection. Please try again.")

    # 3. Time Selection (Enforces 30-Minute Slot Reservation)
    print("\n  NOTE: Each appointment reserves a 30-minute slot (e.g. 10:00 - 10:30).")
    while True:
        time_str = input("  Appointment Date & Time (YYYY-MM-DD HH:MM) [or 'cancel']: ").strip()
        if time_str.lower() == "cancel":
            return
        try:
            appt = manager.book_appointment(p_id, d_id, time_str)
            manager.save_to_file("clinic_data.json", silent=True)
            print(f"\n[SUCCESS] Appointment booked successfully!")
            print(f"  Reserved Slot: {appt.time.strftime('%Y-%m-%d %H:%M')} - {appt.end_time.strftime('%H:%M')} (30 mins)")
            print(f"  Patient      : {appt.patient.name} ({appt.patient.person_id})")
            print(f"  Doctor       : Dr. {appt.doctor.name} ({appt.doctor.specialty})")
            print(f"  Fee          : ${appt.fee:.2f}\n")
            return
        except ClinicError as err:
            print(f"\n[ERROR] Booking failed: {err}\n")


def action_update_visit_status(manager: ClinicManager):
    """Update appointment visit status with 30-minute reactivation safety."""
    print_section_header("UPDATE VISIT STATUS")
    if manager.current_user is not None and not manager.current_user.has_permission("update_visit_status"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.appointments:
        print("\n[INFO] No appointments found in the system.\n")
        return

    print("\nCurrent Appointments:")
    for idx, a in enumerate(manager.appointments, 1):
        t_str = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        t_end = a.end_time.strftime("%H:%M") if isinstance(a.time, datetime) else ""
        slot_s = f"{t_str} - {t_end}" if t_end else t_str
        print(f"  [{idx}] Patient: {a.patient.name:<16} | Dr. {a.doctor.name:<14} | Slot: {slot_s} | Status: {a.status.upper()}")

    while True:
        idx_input = input("\n  Select Appointment Number to update [or 'cancel']: ").strip()
        if idx_input.lower() == "cancel":
            return
        if idx_input.isdigit() and 1 <= int(idx_input) <= len(manager.appointments):
            target_idx = int(idx_input) - 1
            break
        print(f"\n[ERROR] Please enter a valid number between 1 and {len(manager.appointments)}.")

    print("\nAvailable Status Options:")
    print("  [1] Pending")
    print("  [2] In Progress")
    print("  [3] Completed")
    print("  [4] Cancelled")

    while True:
        st_input = input("\n  Enter new status (1-4 or name) [or 'cancel']: ").strip()
        if st_input.lower() == "cancel":
            return
        norm_st = parse_status(st_input)
        if norm_st:
            break
        print("\n[ERROR] Invalid status. Choose 1 (Pending), 2 (In Progress), 3 (Completed), or 4 (Cancelled).")

    try:
        updated_appt = manager.update_visit_status(target_idx, norm_st)
        manager.save_to_file("clinic_data.json", silent=True)
        print(f"\n[SUCCESS] Appointment #{target_idx + 1} status updated to: {updated_appt.status.upper()}\n")
    except ClinicError as err:
        print(f"\n[ERROR] Update failed: {err}\n")


def action_show_queue(manager: ClinicManager):
    """Display prioritized waiting queue using custom iterator."""
    full_w = 76
    print_section_header("WAITING QUEUE (Emergency First, by Priority & Time)", width=full_w)
    if manager.current_user is not None and not manager.current_user.has_permission("view_queue"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    queue_iter = manager.get_waiting_queue_iterator()
    count = 0

    border = "+" + "-" * full_w + "+"
    print("\n" + border)
    h_pos, h_pat, h_doc, h_slot, h_prio = "#", "Patient", "Doctor", "30-Min Time Slot", "Priority"
    print(f"| {h_pos:<3} | {h_pat:<18} | {h_doc:<18} | {h_slot:<17} | {h_prio:<8} |")
    print(border)

    for appt in queue_iter:
        count += 1
        p_name = appt.patient.name[:18]
        d_name = f"Dr. {appt.doctor.name}"[:18]
        t_start = appt.time.strftime("%H:%M") if isinstance(appt.time, datetime) else str(appt.time)
        t_end = appt.end_time.strftime("%H:%M") if isinstance(appt.time, datetime) else ""
        slot_str = f"{t_start}-{t_end}"
        prio_label = "EMG (1)" if appt.patient.priority_level() == 1 else "REG (2)"
        print(f"| {count:<3} | {p_name:<18} | {d_name:<18} | {slot_str:<17} | {prio_label:<8} |")

    print(border)
    if count == 0:
        print(f"| {'No patients currently waiting in queue.'.center(full_w)} |")
        print(border)
    print(f"\nTotal patients waiting in queue: {count}\n")


def action_toggle_doctor_availability(manager: ClinicManager):
    """Toggle a doctor's active availability status."""
    print_section_header("TOGGLE DOCTOR AVAILABILITY")
    if manager.current_user is not None and not manager.current_user.has_permission("toggle_doctor_availability"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.doctors:
        print("\n[INFO] No doctors registered in the clinic.\n")
        return

    d_keys = list(manager.doctors.keys())
    print("\nRegistered Doctors:")
    for idx, d_id in enumerate(d_keys, 1):
        d = manager.doctors[d_id]
        st = "Available" if d.availability else "Unavailable"
        print(f"  [{idx}] {d.person_id}: Dr. {d.name} ({d.specialty}) - [{st}]")

    while True:
        choice = input("\n  Select Doctor (Number or ID) [or 'cancel']: ").strip()
        if choice.lower() == "cancel":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(d_keys):
            target_id = d_keys[int(choice) - 1]
            break
        elif choice in manager.doctors:
            target_id = choice
            break
        print("\n[ERROR] Invalid doctor selection. Please try again.")

    try:
        new_avail = manager.toggle_doctor_availability(target_id)
        manager.save_to_file("clinic_data.json", silent=True)
        doc = manager.doctors[target_id]
        st_text = "AVAILABLE" if new_avail else "UNAVAILABLE (BUSY)"
        print(f"\n[SUCCESS] Dr. {doc.name} status toggled to: {st_text}\n")
    except ClinicError as err:
        print(f"\n[ERROR] Failed toggling doctor status: {err}\n")


def action_delete_appointment(manager: ClinicManager):
    """Delete an appointment and release its 30-minute busy slot."""
    print_section_header("DELETE APPOINTMENT")
    if manager.current_user is not None and not manager.current_user.has_permission("delete_appointment"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.appointments:
        print("\n[INFO] No appointments available to delete.\n")
        return

    print("\nCurrent Appointments:")
    for idx, a in enumerate(manager.appointments, 1):
        t_str = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        t_end = a.end_time.strftime("%H:%M") if isinstance(a.time, datetime) else ""
        slot_s = f"{t_str} - {t_end}" if t_end else t_str
        print(f"  [{idx}] Patient: {a.patient.name:<15} | Dr. {a.doctor.name:<14} | Slot: {slot_s} | Status: {a.status.upper()}")

    while True:
        idx_input = input("\n  Enter appointment number to DELETE [or 'cancel']: ").strip()
        if idx_input.lower() == "cancel":
            return
        if idx_input.isdigit() and 1 <= int(idx_input) <= len(manager.appointments):
            target_idx = int(idx_input) - 1
            break
        print(f"\n[ERROR] Please enter a valid number between 1 and {len(manager.appointments)}.")

    confirm = input(f"  Are you sure you want to permanently delete appointment #{target_idx + 1}? (yes/no): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n[INFO] Deletion cancelled.\n")
        return

    try:
        deleted = manager.delete_appointment(target_idx)
        manager.save_to_file("clinic_data.json", silent=True)
        print(f"\n[SUCCESS] Appointment #{target_idx + 1} deleted successfully!")
        print(f"  Released Slot: {deleted.time.strftime('%Y-%m-%d %H:%M')} - {deleted.end_time.strftime('%H:%M')}")
        print(f"  Patient: {deleted.patient.name} | Doctor: Dr. {deleted.doctor.name}\n")
    except ClinicError as err:
        print(f"\n[ERROR] Deletion failed: {err}\n")


def action_daily_report(manager: ClinicManager):
    """Generate and display the daily clinic report."""
    print_section_header("DAILY REPORT")
    try:
        manager.daily_report()
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


def action_save_data(manager: ClinicManager):
    """Manually trigger saving database to JSON file."""
    print_section_header("SAVE CLINIC DATA")
    manager.save_to_file("clinic_data.json")


def action_reset_data(manager: ClinicManager):
    """Reset clinic database to a clean initial state."""
    print_section_header("RESET CLINIC DATA")
    if manager.current_user is not None and not manager.current_user.has_permission("reset_database"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    print("  WARNING: This operation will permanently wipe all registered patients,")
    print("  doctors, appointments, and schedules from memory and JSON storage.")
    confirm = input("\n  Type 'RESET' in capital letters to confirm database wipe: ").strip()
    if confirm != "RESET":
        print("\n[INFO] Reset aborted. No data was modified.\n")
        return

    try:
        manager.reset_database("clinic_data.json")
        print("\n[SUCCESS] Clinic database reset successfully. All records cleared.\n")
    except ClinicError as err:
        print(f"\n[ERROR] Reset failed: {err}\n")


def action_export_report(manager: ClinicManager):
    """Export the daily clinic report to daily_report.txt."""
    print_section_header("EXPORT DAILY REPORT")
    if manager.current_user is not None and not manager.current_user.has_permission("export_report"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    filename = input("  Enter output text filename [Default: daily_report.txt]: ").strip()
    if not filename:
        filename = "daily_report.txt"
    try:
        manager.export_report_to_file(filename)
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


def action_patient_history(manager: ClinicManager):
    """View completed visit history for a patient with memoization status."""
    print_section_header("PATIENT MEDICAL HISTORY")
    if manager.current_user is not None and not manager.current_user.has_permission("view_history"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.patients:
        print("\n[INFO] No patients registered yet.\n")
        return

    p_id = input("  Enter Patient ID (e.g. patient-123) [or 'cancel']: ").strip()
    if p_id.lower() == "cancel":
        return

    try:
        completed_visits, is_hit = manager.get_patient_completed_visits(p_id, return_status=True)
        patient = manager.patients[p_id]
        status_tag = "[CACHE HIT]" if is_hit else "[COMPUTED]"

        print(f"\n{status_tag} Completed visits for Patient {patient.name} ({patient.person_id}):")
        print("  " + "-" * 65)
        if not completed_visits:
            print("  No completed visits found for this patient.")
        else:
            for v_idx, v in enumerate(completed_visits, 1):
                v_time = v.time.strftime("%Y-%m-%d %H:%M") if isinstance(v.time, datetime) else str(v.time)
                v_end = v.end_time.strftime("%H:%M") if isinstance(v.time, datetime) else ""
                slot_s = f"{v_time} - {v_end}" if v_end else v_time
                print(f"  {v_idx}. Dr. {v.doctor.name:<16} ({v.doctor.specialty:<12}) | Slot: {slot_s} | Fee: ${v.fee:.2f}")
        print("  " + "-" * 65)
        print(f"  Total completed visits: {len(completed_visits)}\n")
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


# ---------- Scoped Patient Portal Actions ----------

def action_view_own_appointments(manager: ClinicManager, patient_id: str):
    """View all scheduled appointments for the logged-in patient."""
    print_section_header("MY APPOINTMENTS")
    patient_appts = [a for a in manager.appointments if a.patient.person_id == patient_id]

    if not patient_appts:
        print("\n[INFO] You do not have any scheduled appointments currently.\n")
        return

    print(f"\nAppointments for Patient ID: {patient_id}")
    print("  " + "-" * 75)
    for idx, a in enumerate(patient_appts, 1):
        time_s = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        end_s = a.end_time.strftime("%H:%M") if isinstance(a.time, datetime) else ""
        slot_s = f"{time_s} - {end_s}" if end_s else time_s
        print(f"  {idx}. Dr. {a.doctor.name:<15} ({a.doctor.specialty:<12}) | Slot: {slot_s} | Status: {a.status.upper()} | Fee: ${a.fee:.2f}")
    print("  " + "-" * 75)
    print(f"  Total appointments found: {len(patient_appts)}\n")


def action_view_own_queue_position(manager: ClinicManager, patient_id: str):
    """Display exact queue position and priority status for the patient."""
    print_section_header("MY QUEUE POSITION")
    waiting_queue = manager.sort_queue_by_priority()

    position = None
    patient_appt = None
    for idx, appt in enumerate(waiting_queue, 1):
        if appt.patient.person_id == patient_id:
            position = idx
            patient_appt = appt
            break

    if position is None:
        print(f"\n[INFO] Patient [{patient_id}] has no pending appointments in the waiting queue.\n")
        return

    time_s = patient_appt.time.strftime("%Y-%m-%d %H:%M") if isinstance(patient_appt.time, datetime) else str(patient_appt.time)
    end_s = patient_appt.end_time.strftime("%H:%M") if isinstance(patient_appt.time, datetime) else ""
    slot_s = f"{time_s} - {end_s} (30 mins)" if end_s else time_s
    p_level = "Emergency (High Priority)" if patient_appt.patient.priority_level() == 1 else "Regular Priority"

    print("\n+" + "=" * 54 + "+")
    print("|" + "YOUR QUEUE STATUS".center(54) + "|")
    print("+" + "=" * 54 + "+")
    pos_badge = f">>> CURRENT QUEUE POSITION: #{position} <<<"
    print("|" + pos_badge.center(54) + "|")
    print("+" + "-" * 54 + "+")
    print(f"|  Doctor        : Dr. {patient_appt.doctor.name:<33} |")
    print(f"|  Time Slot     : {slot_s:<35} |")
    print(f"|  Priority      : {p_level:<35} |")
    print(f"|  Total Waiting : {str(len(waiting_queue)):<35} |")
    print("+" + "=" * 54 + "+\n")


def action_view_own_history(manager: ClinicManager, patient_id: str):
    """Display completed medical visits for the patient."""
    print_section_header("MY VISIT HISTORY (Completed Visits)")
    try:
        completed_visits, is_hit = manager.get_patient_completed_visits(patient_id, return_status=True)
        patient = manager.patients.get(patient_id)
        p_name = patient.name if patient else patient_id
        status_tag = "[CACHE HIT]" if is_hit else "[COMPUTED]"

        print(f"\n{status_tag} Medical history for {p_name} ({patient_id}):")
        print("  " + "-" * 65)
        if not completed_visits:
            print("  No completed visits found in your medical history.")
        else:
            for v_idx, v in enumerate(completed_visits, 1):
                v_time = v.time.strftime("%Y-%m-%d %H:%M") if isinstance(v.time, datetime) else str(v.time)
                v_end = v.end_time.strftime("%H:%M") if isinstance(v.time, datetime) else ""
                slot_s = f"{v_time} - {v_end}" if v_end else v_time
                print(f"  {v_idx}. Dr. {v.doctor.name:<16} ({v.doctor.specialty:<12}) | Slot: {slot_s} | Fee: ${v.fee:.2f}")
        print("  " + "-" * 65)
        print(f"  Total completed visits: {len(completed_visits)}\n")
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


def action_cloud_sync(manager: ClinicManager):
    """Trigger manual cloud sync & recovery diagnostics."""
    print_section_header("CLOUD DATA RECOVERY & SYNCHRONIZATION")
    status = manager.cloud_sync.get_status()
    print(f"Provider:    {status['provider']}")
    print(f"Status:      {status['status'].upper()}")
    print(f"Last Synced: {status['last_synced']}")
    print("-" * 54)
    print("Options:")
    print("  [1] Push Database to Cloud Now")
    print("  [2] Recover / Pull Database from Cloud")
    print("  [3] Back to Menu")
    opt = input("\nEnter choice (1-3): ").strip()
    if opt == "1":
        res = manager.sync_cloud()
        if res.get("success"):
            print("\n[SUCCESS] Clinic database successfully pushed to Cloud storage!\n")
        else:
            print("\n[WARNING] Could not push to cloud. Running in local fallback mode.\n")
    elif opt == "2":
        confirm = input("This will overwrite local database with cloud copy. Proceed? (y/n): ").strip().lower()
        if confirm in ("y", "yes"):
            recovered = manager.recover_from_cloud()
            if recovered:
                print("\n[SUCCESS] Local database successfully recovered from Cloud!\n")
            else:
                print("\n[INFO] Cloud has no data or recovery was skipped.\n")
