"""Regex patterns and input normalization helpers."""

import re

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
        "4": "cancelled", "cancelled": "cancelled", "canceled": "cancelled",
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
        "13": "13", "quit": "13", "exit": "13", "logout": "13",
    }
    return choice_map.get(val, val)
