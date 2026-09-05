
#------------------- المكتبات -----------------
import re
from functools import reduce
from datetime import datetime
#----------------------------------------------

# =========================================================
# SECTION OWNED BY: عمر (OMAR)
# Scope: Custom exceptions + regex validators
# =========================================================

class ClinicError(Exception):
    """
      inherit دا الاكسبشنز الاساسي اي حاجة تحته لازم يكزن في
      #TODO
    """
    pass


class InvalidAppointmentTimeError(ClinicError):
    # اخطاء الوقت هسيب تفاصيل  واكتب الرسالة دي وانت بتعمل رايز
    """ time is invalid (past date, wrong format, etc.)."""
    # TODO
    pass


class DuplicateBookingError(ClinicError):
    """ patient tries to book a slot that is already taken"""
    # TODO
    pass


class PatientNotFoundError(ClinicError):
    """Raised when a given patient ID does not exist in the system"""
    # TODO
    pass


class DoctorNotFoundError(ClinicError):
    """Raised when a given doctor ID does not exist in the system"""
    # TODO
    pass


class InvalidFormatError(ClinicError):
    """Raised when a field fails regex validation."""
    # التلفون وال ID بس
    # TODO
    pass

# توافق فكك منه
Clinic_Error = ClinicError
Invalidappointment_time_Error = InvalidAppointmentTimeError
DuplicatingBoking_Error = DuplicateBookingError
PateintNotFound_Error = PatientNotFoundError
DocumentNotFound_Error = DoctorNotFoundError

r"""
ونبي ظبط الجزء دا سايب كومنت ملون عشان تشوفه 
"""

# Regex patterns (required: at least 2 validated fields)
PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")   # TODO: define patient ID pattern
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")    # TODO: define doctor ID pattern
PHONE_PATTERN = re.compile(r"01[0-9]{9}")        # TODO: define phone number pattern


def validate_patient_id(patient_id: str) -> bool:
    """Check whether patient_id matches PATIENT_ID_PATTERN."""
    # عندي فكرة ID GENERATING حلوة قدام
    # TODO
    if PATIENT_ID_PATTERN.fullmatch(patient_id):
        return True
    return False


def validate_doctor_id(doctor_id: str) -> bool:
    """Check whether doctor_id matches DOCTOR_ID_PATTERN."""
    if DOCTOR_ID_PATTERN.fullmatch(doctor_id):
        return True
    return False


def validate_phone(phone: str) -> bool:
    """Check whether phone matches PHONE_PATTERN."""
    # TODO
    return bool(PHONE_PATTERN.fullmatch(phone))


validate_phone_ = validate_phone


# =========================================================
# SECTION OWNED BY: عمر (OMAR)
# Scope: Base class + Person subclasses (Patient, Doctor) + Appointment
# =========================================================

class Person:


    def __init__(self, person_id: str, name: str, phone: str):
        # TODO: store fields + call phone/id validation
        self.person_id = person_id
        self.name = name
        self.phone = phone
        self.phone_ = phone

    def display_profile(self):

        # TODO
        return f"{self.person_id} {self.name} {self.phone}"

    def __str__(self):
        # TODO
        return f"{self.person_id} {self.name} {self.phone}"


class Patient(Person):
    """
    Represents a clinic patient
    """

    def __init__(self, person_id: str, name: str, phone: str, age: int, case_type: str):
        if not validate_patient_id(person_id):
            raise InvalidFormatError("Invalid patient ID format")
        super().__init__(person_id, name, phone)
        # TODO: age, case_type, visit_history, etc.
        self.age = age
        self.case_type = case_type
        self.visit_history = []
        self.history = self.visit_history

    def display_profile(self):
#المريض مش الدكتور         # TODO
        return f"{self.person_id} {self.name} {self.phone} {self.age} {self.case_type}"

    def priority_level(self):
        # ياريت تتقسم درجات مش ترو وفولس
        # TODO
        return 2

    def add_visit(self, visit):
        self.visit_history.append(visit)


class EmergencyPatient(Patient):
    """A patient with an urgent/emergency case type ."""
    # راجل بيموت مننا

    def priority_level(self):
        # TODO: must return a genuinely different value/behavior than RegularPatient
        return 1

    def display_profile(self):
        """ adds emergency-specific details to the profile."""
        # TODO
        base_profile = super().display_profile()
        return f"{base_profile} high priority"


class RegularPatient(Patient):
    """A patient with a normal case type."""
    # مش طوارئ لو مش فاهم

    def priority_level(self):
        # TODO: normal priority logic, different from EmergencyPatient
        return 2

    def display_profile(self):
        base_profile = super().display_profile()
        return f"{base_profile} regular priority"


