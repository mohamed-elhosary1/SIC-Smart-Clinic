# ==============================================================================
# كود عمر (OMAR) - مراجعة تفصيلية قبل وبعد التعديل
# يحتوي هذا الملف على:
# 1. كود عمر قبل التعديل (في كومنت)
# 2. ذكر الخطأ (The Error)
# 3. سبب الخطأ وتأثيره (The Reason)
# 4. كود عمر بعد التعديل والتصحيح
# ==============================================================================

import re
from datetime import datetime


# ==============================================================================
# الجزء 0: مشكلة تكرار الملف بالكامل (File-Level Duplication)
# ==============================================================================
# [قبل التعديل]:
# ملف omar_part (1).py كان يحتوي على 190 سطرًا، الأسطر من 96 إلى 190 كانت
# تكرارًا حرفيًا لنفس الأسطر من 1 إلى 95.
#
# الخطأ:
# تكرار الكود بالكامل (Duplicate Code).
#
# السبب:
# خطأ ناتج عن Copy-Paste داخل الملف، مما يؤدي إلى إعادة تعريف الكلاسات مرتين
# وإهدار موارد الكود وإرباك أي مبرمج يقرأ الملف.
#
# [بعد التعديل]:
# تم حذف النصف الثاني المكرر بالكامل والاحتفاظ بنسخة واحدة نظيفة ومصححة.
# ==============================================================================


# ==============================================================================
# الجزء 1: كلاسات الأخطاء المخصصة (Custom Exceptions)
# ==============================================================================
# [قبل التعديل]:
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
# 1. مخالفة معايير التسمية القياسية في بايثون PEP 8 (استخدام Underscores داخل أسماء الكلاسات).
# 2. أخطاء إملائية (Typos) فادحة:
#    - DuplicatingBoking_Error (كتب Boking بدل Booking و Duplicating بدل Duplicate).
#    - PateintNotFound_Error (كتب Pateint بدل Patient).
#    - DocumentNotFound_Error (كتب Document "مستند" بدل Doctor "طبيب"!).
# 3. غياب كلاس InvalidFormatError تمامًا، وهو مطلوب لفحص Regex.
#
# السبب:
# هذه الأخطاء الإملائية تجعل الكود غير متوافق مع main.py؛ فعندما يحاول main.py
# صيد خطأ مثل: except DoctorNotFoundError، لن يتم صيده لأن الكلاس اسمه Document!
#
# [بعد التعديل]:
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


# توافق رجعي (Compatibility Aliases) لضمان عدم تعطل أي استدعاء قديم بأسماء عمر:
Clinic_Error = ClinicError
Invalidappointment_time_Error = InvalidAppointmentTimeError
DuplicatingBoking_Error = DuplicateBookingError
PateintNotFound_Error = PatientNotFoundError
DocumentNotFound_Error = DoctorNotFoundError


# ==============================================================================
# الجزء 2: دوال وأنماط التحقق (Regex Validators)
# ==============================================================================
# [قبل التعديل]:
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
# 1. تعريف الـ Pattern كنص عادي داخل جسم كل دالة وإعادة ترجمته في كل استدعاء.
# 2. تسمية دالة الهاتف validate_phone_ بشرطة سفلية في النهاية مما خالف main.py (validate_phone).
#
# السبب:
# تصميم المشروع في main.py يطلب Compiled Patterns عامة (PATIENT_ID_PATTERN, DOCTOR_ID_PATTERN, PHONE_PATTERN)
# لتحسين الأداء وتوحيد مكان التعديل على صيغ الأرقام.
#
# [بعد التعديل]:
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


# Alias للتوافق مع كود عمر
validate_phone_ = validate_phone


# ==============================================================================
# الجزء 3: الكلاس الأساسي Person
# ==============================================================================
# [قبل التعديل]:
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
# 1. اسم الكلاس person بحروف صغيرة بدل PascalCase (Person).
# 2. اسم الخاصية phone_ بشرطة سفلية بدل phone المتفق عليه في main.py.
#
# السبب:
# الكلاسات في بايثون يجب أن تبدأ بحرف كبير، وتسمية المتغيرات بـ phone_ كانت تسبب
# AttributeError عند محاولة الوصول إلى obj.phone في أجزاء المشروع الأخرى.
#
# [بعد التعديل]:
class Person:
    """
    Base class for anyone in the clinic system (patients and doctors).
    Holds the shared identity fields (id, name, phone).
    """

    def __init__(self, person_id: str, name: str, phone: str):
        self.person_id = person_id
        self.name = name
        self.phone = phone
        self.phone_ = phone  # Alias للتوافق

    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone}"

    def __str__(self):
        return f"{self.person_id} {self.name} {self.phone}"


# Alias للتوافق
person = Person


