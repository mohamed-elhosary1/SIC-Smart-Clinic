
import re
from datetime import datetime




# الجزء 1: كلاسات الأخطاء المخصصة (Custom Exceptions)



#قبل التعديل:
# class Clinic_Error(Exception):
#     pass
# class Invalidappointment_time_Error(Clinic_Error):
#     pass
# class DuplicatingBoking_Error(Clinic_Error):
#     pass
# class PateintNotFound_Error(Clinic_Error):
#     pass
# class DocumentNotFound_Error(Clinic_Error):
#     pass
#
# الخطأ:
# كلها اخطاء املائية مش اكتر
#    - DuplicatingBoking_Error (تكتب Boking بدل Booking و Duplicating بدل Duplicate).
#    - PateintNotFound_Error (مكتوبة Pateint بدل Patient).
#    - DocumentNotFound_Error (مكتوبة Document "مستند" بدل Doctor "طبيب"!).
#ivalid format error مكانش موجود
# السبب:
# اخطاء املائية بتعمل ايرورز بس عادي
# بعد التعديل:
class ClinicError(Exception):
    """Base exception for the whole clinic system."""
    pass


class InvalidAppointmentTimeError(ClinicError):
    """Raised when an appointment time is invalid (past date, wrong format, etc.)."""
    pass


class DuplicateBookingError(ClinicError):
    """Raised when a patient tries to book a slot that is already taken."""
    pass


class PatientNotFoundError(ClinicError):
    """Raised when a given patient ID does not exist in the system."""
    pass


class DoctorNotFoundError(ClinicError):
    """Raised when a given doctor ID does not exist in the system."""
    pass


class InvalidFormatError(ClinicError):
    """Raised when a field (ID/phone) fails regex validation."""
    pass

r"""
دا توافق توفير وقت فكك منه وانزل على جزء الريجيكس
"""

Clinic_Error = ClinicError
Invalidappointment_time_Error = InvalidAppointmentTimeError
DuplicatingBoking_Error = DuplicateBookingError
PateintNotFound_Error = PatientNotFoundError
DocumentNotFound_Error = DoctorNotFoundError

#  (Regex Validators) -------------------------------------

# قبل التعديل
# def validate_patient_id(patient_id):
#     pattern="patient-[0-9]+"
#     if re.fullmatch(pattern,patient_id):
#         return True
#     return False
# def validate_doctor_id(doctor_id):
#     pattern="doctor-[0-9]+"
#     if re.fullmatch(pattern,doctor_id):
#         return True
#     return False
# def validate_phone_(phone):
#     return bool(re.fullmatch("01[0-9]{9}",phone))
#
# الخطأ:
#تعريف الباترين غلط
# غلط في تسمية دالةالتلفون
# السبب:
# بعد التعديل:
PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")
PHONE_PATTERN = re.compile(r"01[0-9]{9}")


def validate_patient_id(patient_id: str) -> bool:
    """Check whether patient_id matches PATIENT_ID_PATTERN."""
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
    return bool(PHONE_PATTERN.fullmatch(phone))


validate_phone_ = validate_phone



# person class -------------------------------------------



# قبل التعديل:
# class person:
#     def __init__(self,person_id,name,phone_):
#         self.person_id = person_id
#         self.name = name
#         self.phone_ = phone_
#     def display_profile(self):
#         return f"{self.person_id} {self.name} {self.phone_}"
#     def __str__(self):
#         return f"{self.person_id} {self.name} {self.phone_}"
#
# الخطأ:
# 1. اسم الكلاس person بحروف صغيرة بدل كابيتال بيعملرايرور بس مش مشكلة .
#
#
#
#بعد التعديل:
class Person:


    def __init__(self, person_id: str, name: str, phone: str):
        self.person_id = person_id
        self.name = name
        self.phone = phone
        self.phone_ = phone  # Alias للتوافق

    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone}"

    def __str__(self):
        return f"{self.person_id} {self.name} {self.phone}"


person = Person


# ال كلاس Patient الأساسي -------------------------

# [قبل التعديل]:
# class patient(person):
#     def __init__(self,patient_id,name,phone,age,case_type):
#         if not validate_patient_id(patient_id):
#             raise PateintNotFound_Error("patient_id")
#         super().__init__(patient_id,name,phone)
#         self.age = age
#         self.case_type = case_type
#         self.history = []
#     def display_profile(self):
#         return f"{self.person_id} {self.name} {self.phone_} {self.age} {self.case_type}"
#     def priority_level(self):
#         return "normal"
#     def add_visit(self,visit):
#         self.history.append(visit)
#
# الخطأ:
# 1. خطأ لوجيك  : رفع PateintNotFound_Error عند فشل التحقق محاجة تعديل بسيط مش اكتر
# 2. نوع القيمة المرجعة من priority_level() محتاجة تتبظط.
#
# السبب:
# داتا تايبس مش زي بعض كمان اسماء مختلفة مشش اكتر
# [بعد التعديل]:
class Patient(Person):


    def __init__(self, person_id: str, name: str, phone: str, age: int, case_type: str):
        if not validate_patient_id(person_id):
            raise InvalidFormatError(f"Invalid patient ID format: '{person_id}'")
        super().__init__(person_id, name, phone)
        self.age = age
        self.case_type = case_type
        self.visit_history = []
        self.history = self.visit_history  # Alias للتوافق

    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone} {self.age} {self.case_type}"

    def priority_level(self):
        return 2

    def add_visit(self, visit):
        self.visit_history.append(visit)


