# =========================================================
# LIBRARIES & DEPENDENCIES
# =========================================================
import json
import os
import random
import re
import shutil
from datetime import datetime, timedelta
from functools import reduce


# =========================================================
# STANDARD SYSTEM CONSTANTS
# =========================================================

# Default duration for any clinic appointment slot (30 minutes)
DEFAULT_APPOINTMENT_DURATION = timedelta(minutes=30)


# =========================================================
# CUSTOM EXCEPTIONS HIERARCHY
# =========================================================

class ClinicError(Exception):
    """Base exception for all clinic system errors."""
    pass


class InvalidAppointmentTimeError(ClinicError):
    """Raised when an appointment time format is invalid or scheduled in the past."""
    pass


class DuplicateBookingError(ClinicError):
    """Raised on double-booking, overlapping appointment slots, or duplicate IDs."""
    pass


class PatientNotFoundError(ClinicError):
    """Raised when a specified patient is not registered in the system."""
    pass


class DoctorNotFoundError(ClinicError):
    """Raised when a specified doctor is not registered in the system."""
    pass


class InvalidFormatError(ClinicError):
    """Raised when ID or phone number validation fails against regex constraints."""
    pass


# =========================================================
# AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC)
# =========================================================

class User:
    """Base class for authenticated system users (Staff / Doctor)."""

    def __init__(self, username: str, password: str, allowed_actions: set):
        self.username = username
        self.password = password  # Stored plainly for simulation purposes
        self.allowed_actions = allowed_actions

    def has_permission(self, action: str) -> bool:
        """Check whether user has permission for a specific action."""
        return action in self.allowed_actions

    def display_role(self) -> str:
        """Return the display role name."""
        return "Generic User"


class StaffUser(User):
    """Clinic staff member with full operational and administrative privileges."""

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=set())

    def has_permission(self, action: str) -> bool:
        # Staff members have full, unrestricted permissions across all actions
        return True

    def display_role(self) -> str:
        return "Staff"


class DoctorUser(User):
    """Medical doctor with scoped clinical permissions."""

    DOCTOR_ACTIONS = {
        "view_queue",
        "update_visit_status",
        "daily_report",
        "view_history",
    }

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=self.DOCTOR_ACTIONS)

    def display_role(self) -> str:
        return "Doctor"


# Default credentials database for staff and doctors
USERS_DB: dict[str, dict] = {
    "staff": {
        "password": "staff123",
        "factory": lambda u, p: StaffUser(u, p),
    },
    "doctor": {
        "password": "doc123",
        "factory": lambda u, p: DoctorUser(u, p),
    },
}


def authenticate(username: str, password: str) -> User:
    """Authenticate administrative and medical staff against USERS_DB."""
    u_key = username.strip().lower()
    p_clean = password.strip()
    user_record = USERS_DB.get(u_key)
    if not user_record or user_record["password"] != p_clean:
        raise ClinicError("Invalid credentials. Please check username and password.")
    return user_record["factory"](username.strip(), p_clean)


# =========================================================
# REGEX VALIDATORS
# =========================================================

PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")   # Format: patient-<number>
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")    # Format: doctor-<number>
PHONE_PATTERN = re.compile(r"01[0-9]{9}")        # 11-digit Egyptian mobile starting with 01


def validate_patient_id(patient_id: str) -> bool:
    """Validate patient ID format (patient-<number>)."""
    return bool(PATIENT_ID_PATTERN.fullmatch(patient_id.strip()))


def validate_doctor_id(doctor_id: str) -> bool:
    """Validate doctor ID format (doctor-<number>)."""
    return bool(DOCTOR_ID_PATTERN.fullmatch(doctor_id.strip()))


def validate_phone(phone: str) -> bool:
    """Validate Egyptian phone number format (01xxxxxxxxx)."""
    return bool(PHONE_PATTERN.fullmatch(phone.strip()))


# =========================================================
# INPUT NORMALIZATION HELPERS
# =========================================================

def parse_patient_type(val: str) -> str:
    """Normalize patient type input (1: Regular, 2: Emergency)."""
    val = val.strip().lower()
    if val in ("1", "regular", "reg"):
        return "1"
    elif val in ("2", "emergency", "emg"):
        return "2"
    return ""


def parse_status(val: str) -> str:
    """Normalize visit status input to standard status strings."""
    val = val.strip().lower()
    status_map = {
        "1": "pending", "pending": "pending",
        "2": "in_progress", "in_progress": "in_progress", "in progress": "in_progress",
        "3": "completed", "completed": "completed", "done": "completed",
        "4": "cancelled", "cancelled": "cancelled", "canceled": "cancelled"
    }
    return status_map.get(val, "")


