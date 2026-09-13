"""Domain entities: Person, Patient, EmergencyPatient, RegularPatient, Doctor, Appointment."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from .exceptions import InvalidFormatError
from .validators import validate_patient_id, validate_doctor_id, validate_phone

# Default duration for any clinic appointment slot (30 minutes)
DEFAULT_APPOINTMENT_DURATION = timedelta(minutes=30)

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

    def overlaps_with(self, other_time: "datetime | Appointment", other_duration: timedelta = DEFAULT_DURATION) -> bool:
        """Check whether this appointment interval overlaps with another time window or appointment."""
        if self.status == "cancelled":
            return False
        if isinstance(other_time, Appointment):
            if other_time.status == "cancelled":
                return False
            other_duration = other_time.duration
            other_time = other_time.time
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