patient = Patient



# الجزء 5: كلاسات الوراثة EmergencyPatient و RegularPatient -----------------------

# [قبل التعديل]:
# class emergency_patient(patient):
#     def priority_level(self):
#         return 1
#     def display_profile(self):
#         list=super().display_profile()
#         return f"{list} high priority"
# class Regular_Patients(patient):
#     def priority_level(self):
#         return 2
#     def display_profile(self):
#         list= super().display_profile()
#         return f"{list} regular priority"
#
# الخطأ:
# 1. حجب الاسم  list (Built-in Shadowing): استخدام listكلوكال .
# اخطاء تسمية برضو #
# السبب:
# تسمية المتغير باسم list بتمنع استخدام دالة list()  ،
#
# [بعد التعديل]
class EmergencyPatient(Patient):

    def priority_level(self):
        return 1

    def display_profile(self):
        base_profile = super().display_profile()  #  حجب اسم list
        return f"{base_profile} high priority"


class RegularPatient(Patient):

    def priority_level(self):
        return 2

    def display_profile(self):
        base_profile = super().display_profile()  # تجنب حجب اسم list
        return f"{base_profile} regular priority"


emergency_patient = EmergencyPatient
Regular_Patients = RegularPatient



# الجزء 6: كلاس الدكتور Doctor

# [قبل التعديل]:
# class doctor(person):
#     def __init__(self,doctor_id,name,phone_,speciality,availability=True or False):
#         self.doctor_id = doctor_id
#         self.person_id = doctor_id
#         self.name = name
#         self.phone_ = phone_
#         self.speciality = speciality
#         self.availability = availability
#     def display_profile(self):
#         return f"{self.doctor_id} {self.name} {self.phone_} {self.speciality}"
#     def toggle_availability(self):
#         self.availability = not self.availability
#
# الخطأ:
# 1.  availability = True or False ناتج غلط افتراضي.
# 2. مفيش استدعاء استدعاء super().__init__(doctor_id, name, phone_).
# 3. اسم الكلاس  .
#
# السبب:
# عدم استدعاء super() هيبوظ مبدأ الوراثة كدا عم مندل بتاع البسلة يزعل   .
#
# [بعد التعديل]:
class Doctor(Person):

    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        super().__init__(person_id, name, phone)
        self.doctor_id = person_id
        self.specialty = specialty
        self.speciality = specialty
        self.availability = availability

    def display_profile(self):
        return f"{self.doctor_id} {self.name} {self.phone} {self.specialty}"

    def toggle_availability(self):
        self.availability = not self.availability


doctor = Doctor

#  Appointment ----------------------------
# قبل التعديل :
# class appointment:
#     booked_date = {}
#     def __init__(self,patient,doctor,date,fee,status="scheduled"):
#         if doctor.person_id not in appointment.booked_date:
#             appointment.booked_date[doctor.person_id] = []
#         if date in appointment.booked_date[doctor.person_id]:
#             raise DuplicatingBoking_Error("appointment already booked")
#         appointment.booked_date[doctor.person_id].append(date)
#         self.patient=patient
#         self.doctor=doctor
#         self.date=date
#         self.fee=fee
#         self.status=status
#
#     def update_status(self,new_status):
#         self.status=new_status
#     def __str__(self) :
#         return f"{self.patient.person_id} {self.doctor.person_id} {self.date} {self.status}"
#
# الخطأ:
#كلمني افهمهولك او اقرا االكود هتلاقيه بعد التعديل

# بعد التعديل :
class Appointment:
    """
    Links a patient with a doctor at a given time, and tracks
    the visit status (pending/completed/cancelled, etc.).
    """

    booked_date = {}

    def __init__(self, patient: Patient, doctor: Doctor, time: datetime, status: str = "pending", fee: float = 0):
        if doctor.person_id not in Appointment.booked_date:
            Appointment.booked_date[doctor.person_id] = []
        if time in Appointment.booked_date[doctor.person_id]:
            raise DuplicateBookingError("appointment already booked")
        Appointment.booked_date[doctor.person_id].append(time)

        self.patient = patient
        self.doctor = doctor
        self.time = time
        self.date = time  #  للتوافق
        self.status = status
        self.fee = fee

    def update_status(self, new_status: str):
        self.status = new_status

    def __str__(self):
        return f"{self.patient.person_id} {self.doctor.person_id} {self.time} {self.status}"


appointment = Appointment # بوفر وقت


#  (-Test عشان منروحش فداهية)
if __name__ == "__main__":
    print("--- Testing Omar's corrected part ---")
    
    p1 = emergency_patient("patient-243", "ali mohamed", "01272829111", 25, "chestpain")
    print("Patient Profile:", p1.display_profile())
    print("Patient Priority:", p1.priority_level())

    d1 = doctor("doctor-100", "mohamed alaa", "01205341252", "cardiologist")
    print("Doctor Profile:", d1.display_profile())

    appt1 = appointment(p1, d1, "2026-09-05 20:00", fee=300)
    print("Appointment:", appt1)

    print("\n All tests passed successfully without errors!")