def parse_menu_choice(val: str) -> str:
    """Normalize menu choice input from numbers or textual keywords."""
    val = val.strip().lower()
    choice_map = {
        "1": "1", "register": "1", "patient": "1", "register patient": "1",
        "2": "2", "doctor": "2", "add doctor": "2",
        "3": "3", "book": "3", "appointment": "3", "book appointment": "3",
        "4": "4", "update": "4", "status": "4", "update status": "4",
        "5": "5", "queue": "5", "show queue": "5",
        "6": "6", "toggle": "6", "availability": "6", "toggle availability": "6",
        "7": "7", "delete": "7", "remove": "7", "delete appointment": "7",
        "8": "8", "report": "8", "daily report": "8",
        "9": "9", "save": "9", "save data": "9",
        "10": "10", "reset": "10", "clear": "10", "reset data": "10",
        "11": "11", "export": "11", "export report": "11",
        "12": "12", "history": "12", "patient history": "12",
        "13": "13", "quit": "13", "exit": "13", "logout": "13"
    }
    return choice_map.get(val, val)


# =========================================================
# OBJECT-ORIENTED MODELS (DOMAIN ENTITIES)
# =========================================================

class Person:
    """Abstract base class representing an individual in the clinic."""

    def __init__(self, person_id: str, name: str, phone: str):
        self.person_id = person_id.strip()
        self.name = name.strip()
        if not validate_phone(phone):
            raise InvalidFormatError(f"Invalid phone number format: '{phone}'. Expected 11 digits starting with 01")
        self.phone = phone.strip()

    def display_profile(self) -> str:
        """Display basic profile information."""
        return f"[{self.person_id}] {self.name} | Phone: {self.phone}"

    def __str__(self) -> str:
        return self.display_profile()


class Patient(Person):
    """Patient entity storing personal details and visit history."""

    def __init__(self, person_id: str, name: str, phone: str, age: int, case_type: str):
        if not validate_patient_id(person_id):
            raise InvalidFormatError(f"Invalid patient ID format: '{person_id}'. Expected 'patient-<number>'")
        super().__init__(person_id, name, phone)
        self.age = int(age)
        self.case_type = case_type.strip()
        self.visit_history: list = []

    def display_profile(self) -> str:
        return f"[{self.person_id}] {self.name} | Phone: {self.phone} | Age: {self.age} | Case: {self.case_type or 'General Checkup'}"

    def priority_level(self) -> int:
        """Default priority level (2 for regular patients)."""
        return 2

    def add_visit(self, visit):
        """Append an appointment to patient's personal visit history."""
        self.visit_history.append(visit)


class EmergencyPatient(Patient):
    """High-priority emergency patient (Priority 1: preempts queue)."""

    def priority_level(self) -> int:
        return 1

    def display_profile(self) -> str:
        return f"{super().display_profile()} | Priority: Emergency (Highest)"


class RegularPatient(Patient):
    """Standard regular patient (Priority 2: normal queue)."""

    def priority_level(self) -> int:
        return 2

    def display_profile(self) -> str:
        return f"{super().display_profile()} | Priority: Regular (Normal)"


class Doctor(Person):
    """Medical doctor entity with specialty and availability status."""

    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        if not validate_doctor_id(person_id):
            raise InvalidFormatError(f"Invalid doctor ID format: '{person_id}'. Expected 'doctor-<number>'")
        super().__init__(person_id, name, phone)
        self.specialty = specialty.strip()
        self.availability = bool(availability)

    def display_profile(self) -> str:
        status = "Available" if self.availability else "Unavailable (Busy)"
        return f"[{self.person_id}] Dr. {self.name} | Specialty: {self.specialty} | Status: {status} | Phone: {self.phone}"

    def toggle_availability(self):
        """Toggle availability between True and False."""
        self.availability = not self.availability