# ==============================================================================
# الجزء 4: كلاس Patient الأساسي
# ==============================================================================
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
# 1. خطأ منطقي فادح: رفع PateintNotFound_Error عند فشل التحقق من الـ ID!
# 2. نوع القيمة المرجعة من priority_level(): تُرجع نص "normal".
# 3. اسم المتغير self.history بدل self.visit_history المحدد في سكيلتون main.py.
# 4. اسم الكلاس patient بحروف صغيرة.
#
# السبب:
# 1. إذا أدخل المستخدم ID غير مطابق للصيغة، فالخطأ هو InvalidFormatError وليس أن المريض "غير موجود".
# 2. إرجاع "normal" (نص) يسبب انهيار كامل TypeError عند ترتيب الطابور بالـ sorted مع المرضى
#    الآخرين الذين يُرجعون أرقامًا (1 و 2)، لأن بايثون 3 لا تقارن str مع int!
#
# [بعد التعديل]:
class Patient(Person):
    """
    Represents a clinic patient. Holds medical/queue-related info
    on top of the base Person fields.
    """

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
        # تم تعديلها إلى رقم 2 لتكون متوافقة عدديًا مع EmergencyPatient (1)
        return 2

    def add_visit(self, visit):
        self.visit_history.append(visit)


# Alias للتوافق
patient = Patient


# ==============================================================================
# الجزء 5: كلاسات الوراثة EmergencyPatient و RegularPatient
# ==============================================================================
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
# 1. حجب الاسم المدمج list (Built-in Shadowing): استخدام list كمتغير محلي.
# 2. تسمية Regular_Patients بصيغة الجمع والشرطة السفلية، و emergency_patient بحروف صغيرة.
#
# السبب:
# تسمية المتغير باسم list تمنع استخدام دالة list() داخل النطاق، كما أن الأسماء
# تخالف المعيار المطلوب في المشروع (EmergencyPatient و RegularPatient).
#
# [بعد التعديل]:
class EmergencyPatient(Patient):
    """A patient with an urgent/emergency case type — highest queue priority (1)."""

    def priority_level(self):
        return 1

    def display_profile(self):
        base_profile = super().display_profile()  # تجنب حجب اسم list
        return f"{base_profile} high priority"


class RegularPatient(Patient):
    """A patient with a normal (non-emergency) case type (2)."""

    def priority_level(self):
        return 2

    def display_profile(self):
        base_profile = super().display_profile()  # تجنب حجب اسم list
        return f"{base_profile} regular priority"


# Aliases للتوافق مع الأسماء القديمة
emergency_patient = EmergencyPatient
Regular_Patients = RegularPatient


# ==============================================================================
# الجزء 6: كلاس الطبيب Doctor
# ==============================================================================
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
# 1. صياغة availability = True or False كمعامل افتراضي.
# 2. عدم استدعاء super().__init__(doctor_id, name, phone_).
# 3. اسم الكلاس doctor بحروف صغيرة.
# 4. كتابة speciality بالإملاء البريطاني بينما main.py يستخدم specialty.
#
# السبب:
# عدم استدعاء super() يكسر مبدأ الوراثة ويعيد تعريف المتغيرات يدويًا.
# والتعبير True or False يُعطي True لكنه كتابة غير دقيقة برمجياً.
#
# [بعد التعديل]:
class Doctor(Person):
    """Represents a doctor with a specialty and availability status."""

    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        super().__init__(person_id, name, phone)
        self.doctor_id = person_id
        self.specialty = specialty
        self.speciality = specialty  # Alias للتوافق
        self.availability = availability

    def display_profile(self):
        return f"{self.doctor_id} {self.name} {self.phone} {self.specialty}"

    def toggle_availability(self):
        self.availability = not self.availability


# Alias للتوافق
doctor = Doctor


# ==============================================================================
# الجزء 7: كلاس المواعيد Appointment
# ==============================================================================
# [قبل التعديل]:
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
# 1. جعل fee إلزاميًا وبدون قيمة افتراضية، بينما في main.py يتم حسابه عبر closure لاحقًا أو افتراضيًا 0.
# 2. استخدام date كنص بدلاً من time المتوقع كـ datetime / time.
# 3. الحالة الافتراضية "scheduled" بدل "pending" المعتمدة في النظام.
# 4. اسم الكلاس appointment بحروف صغيرة.
#
# السبب:
# إذا أنشأ main.py موعدًا بالشكل Appointment(patient, doctor, time) بدون تمرير fee،
# سينهار كود عمر بـ TypeError: missing 1 required positional argument: 'fee'.
#
# [بعد التعديل]:
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
        self.date = time  # Alias للتوافق
        self.status = status
        self.fee = fee

    def update_status(self, new_status: str):
        self.status = new_status

    def __str__(self):
        return f"{self.patient.person_id} {self.doctor.person_id} {self.time} {self.status}"


# Alias للتوافق
appointment = Appointment


# ==============================================================================
# الجزء 8: تجربة تشغيل كود عمر بعد التصحيح (Self-Test)
# ==============================================================================
if __name__ == "__main__":
    print("--- Testing Omar's corrected part ---")
    
    # تجربة إنشاء مريض طوارئ
    p1 = emergency_patient("patient-243", "ali mohamed", "01272829111", 25, "chestpain")
    print("Patient Profile:", p1.display_profile())
    print("Patient Priority:", p1.priority_level())

    # تجربة إنشاء طبيب
    d1 = doctor("doctor-100", "mohamed alaa", "01205341252", "cardiologist")
    print("Doctor Profile:", d1.display_profile())

    # تجربة إنشاء موعد
    appt1 = appointment(p1, d1, "2026-09-05 20:00", fee=300)
    print("Appointment:", appt1)

    print("\n All tests passed successfully without errors!")