class Doctor(Person):
# ونبي اقري اسم الكلاس قبل ما تعدلي :)
    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        super().__init__(person_id, name, phone)
        # TODO
        self.doctor_id = person_id
        self.specialty = specialty
        self.speciality = specialty
        self.availability = availability

    def display_profile(self):
        # بتاعتتتت الدكتور اوعي تتلغيطي وتحطي المريض
        # TODO
        return f"{self.doctor_id} {self.name} {self.phone} {self.specialty}"

    def toggle_availability(self):
        self.availability = not self.availability


class Appointment:
    """
    Links a patient with a doctor at a given time, and tracks
    the visit status (pending/completed/cancelled.).
    """

    booked_date = {}

    def __init__(self, patient: Patient, doctor: Doctor, time: datetime, status: str = "pending", fee: float = 0):
        # TODO: store fields + validate time (raise InvalidAppointmentTimeError if needed)
        if doctor.person_id not in Appointment.booked_date:
            Appointment.booked_date[doctor.person_id] = []
        if time in Appointment.booked_date[doctor.person_id]:
            raise DuplicateBookingError("appointment already booked")
        Appointment.booked_date[doctor.person_id].append(time)

        self.patient = patient
        self.doctor = doctor
        self.time = time
        self.date = time
        self.status = status
        self.fee = fee  # TODO: set via the closure fee calculator

    def update_status(self, new_status: str):
        """Update the appointment's status (pending -> completed)"""
        # TODO
        self.status = new_status

    def __str__(self):
        return f"{self.patient.person_id} {self.doctor.person_id} {self.time} {self.status}"

# توافق الاسماء متلعبوش فيها
person = Person
patient = Patient
emergency_patient = EmergencyPatient
Regular_Patients = RegularPatient
doctor = Doctor
appointment = Appointment


# =========================================================
# SECTION OWNED BY: ندى (NADA)
# Scope: Custom iterator for the waiting queue
# =========================================================

class WaitingQueueIterator:
    # مش عارف اعبر بس هتفهميها يعني

    def __init__(self, appointments: list):
        self._appointments = appointments
        self._index = 0

    def __iter__(self):
        # TODO
        return self

    def __next__(self):
        """Return the next appointment, raise StopIteration at the end."""
        # TODO
        pass


# =========================================================
# SECTION OWNED BY: ندى (NADA)
# Scope: Closures
# =========================================================

def make_triage_calculator(base_fee: float):

    emergency_count = 0  # state that changes inside the closure

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        # TODO: compute the fee based on patient.priority_level()
        # if emergency: emergency_count += 1
        # بتشتغل عادي ( مش لاقي ايموجي سهم لفوق )
        pass

    return calculate


# =========================================================
# SECTION OWNED BY: ندى (NADA)
# Scope: ClinicManager (the main orchestrator class)
# =========================================================

class ClinicManager:
    """
    Central class that owns all patients, doctors, and appointments.
    Responsible for registration, booking, queue handling, and reports.
    """

    def __init__(self):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []
        self.fee_calculator = make_triage_calculator(base_fee=100)  # TODO: adjust base_fee

    # ---------- Registration ----------

    def register_patient(self, patient: Patient):
        """Add a new patient, checking for duplicate IDs and valid format."""
        # TODO: raise InvalidFormatError / handle duplicates
        pass

    def add_doctor(self, doctor: Doctor):
        """Add a new doctor to the system."""
        # TODO
        pass

    # ---------- Appointments ----------

    def book_appointment(self, patient_id: str, doctor_id: str, time: datetime):
        """
        Book a new appointment.
        Must validate patient/doctor existence, time validity,
        and prevent duplicate bookings.
        """
        # TODO: PatientNotFoundError / DoctorNotFoundError /
        # DuplicateBookingError / InvalidAppointmentTimeError
        pass

    def update_visit_status(self, appointment_index: int, new_status: str):
        """Update the status of an existing appointment."""
        # TODO
        pass

    # ---------- Queue / Reports (functional tools) ----------

    def get_emergency_patients(self):
        """Return only emergency patients using filter + lambda."""
        # TODO
        pass

    def sort_queue_by_priority(self):
        """Sort the waiting queue using sorted() with a lambda key."""
        # TODO
        pass

    def get_waiting_queue_iterator(self):
        """Return a ready-to-use WaitingQueueIterator over current appointments."""
        # ملاحظة انا قرفت وانا بكتب الكلام دا كلو فانجزو
        # TODO
        pass

    def calculate_total_revenue(self):
        """Calculate total revenue from completed appointments using reduce."""
        # TODO
        pass

    def daily_report(self):
        # TODO
        pass


#-----------------------------main-----------------------------


def main():
    pass


if __name__ == "__main__":
    main()