class Appointment:
    """Clinic appointment linking Patient, Doctor, and a reserved 30-minute time slot."""

    DEFAULT_DURATION = DEFAULT_APPOINTMENT_DURATION

    def __init__(
        self,
        patient: Patient,
        doctor: Doctor,
        time: datetime,
        status: str = "pending",
        fee: float = 0.0,
        duration: timedelta = DEFAULT_DURATION,
    ):
        self.patient = patient
        self.doctor = doctor
        self.time = time
        self.status = status
        self.fee = float(fee)
        self.duration = duration

    @property
    def end_time(self) -> datetime:
        """End time of the appointment slot based on duration."""
        return self.time + self.duration

    def overlaps_with(self, other_time: datetime, other_duration: timedelta = DEFAULT_DURATION) -> bool:
        """Check whether this appointment interval overlaps with another time window."""
        if self.status == "cancelled":
            return False
        other_end = other_time + other_duration
        return max(self.time, other_time) < min(self.end_time, other_end)

    def update_status(self, new_status: str):
        """Update appointment status (pending, in_progress, completed, cancelled)."""
        valid_statuses = ("pending", "in_progress", "completed", "cancelled")
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status '{new_status}'. Valid statuses: {valid_statuses}")
        self.status = new_status

    def __str__(self) -> str:
        t_start = self.time.strftime("%Y-%m-%d %H:%M")
        t_end = self.end_time.strftime("%H:%M")
        return (
            f"Appointment: Patient {self.patient.name} with Dr. {self.doctor.name} | "
            f"Slot: {t_start} - {t_end} (30m) | Status: {self.status.upper()} | Fee: ${self.fee:.2f}"
        )


# =========================================================
# ADVANCED FUNCTIONAL TOOLS & ITERATORS
# =========================================================

class WaitingQueueIterator:
    """Custom iterator implementing Python iterator protocol (__iter__, __next__)."""

    def __init__(self, appointments: list):
        self._appointments = appointments
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._appointments):
            raise StopIteration
        appt = self._appointments[self._index]
        self._index += 1
        return appt


def make_triage_calculator(base_fee: float = 100.0, initial_emergency_count: int = 0):
    """Closure capturing emergency_count using nonlocal with accessor functions."""
    emergency_count = int(initial_emergency_count)

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return base_fee * 1.5
        return base_fee

    def get_emergency_count() -> int:
        return emergency_count

    def decrement_emergency_count() -> int:
        nonlocal emergency_count
        if emergency_count > 0:
            emergency_count -= 1
        return emergency_count

    def reset_count():
        nonlocal emergency_count
        emergency_count = 0

    calculate.get_emergency_count = get_emergency_count
    calculate.decrement_emergency_count = decrement_emergency_count
    calculate.reset_count = reset_count
    return calculate


def find_visits_recursive(visits: list, index: int = 0) -> list:
    """Recursively filter completed appointments from visit history without loops."""
    if index >= len(visits):
        return []

    current = visits[index]
    rest = find_visits_recursive(visits, index + 1)

    if getattr(current, "status", None) == "completed":
        return [current] + rest
    return rest


# =========================================================
# CLINIC MANAGER (CENTRAL CONTROLLER)
# =========================================================

class ClinicManager:
    """Central manager handling business logic, appointments, queues, caching, and persistence."""

    def __init__(self, base_fee: float = 100.0):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []
        # Instance attribute mapping doctor IDs to booked start times
        self.booked_date: dict[str, list[datetime]] = {}
        self.fee_calculator = make_triage_calculator(base_fee=base_fee)
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

    def export_report_to_file(self, path: str = "daily_report.txt") -> bool:
        """Export the daily report to a text file with a timestamp."""
        if self.current_user is not None and not self.current_user.has_permission("export_report"):
            raise ClinicError("Access denied. Your role does not permit this action.")

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

    def save_to_file(self, path: str = "clinic_data.json", silent: bool = False) -> bool:
        """Save entire clinic database to a JSON file with automatic directory creation."""
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            data = {
                "patients": [
                    {
                        "type": "Emergency" if (isinstance(p, EmergencyPatient) or p.priority_level() == 1) else "Regular",
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
                        "time": a.time.isoformat() if isinstance(a.time, datetime) else str(a.time),
                        "status": a.status,
                        "fee": a.fee
                    }
                    for a in self.appointments
                ]
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            if not silent:
                print(f"\n[SUCCESS] Clinic data saved successfully to '{path}'.\n")
            return True
        except Exception as e:
            print(f"\n[ERROR] Failed saving data to '{path}': {e}\n")
            return False

    def load_from_file(self, path: str = "clinic_data.json") -> bool:
        """Load clinic database from JSON with automatic initialization and corrupt-file backup."""
        initial_data = {"patients": [], "doctors": [], "appointments": []}
        parent = os.path.dirname(path)
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


# =========================================================
# UI HELPERS & STANDALONE ACTION FUNCTIONS
# =========================================================

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


# =========================================================
# MENUS & APPLICATION FLOW
# =========================================================

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
        print("|  [13] Logout / Switch User                           |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-13 or action name): ").strip()
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
        elif choice == "13":
            print(f"\nLogging out {current_user.display_role()} ({current_user.username})...")
            manager.save_to_file("clinic_data.json", silent=True)
            return
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please select from 1 to 13.\n")


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


if __name__ == "__main__":
    main()
