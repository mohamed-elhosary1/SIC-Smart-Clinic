"""ClinicManager singleton controller and domain orchestrator."""

import json
import os
import random
import shutil
from datetime import datetime, date, timedelta
from functools import reduce
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .exceptions import (
    ClinicError,
    DuplicateBookingError,
    InvalidAppointmentTimeError,
    PatientNotFoundError,
    DoctorNotFoundError,
    InvalidFormatError,
)
from .auth import User, StaffUser, DoctorUser
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
from .validators import validate_patient_id, validate_doctor_id, validate_phone, parse_status
from .triage import make_triage_calculator, find_visits_recursive
from .persistence import get_data_path, get_report_path
from .cloud_sync import get_cloud_sync_client, CloudSyncClient


class ClinicManager:
    """Central manager handling business logic, appointments, queues, caching, and persistence."""

    def __init__(self, base_fee: float = 100.0, cloud_sync: Optional[CloudSyncClient] = None):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []
        # Instance attribute mapping doctor IDs to booked start times
        self.booked_date: dict[str, list[datetime]] = {}
        self.fee_calculator = make_triage_calculator(base_fee=base_fee)
        self.cloud_sync: CloudSyncClient = cloud_sync or get_cloud_sync_client()
        self.current_user: User | None = None
        self._visit_lookup_cache: dict[str, list] = {}

    def set_current_user(self, user: User | None):
        """Set the active user for permission checks on administrative actions."""
        self.current_user = user

    # ---------- ID Generation ----------

    def generate_unique_patient_id(self) -> str:
        """Generate an unused random patient ID between 1 and 1000."""
        while True:
            num = random.randint(1, 1000)
            p_id = f"patient-{num}"
            if p_id not in self.patients:
                return p_id

    def generate_unique_doctor_id(self) -> str:
        """Generate an unused random doctor ID between 1 and 1000."""
        while True:
            num = random.randint(1, 1000)
            d_id = f"doctor-{num}"
            if d_id not in self.doctors:
                return d_id

    # ---------- Registration ----------

    def register_patient(self, patient: Patient):
        """Register a new patient record with permission validation."""
        if self.current_user is not None and not self.current_user.has_permission("register_patient"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient.person_id in self.patients:
            raise DuplicateBookingError(f"Patient with ID '{patient.person_id}' already exists")
        self.patients[patient.person_id] = patient
        return patient

    def add_doctor(self, doctor: Doctor):
        """Add a medical doctor with permission validation."""
        if self.current_user is not None and not self.current_user.has_permission("add_doctor"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if doctor.person_id in self.doctors:
            raise DuplicateBookingError(f"Doctor with ID '{doctor.person_id}' already exists")
        self.doctors[doctor.person_id] = doctor
        if doctor.person_id not in self.booked_date:
            self.booked_date[doctor.person_id] = []
        return doctor

    def toggle_doctor_availability(self, doctor_id: str) -> bool:
        """Toggle a doctor's active availability status."""
        if self.current_user is not None and not self.current_user.has_permission("toggle_doctor_availability"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor ID '{doctor_id}' not found")
        doc = self.doctors[doctor_id]
        doc.toggle_availability()
        return doc.availability

    # ---------- Appointments & 30-Minute Slot Scheduling ----------

    def book_appointment(self, patient_id: str, doctor_id: str, time):
        """
        Book a new appointment slot.
        Enforces a default 30-minute busy duration window. No overlapping appointments
        are permitted for the same doctor or same patient during this 30-minute interval.
        """
        if self.current_user is not None and not self.current_user.has_permission("book_appointment"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient ID '{patient_id}' not found")
        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor ID '{doctor_id}' not found")

        # Parse string time formats into datetime
        if isinstance(time, str):
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y/%m/%d %H:%M"):
                try:
                    time = datetime.strptime(time.strip(), fmt)
                    break
                except ValueError:
                    continue
            else:
                raise InvalidAppointmentTimeError(f"Invalid date format '{time}'. Use 'YYYY-MM-DD HH:MM'")

        if not isinstance(time, datetime) or time <= datetime.now():
            raise InvalidAppointmentTimeError("Appointment time must be a valid future datetime")

        target_doctor = self.doctors[doctor_id]
        if not target_doctor.availability:
            raise ClinicError(f"Dr. {target_doctor.name} is currently marked as unavailable")

        # 1. 30-Minute Doctor Slot Conflict Check
        for existing in self.appointments:
            if existing.doctor.person_id == doctor_id and existing.status != "cancelled":
                if existing.overlaps_with(time, DEFAULT_APPOINTMENT_DURATION):
                    raise DuplicateBookingError(
                        f"Doctor {doctor_id} is busy between {existing.time.strftime('%H:%M')} "
                        f"and {existing.end_time.strftime('%H:%M')} (30-minute appointment slot reserved)."
                    )

        # 2. 30-Minute Patient Schedule Conflict Check
        for existing in self.appointments:
            if existing.patient.person_id == patient_id and existing.status != "cancelled":
                if existing.overlaps_with(time, DEFAULT_APPOINTMENT_DURATION):
                    raise DuplicateBookingError(
                        f"Patient {patient_id} already has an active appointment between "
                        f"{existing.time.strftime('%H:%M')} and {existing.end_time.strftime('%H:%M')} (30-minute slot)."
                    )

        target_patient = self.patients[patient_id]
        new_appt = Appointment(
            patient=target_patient,
            doctor=target_doctor,
            time=time,
            status="pending",
            duration=DEFAULT_APPOINTMENT_DURATION,
        )
        new_appt.fee = self.fee_calculator(target_patient)

        # Record slot in booked_date and append appointment
        if doctor_id not in self.booked_date:
            self.booked_date[doctor_id] = []
        self.booked_date[doctor_id].append(time)

        self.appointments.append(new_appt)
        target_patient.add_visit(new_appt)

        # Invalidate cache for patient
        self._visit_lookup_cache.pop(patient_id, None)

        return new_appt

    def update_visit_status(self, appointment_index: int, new_status: str):
        """Update appointment status with 30-minute reactivation collision checks."""
        if self.current_user is not None and not self.current_user.has_permission("update_visit_status"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if appointment_index < 0 or appointment_index >= len(self.appointments):
            raise IndexError(f"Invalid appointment index {appointment_index}")

        norm_status = parse_status(new_status)
        if not norm_status:
            raise ValueError(f"Invalid visit status '{new_status}'. Allowed: pending, completed, cancelled, in_progress")

        appt = self.appointments[appointment_index]
        old_status = appt.status
        doc_id = appt.doctor.person_id
        pat_id = appt.patient.person_id

        # If reactivating a cancelled appointment, guard against 30-minute slot collisions
        if old_status == "cancelled" and norm_status != "cancelled":
            for existing in self.appointments:
                if existing is not appt and existing.status != "cancelled":
                    if existing.doctor.person_id == doc_id and existing.overlaps_with(appt.time, appt.duration):
                        raise DuplicateBookingError(
                            f"Cannot reactivate appointment: Dr. {appt.doctor.name} already has an active appointment "
                            f"between {existing.time.strftime('%H:%M')} and {existing.end_time.strftime('%H:%M')}."
                        )
                    if existing.patient.person_id == pat_id and existing.overlaps_with(appt.time, appt.duration):
                        raise DuplicateBookingError(
                            f"Cannot reactivate appointment: Patient {appt.patient.name} already has an active appointment "
                            f"between {existing.time.strftime('%H:%M')} and {existing.end_time.strftime('%H:%M')}."
                        )

            if doc_id not in self.booked_date:
                self.booked_date[doc_id] = []
            if appt.time not in self.booked_date[doc_id]:
                self.booked_date[doc_id].append(appt.time)
        elif norm_status == "cancelled" and old_status != "cancelled":
            # Free doctor slot upon cancellation
            if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
                self.booked_date[doc_id].remove(appt.time)

        appt.update_status(norm_status)

        # Invalidate memoization cache for patient
        self._visit_lookup_cache.pop(appt.patient.person_id, None)

        return appt

    def delete_appointment(self, appointment_index: int) -> Appointment:
        """Delete an appointment, releasing time slots and updating triage counts."""
        if self.current_user is not None and not self.current_user.has_permission("delete_appointment"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if appointment_index < 0 or appointment_index >= len(self.appointments):
            raise IndexError(f"Invalid appointment index {appointment_index}")

        appt = self.appointments.pop(appointment_index)

        # Free doctor slot if appointment was active
        doc_id = appt.doctor.person_id
        if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
            self.booked_date[doc_id].remove(appt.time)

        # Remove from patient visit history
        if appt in appt.patient.visit_history:
            appt.patient.visit_history.remove(appt)

        # Decrement emergency counter if emergency case was removed
        if appt.patient.priority_level() == 1:
            if hasattr(self.fee_calculator, "decrement_emergency_count"):
                self.fee_calculator.decrement_emergency_count()

        # Invalidate memoization cache
        self._visit_lookup_cache.pop(appt.patient.person_id, None)

        return appt

    # ---------- Queue & Reports (Functional Tools) ----------

    def get_emergency_patients(self) -> list[Patient]:
        """Filter emergency patients using filter and lambda."""
        emergency = filter(lambda p: p.priority_level() == 1, self.patients.values())
        return list(emergency)

    def sort_queue_by_priority(self) -> list[Appointment]:
        """Sort waiting appointments by priority level (Emergency first) then time."""
        waiting = [appt for appt in self.appointments if appt.status == "pending"]
        waiting.sort(key=lambda appt: (appt.patient.priority_level(), appt.time))
        return waiting

    def get_waiting_queue_iterator(self) -> WaitingQueueIterator:
        """Return custom iterator over priority-ordered waiting queue."""
        waiting = self.sort_queue_by_priority()
        return WaitingQueueIterator(waiting)

    def calculate_total_revenue(self) -> float:
        """Calculate total revenue from completed visits using functools.reduce."""
        completed_fees = [appt.fee for appt in self.appointments if appt.status == "completed"]
        return float(reduce(lambda total, fee: total + fee, completed_fees, 0.0))

    # ---------- Shared DRY Report Helpers ----------

    def _compute_report_metrics(self) -> dict:
        """Aggregate report metrics into a unified dictionary (DRY)."""
        emergency_count = len(self.get_emergency_patients())
        closure_count = self.fee_calculator.get_emergency_count() if hasattr(self.fee_calculator, "get_emergency_count") else 0
        completed = len([a for a in self.appointments if a.status == "completed"])
        pending = len([a for a in self.appointments if a.status == "pending"])
        cancelled = len([a for a in self.appointments if a.status == "cancelled"])
        in_progress = len([a for a in self.appointments if a.status == "in_progress"])
        revenue = self.calculate_total_revenue()

        return {
            "total_patients": len(self.patients),
            "total_doctors": len(self.doctors),
            "emergency_patients": emergency_count,
            "emergency_fees_calculated": closure_count,
            "completed_visits": completed,
            "pending_visits": pending,
            "cancelled_visits": cancelled,
            "in_progress_visits": in_progress,
            "total_revenue": revenue,
        }

    def _format_report_table(self, report: dict, timestamp: str | None = None) -> str:
        """Format report table inside a standardized 56-character frame."""
        border = "+" + "=" * 54 + "+"
        mid_sep = "+" + "-" * 39 + "+" + "-" * 14 + "+"

        lines = []
        if timestamp:
            lines.append(f"Report Generated: {timestamp}")
        lines.append(border)
        lines.append("|" + "CLINIC DAILY REPORT".center(54) + "|")
        lines.append(border)
        lbl_h, val_h = "Metric Description", "Count / Sum"
        lines.append(f"| {lbl_h:<37} | {val_h:>12} |")
        lines.append(mid_sep)

        metrics = [
            ("Registered Patients", str(report["total_patients"])),
            ("Registered Doctors", str(report["total_doctors"])),
            ("Total Appointments", str(len(self.appointments))),
            ("  - Pending Visits", str(report["pending_visits"])),
            ("  - Completed Visits", str(report["completed_visits"])),
            ("  - Cancelled Visits", str(report["cancelled_visits"])),
            ("  - In Progress Visits", str(report["in_progress_visits"])),
            ("Emergency Cases Treated", str(report["emergency_patients"])),
            ("Emergency Fees (Closure)", str(report["emergency_fees_calculated"])),
        ]

        for m_label, m_val in metrics:
            lines.append(f"| {m_label:<37} | {m_val:>12} |")

        lines.append(mid_sep)
        rev_str = f"${report['total_revenue']:.2f}"
        rev_label = "Total Revenue Collected"
        lines.append(f"| {rev_label:<37} | {rev_str:>12} |")
        lines.append(border)

        return "\n".join(lines)

    def daily_report(self) -> dict:
        """Generate and display the clinic daily report."""
        if self.current_user is not None and not self.current_user.has_permission("daily_report"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        report = self._compute_report_metrics()
        table_output = self._format_report_table(report)
        print(f"\n{table_output}\n")
        return report

    def export_report_to_file(self, path: str | Path | None = None) -> bool:
        """Export the daily report to a text file with a timestamp."""
        if self.current_user is not None and not self.current_user.has_permission("export_report"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if path is None:
            path = get_report_path("daily_report.txt")
        else:
            path = Path(path)

        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report = self._compute_report_metrics()
            formatted_text = self._format_report_table(report, timestamp=now_str)

            with open(path, "w", encoding="utf-8") as f:
                f.write(formatted_text + "\n")

            print(f"\n[SUCCESS] Daily report successfully exported to '{path}'.\n")
            return True
        except Exception as e:
            print(f"\n[ERROR] Failed exporting daily report to '{path}': {e}\n")
            return False

    # ---------- Memoized Patient History ----------

    def get_patient_completed_visits(self, patient_id: str, return_status: bool = False):
        """Retrieve patient completed visits using recursion and memoization cache."""
        if self.current_user is not None and not self.current_user.has_permission("view_history"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient ID '{patient_id}' not found")

        if patient_id in self._visit_lookup_cache:
            completed_visits = self._visit_lookup_cache[patient_id]
            is_cache_hit = True
        else:
            patient = self.patients[patient_id]
            completed_visits = find_visits_recursive(patient.visit_history, 0)
            self._visit_lookup_cache[patient_id] = completed_visits
            is_cache_hit = False

        if return_status:
            return completed_visits, is_cache_hit
        return completed_visits

    # ---------- Persistence & Fault-Tolerant JSON Storage ----------

    def save_to_file(self, path: str | Path | None = None, silent: bool = False) -> bool:
        """Save entire clinic database to a JSON file with automatic directory creation."""
        try:
            if path is None:
                path = get_data_path("clinic_data.json")
            else:
                p = Path(path)
                if not p.is_absolute() and p.name == "clinic_data.json":
                    path = get_data_path("clinic_data.json")
                else:
                    path = p

            parent = os.path.dirname(str(path))
            if parent:
                os.makedirs(parent, exist_ok=True)

            data = {
                "patients": [
                    {
                        "type": "Emergency" if (isinstance(p, EmergencyPatient) or (p.priority_level() if callable(p.priority_level) else p.priority_level) == 1) else "Regular",
                        "person_id": p.person_id,
                        "name": p.name,
                        "phone": p.phone,
                        "age": p.age,
                        "case_type": p.case_type
                    }
                    for p in self.patients.values()
                ],
                "doctors": [
                    {
                        "person_id": d.person_id,
                        "name": d.name,
                        "phone": d.phone,
                        "specialty": d.specialty,
                        "availability": d.availability
                    }
                    for d in self.doctors.values()
                ],
                "appointments": [
                    {
                        "patient_id": a.patient.person_id,
                        "doctor_id": a.doctor.person_id,
                        "time": a.time.isoformat() if hasattr(a, "time") and isinstance(a.time, datetime) else getattr(a, "time_slot", "09:00-09:30"),
                        "status": a.status,
                        "fee": getattr(a, "fee", 100.0)
                    }
                    for a in self.appointments
                ]
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            if not silent:
                print(f"\n[SUCCESS] Clinic data saved successfully to '{path}'.\n")
            if getattr(self, "cloud_sync", None) and self.cloud_sync.enabled:
                self.cloud_sync.push_cloud_data(data)
            return True
        except Exception as e:
            print(f"\n[ERROR] Failed saving data to '{path}': {e}\n")
            return False

    def load_from_file(self, path: str | Path | None = None) -> bool:
        """Load clinic database from JSON with automatic initialization and corrupt-file backup."""
        if path is None:
            path = get_data_path("clinic_data.json")
        else:
            p = Path(path)
            if not p.exists() and not p.is_absolute():
                resolved = get_data_path(p.name)
                if resolved.exists():
                    path = resolved
                else:
                    path = p
            else:
                path = p

        # Automatic Cloud Data Recovery on startup / ephemeral deployments
        if getattr(self, "cloud_sync", None) and self.cloud_sync.enabled:
            recovered, msg = self.cloud_sync.recover_if_needed(path)
            if recovered:
                print(f"\n[CLOUD RECOVERY] {msg}\n")

        initial_data = {"patients": [], "doctors": [], "appointments": []}
        parent = os.path.dirname(str(path))
        if parent:
            os.makedirs(parent, exist_ok=True)

        # Scenario 1: File does not exist -> Create fresh file
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=4)
                print(f"\n[INFO] Database file '{path}' was not found. Created a fresh database file automatically.\n")
            except Exception as e:
                print(f"\n[WARNING] Could not create database file '{path}': {e}. Operating in memory.\n")
            return True

        # Scenario 2: File exists but may be empty or corrupted
        try:
            if os.path.getsize(path) == 0:
                raise ValueError(f"File '{path}' is empty (0 bytes)")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"Root JSON content in '{path}' must be an object/dict")
        except Exception as e:
            bak_path = f"{path}.bak"
            try:
                shutil.copyfile(path, bak_path)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=4)
                print(f"\n[WARNING] Database file '{path}' was corrupted ({e}).")
                print(f"[INFO] Backed up corrupt file to '{bak_path}' and created a fresh database file.\n")
            except Exception as bak_err:
                print(f"\n[ERROR] Failed recovering corrupt file '{path}': {bak_err}\n")
            data = initial_data

        self.patients.clear()
        self.doctors.clear()
        self.appointments.clear()
        self.booked_date.clear()
        self._visit_lookup_cache.clear()

        # 1. Reconstruct Patients
        for p_data in data.get("patients", []):
            try:
                p_type = p_data.get("type", "Regular")
                if p_type == "Emergency":
                    patient = EmergencyPatient(
                        person_id=p_data["person_id"],
                        name=p_data["name"],
                        phone=p_data["phone"],
                        age=p_data["age"],
                        case_type=p_data["case_type"]
                    )
                else:
                    patient = RegularPatient(
                        person_id=p_data["person_id"],
                        name=p_data["name"],
                        phone=p_data["phone"],
                        age=p_data["age"],
                        case_type=p_data["case_type"]
                    )
                self.patients[patient.person_id] = patient
            except Exception as e:
                print(f"[ERROR] Could not reconstruct patient {p_data}: {e}")

        # 2. Reconstruct Doctors
        for d_data in data.get("doctors", []):
            try:
                doctor = Doctor(
                    person_id=d_data["person_id"],
                    name=d_data["name"],
                    phone=d_data["phone"],
                    specialty=d_data["specialty"],
                    availability=d_data.get("availability", True)
                )
                self.doctors[doctor.person_id] = doctor
                self.booked_date[doctor.person_id] = []
            except Exception as e:
                print(f"[ERROR] Could not reconstruct doctor {d_data}: {e}")

        # 3. Reconstruct Appointments & Rebuild booked_date
        for a_data in data.get("appointments", []):
            p_id = a_data.get("patient_id")
            d_id = a_data.get("doctor_id")
            if p_id in self.patients and d_id in self.doctors:
                patient = self.patients[p_id]
                doctor = self.doctors[d_id]
                try:
                    time_raw = a_data["time"]
                    try:
                        time_obj = datetime.fromisoformat(time_raw)
                    except ValueError:
                        time_obj = datetime.strptime(time_raw, "%Y-%m-%d %H:%M")

                    status = a_data.get("status", "pending")
                    fee = float(a_data.get("fee", 0.0))

                    appt = Appointment(
                        patient=patient,
                        doctor=doctor,
                        time=time_obj,
                        status=status,
                        fee=fee,
                        duration=DEFAULT_APPOINTMENT_DURATION,
                    )
                    self.appointments.append(appt)
                    patient.add_visit(appt)

                    # Rebuild booked_date for active slots
                    if status != "cancelled":
                        if d_id not in self.booked_date:
                            self.booked_date[d_id] = []
                        if time_obj not in self.booked_date[d_id]:
                            self.booked_date[d_id].append(time_obj)
                except Exception as e:
                    print(f"[ERROR] Could not reconstruct appointment {a_data}: {e}")

        total_loaded = len(self.patients) + len(self.doctors) + len(self.appointments)
        if total_loaded > 0:
            print(f"\n[SUCCESS] Loaded data successfully from '{path}': {len(self.patients)} Patients, {len(self.doctors)} Doctors, {len(self.appointments)} Appointments.\n")

        # Synchronize closure counter with total existing emergency appointments
        loaded_emergency_count = sum(1 for a in self.appointments if a.patient.priority_level() == 1)
        self.fee_calculator = make_triage_calculator(base_fee=100.0, initial_emergency_count=loaded_emergency_count)
        return True

    def reset_database(self, path: str = "clinic_data.json") -> bool:
        """Reset clinic database completely and clear records with permission check."""
        if self.current_user is not None and not self.current_user.has_permission("reset_database"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        self.patients.clear()
        self.doctors.clear()
        self.appointments.clear()
        self.booked_date.clear()
        self._visit_lookup_cache.clear()
        if hasattr(self.fee_calculator, "reset_count"):
            self.fee_calculator.reset_count()
        return self.save_to_file(path, silent=True)

    # ---------- Cloud Sync & Recovery ----------

    def sync_cloud(self) -> dict:
        """Push current database snapshot to cloud storage and return diagnostics."""
        data = {
            "patients": [
                {
                    "type": "Emergency" if (isinstance(p, EmergencyPatient) or (p.priority_level() if callable(p.priority_level) else p.priority_level) == 1) else "Regular",
                    "person_id": p.person_id,
                    "name": p.name,
                    "phone": p.phone,
                    "age": p.age,
                    "case_type": p.case_type
                }
                for p in self.patients.values()
            ],
            "doctors": [
                {
                    "person_id": d.person_id,
                    "name": d.name,
                    "phone": d.phone,
                    "specialty": d.specialty,
                    "availability": d.availability
                }
                for d in self.doctors.values()
            ],
            "appointments": [
                {
                    "patient_id": a.patient.person_id,
                    "doctor_id": a.doctor.person_id,
                    "time": a.time.isoformat() if hasattr(a, "time") and isinstance(a.time, datetime) else getattr(a, "time_slot", "09:00-09:30"),
                    "status": a.status,
                    "fee": getattr(a, "fee", 100.0)
                }
                for a in self.appointments
            ]
        }
        success = self.cloud_sync.push_cloud_data(data)
        status = self.cloud_sync.get_status()
        status["success"] = success
        return status

    def recover_from_cloud(self, path: str | Path | None = None) -> bool:
        """Force recovery of latest database from cloud storage into local memory."""
        cloud_data = self.cloud_sync.fetch_cloud_data()
        if not cloud_data or not isinstance(cloud_data, dict):
            return False
        if path is None:
            path = get_data_path("clinic_data.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cloud_data, f, ensure_ascii=False, indent=4)
        return self.load_from_file(path)


