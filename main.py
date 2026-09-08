#------------------- المكتبات -----------------
import json
import os
import random
import re
import shutil
from functools import reduce
from datetime import datetime
#----------------------------------------------


# =========================================================
# EXCEPTIONS (استثناءات النظام)
# =========================================================

class ClinicError(Exception):
    """الأساس لكل أخطاء العيادة"""
    pass


class InvalidAppointmentTimeError(ClinicError):
    """وقت الكشف غير صالح أو في الماضي"""
    pass


class DuplicateBookingError(ClinicError):
    """حجز متكرر لنفس الطبيب أو المريض في نفس الموعد أو تكرار ID"""
    pass


class PatientNotFoundError(ClinicError):
    """المريض غير مسجل في النظام"""
    pass


class DoctorNotFoundError(ClinicError):
    """الطبيب غير مسجل في النظام"""
    pass


class InvalidFormatError(ClinicError):
    """فشل التحقق من صيغة الـ ID أو رقم الهاتف"""
    pass


# =========================================================
# AUTHENTICATION & ROLE-BASED ACCESS CONTROL (نظام الصلاحيات)
# =========================================================

class User:
    """كلاس أب لأي مستخدم إداري أو طبي في النظام (Staff / Doctor)"""

    def __init__(self, username: str, password: str, allowed_actions: set):
        self.username = username
        self.password = password  # ملحوظة: للتبسيط فقط - في الأنظمة الحقيقية يتم استخدام hashing
        self.allowed_actions = allowed_actions

    def has_permission(self, action: str) -> bool:
        """فحص الصلاحية الافتراضية بناءً على مجموعة الأكشنز المسموحة"""
        return action in self.allowed_actions

    def display_role(self) -> str:
        """عرض اسم الدور الوظيفي للمستخدم"""
        return "Generic User"


class StaffUser(User):
    """موظف العيادة - يمتلك كافة الصلاحيات الإدارية والتشغيلية في النظام دون قيود"""

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=set())

    def has_permission(self, action: str) -> bool:
        # موظف العيادة مسموح له بكافة العمليات دائمًا
        return True

    def display_role(self) -> str:
        return "Staff"


class DoctorUser(User):
    """الطبيب - يعاين طابور الانتظار ويحدث حالة الكشف ويطلع على تاريخ المريض والتقرير اليومي"""

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


# قاعدة بيانات المستخدمين التجريبية الافتراضية للطاقم الطبي والإداري
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
    """التحقق من بيانات الطاقم فقط (Staff / Doctor) — مفيش مرضى هنا خالص"""
    u_key = username.strip().lower()
    p_clean = password.strip()
    user_record = USERS_DB.get(u_key)
    if not user_record or user_record["password"] != p_clean:
        raise ClinicError("Invalid credentials. Please check username and password.")
    return user_record["factory"](username.strip(), p_clean)


# =========================================================
# REGEX VALIDATORS (التحقق بالـ Regex)
# =========================================================

PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")   # صيغة ID المريض: patient-123
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")    # صيغة ID الدكتور: doctor-123
PHONE_PATTERN = re.compile(r"01[0-9]{9}")        # 11 رقم بيبدأ بـ 01


def validate_patient_id(patient_id: str) -> bool:
    """فحص صحة ID المريض"""
    return bool(PATIENT_ID_PATTERN.fullmatch(patient_id.strip()))


def validate_doctor_id(doctor_id: str) -> bool:
    """فحص صحة ID الدكتور"""
    return bool(DOCTOR_ID_PATTERN.fullmatch(doctor_id.strip()))


def validate_phone(phone: str) -> bool:
    """فحص صحة رقم الموبايل المصري"""
    return bool(PHONE_PATTERN.fullmatch(phone.strip()))


# =========================================================
# FLEXIBLE INPUT HELPERS (مرونة الإدخال)
# =========================================================

def parse_patient_type(val: str) -> str:
    """قبول 1 أو Regular أو عادي أو أي اختصار"""
    v = val.strip().lower()
    if v in ("1", "regular", "reg", "r", "عادي", ""):
        return "1"
    if v in ("2", "emergency", "emg", "em", "e", "urgent", "طوارئ"):
        return "2"
    return ""


def parse_status(val: str) -> str:
    """قبول الحالات بأي شكل (كلمة كاملة أو رقم أو اختصار)"""
    v = val.strip().lower()
    if v in ("pending", "p", "انتظار", "قيد الانتظار", "1"):
        return "pending"
    if v in ("completed", "complete", "c", "done", "مكتمل", "تم", "2"):
        return "completed"
    if v in ("cancelled", "cancel", "canceled", "x", "ملغي", "الغاء", "3"):
        return "cancelled"
    if v in ("in_progress", "inprogress", "progress", "in progress", "جاري", "4"):
        return "in_progress"
    return ""


def parse_menu_choice(val: str) -> str:
    """قبول الاختيارات من المنيو كرقم أو ككلمة (1 إلى 13)"""
    v = val.strip().lower()
    if v in ("1", "register", "reg", "patient", "register patient", "تسجيل مريض"):
        return "1"
    if v in ("2", "doctor", "doc", "add doctor", "اضافة دكتور"):
        return "2"
    if v in ("3", "book", "appointment", "book appointment", "حجز موعد"):
        return "3"
    if v in ("4", "update", "status", "update status", "تحديث حالة"):
        return "4"
    if v in ("5", "queue", "show queue", "show", "طابور"):
        return "5"
    if v in ("6", "toggle", "doctor status", "toggle doctor", "تبديل دكتور", "تبديل حالة الدكتور"):
        return "6"
    if v in ("7", "delete", "del", "remove", "delete appointment", "حذف موعد", "مسح موعد"):
        return "7"
    if v in ("8", "report", "daily report", "تقرير"):
        return "8"
    if v in ("9", "save", "save data", "حفظ"):
        return "9"
    if v in ("10", "reset", "reset data", "clear", "مسح", "تصفير", "اعادة ضبط"):
        return "10"
    if v in ("11", "export", "export report", "export daily report", "تصدير", "تصدير التقرير"):
        return "11"
    if v in ("12", "history", "patient history", "completed visits", "سجل", "سجل المريض", "تاريخ المريض"):
        return "12"
    if v in ("13", "quit", "exit", "q", "خروج"):
        return "13"
    return v


# =========================================================
# OOP DATA MODELS
# =========================================================

class Person:
    def __init__(self, person_id: str, name: str, phone: str):
        # تفعيل فحص رقم التلفون ورفع InvalidFormatError لو غلط
        if not validate_phone(phone):
            raise InvalidFormatError(f"Invalid phone number '{phone}'. Must be 11 digits starting with 01.")
        
        self.person_id = person_id.strip()
        self.name = name.strip()
        self.phone = phone.strip()

    def display_profile(self) -> str:
        return f"[{self.person_id}] {self.name} | Phone: {self.phone}"

    def __str__(self) -> str:
        return self.display_profile()


class Patient(Person):
    def __init__(self, person_id: str, name: str, phone: str, age: int, case_type: str):
        if not validate_patient_id(person_id):
            raise InvalidFormatError(f"Invalid patient ID format: '{person_id}'. Expected 'patient-<number>'")
        super().__init__(person_id, name, phone)
        self.age = int(age)
        self.case_type = case_type.strip()
        self.visit_history: list = []

    def display_profile(self) -> str:
        # بروفايل المريض الأساسي
        return f"[{self.person_id}] {self.name} | Phone: {self.phone} | Age: {self.age} | Case: {self.case_type or 'General Checkup'}"

    def priority_level(self) -> int:
        # درجة 2 للحالات العادية
        return 2

    def add_visit(self, visit):
        self.visit_history.append(visit)


class EmergencyPatient(Patient):
    def priority_level(self) -> int:
        # أولوية 1 عشان دي طوارئ ومستعجلة
        return 1

    def display_profile(self) -> str:
        # تمييز مريض الطوارئ بوضوح
        return f"{super().display_profile()} | Priority: Emergency (High)"


class RegularPatient(Patient):
    def priority_level(self) -> int:
        # أولوية 2 عادية
        return 2

    def display_profile(self) -> str:
        # تمييز المريض العادي
        return f"{super().display_profile()} | Priority: Regular (Normal)"


class Doctor(Person):
    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        if not validate_doctor_id(person_id):
            raise InvalidFormatError(f"Invalid doctor ID format: '{person_id}'. Expected 'doctor-<number>'")
        super().__init__(person_id, name, phone)
        self.specialty = specialty.strip()
        self.availability = availability

    def display_profile(self) -> str:
        # بروفايل الدكتور وتخصصه وحالة توفره
        status_str = "Available" if self.availability else "Unavailable"
        doc_name = self.name if self.name.lower().startswith("dr.") else f"Dr. {self.name}"
        return f"[{self.person_id}] {doc_name} | Phone: {self.phone} | Specialty: {self.specialty} | Status: [{status_str}]"

    def toggle_availability(self):
        self.availability = not self.availability


class Appointment:
    def __init__(self, patient: Patient, doctor: Doctor, time: datetime, status: str = "pending", fee: float = 0.0):
        self.patient = patient
        self.doctor = doctor
        self.time = time
        self.status = parse_status(status) or "pending"
        self.fee = float(fee)

    def update_status(self, new_status: str):
        """تحديث حالة الكشف بنص عادي بعد الفحص المرن"""
        norm_status = parse_status(new_status)
        if not norm_status:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: pending, completed, cancelled, in_progress")
        self.status = norm_status

    def __str__(self) -> str:
        time_str = self.time.strftime("%Y-%m-%d %H:%M") if isinstance(self.time, datetime) else str(self.time)
        return f"Patient: {self.patient.person_id} | Dr. {self.doctor.name} | Time: {time_str} | Status: {self.status.upper()} | Fee: ${self.fee:.2f}"


# =========================================================
# ITERATOR, CLOSURE & RECURSION
# =========================================================

class WaitingQueueIterator:
    """كاستم إيتريتور للمرور على طابور الانتظار عنصر عنصر"""

    def __init__(self, appointments: list):
        self._appointments = appointments
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._appointments):
            raise StopIteration
        current_appointment = self._appointments[self._index]
        self._index += 1
        return current_appointment


def make_triage_calculator(base_fee: float = 100.0, initial_emergency_count: int = 0):
    """كلوزر لحساب سعر الكشف مع عداد حالات الطوارئ بـ nonlocal"""
    emergency_count = initial_emergency_count

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return float(base_fee * 1.5)  # زيادة 50% لحالات الطوارئ
        return float(base_fee)

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
    """دالة عودية (Recursive) للمرور على سجل الزيارات واستخراج المكتملة فقط بدون استخدام loops"""
    # Base Case: لو وصلنا لنهاية قائمة الزيارات
    if index >= len(visits):
        return []

    # Recursive Step: فحص الزيارة الحالية واستدعاء الدالة على باقي العناصر
    current_visit = visits[index]
    remaining_visits = find_visits_recursive(visits, index + 1)

    if current_visit.status == "completed":
        return [current_visit] + remaining_visits
    return remaining_visits


# =========================================================
# CLINIC MANAGER (MAIN ORCHESTRATOR)
# =========================================================

class ClinicManager:
    """إدارة العيادة بالكامل: المرضى، الدكاترة، المواعيد، التصدير، الكاش، والصلاحيات"""

    def __init__(self, base_fee: float = 100.0):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []
        # booked_date instance attribute مش class attribute مشترك
        self.booked_date: dict[str, list[datetime]] = {}
        self.fee_calculator = make_triage_calculator(base_fee=base_fee)
        # الصلاحيات والتخزين المؤقت للبحث
        self.current_user: User | None = None
        self._visit_lookup_cache: dict[str, list] = {}

    def set_current_user(self, user: User | None):
        """تعيين المستخدم الحالي للتحقق من صلاحياته في العمليات الحساسة"""
        self.current_user = user

    # ---------- ID Generation (randint من 1 لـ 1000) ----------

    def generate_unique_patient_id(self) -> str:
        """توليد ID مريض تلقائي عشوائي من 1 لـ 1000 والتأكد إنه مش متكرر"""
        while True:
            num = random.randint(1, 1000)
            p_id = f"patient-{num}"
            if p_id not in self.patients:
                return p_id

    def generate_unique_doctor_id(self) -> str:
        """توليد ID دكتور تلقائي عشوائي من 1 لـ 1000 والتأكد إنه مش متكرر"""
        while True:
            num = random.randint(1, 1000)
            d_id = f"doctor-{num}"
            if d_id not in self.doctors:
                return d_id

    # ---------- Registration ----------

    def register_patient(self, patient: Patient):
        """تسجيل مريض جديد والتأكد إن رقمه مش متكرر مع فحص الصلاحية"""
        if self.current_user is not None and not self.current_user.has_permission("register_patient"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient.person_id in self.patients:
            raise DuplicateBookingError(f"Patient with ID '{patient.person_id}' already exists")
        self.patients[patient.person_id] = patient
        return patient

    def add_doctor(self, doctor: Doctor):
        """إضافة دكتور جديد للعيادة مع فحص الصلاحية"""
        if self.current_user is not None and not self.current_user.has_permission("add_doctor"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if doctor.person_id in self.doctors:
            raise DuplicateBookingError(f"Doctor with ID '{doctor.person_id}' already exists")
        self.doctors[doctor.person_id] = doctor
        if doctor.person_id not in self.booked_date:
            self.booked_date[doctor.person_id] = []
        return doctor

    def toggle_doctor_availability(self, doctor_id: str) -> bool:
        """تبديل حالة توفر الطبيب (متاح / غير متاح) مع فحص الصلاحية"""
        if self.current_user is not None and not self.current_user.has_permission("toggle_doctor_availability"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor ID '{doctor_id}' not found")
        doc = self.doctors[doctor_id]
        doc.toggle_availability()
        return doc.availability

    # ---------- Appointments ----------

    def book_appointment(self, patient_id: str, doctor_id: str, time):
        """حجز موعد جديد مع منع التكرار والتحقق من التوفر وفحص الصلاحية"""
        if self.current_user is not None and not self.current_user.has_permission("book_appointment"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient ID '{patient_id}' not found")
        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor ID '{doctor_id}' not found")

        # تحويل التاريخ لـ datetime بأمان
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

        # فحص تكرار موعد الدكتور في booked_date الخاص بالـ instance
        if doctor_id not in self.booked_date:
            self.booked_date[doctor_id] = []
        if time in self.booked_date[doctor_id]:
            raise DuplicateBookingError(f"Doctor {doctor_id} already has an appointment at this time")

        # فحص إن المريض نفسه معندوش موعد تاني فنفس التوقيت
        for existing in self.appointments:
            if existing.patient.person_id == patient_id and existing.time == time and existing.status != "cancelled":
                raise DuplicateBookingError(f"Patient {patient_id} already has an appointment at this time")

        target_patient = self.patients[patient_id]
        new_appt = Appointment(target_patient, target_doctor, time, status="pending")
        new_appt.fee = self.fee_calculator(target_patient)

        # حجز الميعاد في booked_date وإضافته للمواعيد
        self.booked_date[doctor_id].append(time)
        self.appointments.append(new_appt)
        target_patient.add_visit(new_appt)

        # إفراغ الكاش الخاص بالمريض لتحديث سجله (Cache Invalidation)
        self._visit_lookup_cache.pop(patient_id, None)

        return new_appt

    def update_visit_status(self, appointment_index: int, new_status: str):
        """تحديث حالة الكشف مع معالجة الإلغاء والتحقق من التعارض عند إعادة التفعيل وفحص الصلاحية"""
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

        # التحقق عند إعادة تفعيل موعد كان ملغي لمنع التعارض إذا تم حجز الموعد لمريض آخر أثناء فترة الإلغاء
        if old_status == "cancelled" and norm_status != "cancelled":
            if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
                raise DuplicateBookingError(
                    f"Cannot reactivate appointment: Dr. {appt.doctor.name} already has another active appointment at this time"
                )
            if doc_id not in self.booked_date:
                self.booked_date[doc_id] = []
            self.booked_date[doc_id].append(appt.time)
        elif norm_status == "cancelled" and old_status != "cancelled":
            # تفريغ الوقت عند الإلغاء
            if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
                self.booked_date[doc_id].remove(appt.time)

        appt.update_status(norm_status)

        # إفراغ الكاش الخاص بالمريض لتحديث سجل زياراته (Cache Invalidation)
        self._visit_lookup_cache.pop(appt.patient.person_id, None)

        return appt

    def delete_appointment(self, appointment_index: int) -> Appointment:
        """حذف موعد محدد من النظام وتحرير وقت الطبيب وتاريخ المريض وتنقيص عداد الطوارئ مع فحص الصلاحية"""
        if self.current_user is not None and not self.current_user.has_permission("delete_appointment"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if appointment_index < 0 or appointment_index >= len(self.appointments):
            raise IndexError(f"Invalid appointment index {appointment_index}")

        appt = self.appointments.pop(appointment_index)

        # تحرير الوقت من booked_date للدكتور لو الموعد مكنش ملغي
        doc_id = appt.doctor.person_id
        if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
            self.booked_date[doc_id].remove(appt.time)

        # إزالة الموعد من سجل زيارات المريض
        if appt in appt.patient.visit_history:
            appt.patient.visit_history.remove(appt)

        # تنقيص عداد حالات الطوارئ في الكلوزر عند حذف موعد طوارئ
        if appt.patient.priority_level() == 1:
            if hasattr(self.fee_calculator, "decrement_emergency_count"):
                self.fee_calculator.decrement_emergency_count()

        # إفراغ الكاش الخاص بالمريض لتحديث سجله (Cache Invalidation)
        self._visit_lookup_cache.pop(appt.patient.person_id, None)

        return appt

    # ---------- Queue / Reports (functional tools) ----------

    def get_emergency_patients(self) -> list[Patient]:
        """فلترة مرضى الطوارئ بـ filter + lambda"""
        emergency = filter(lambda p: p.priority_level() == 1, self.patients.values())
        return list(emergency)

    def sort_queue_by_priority(self) -> list[Appointment]:
        """ترتيب المواعيد بـ sorted + lambda (الطوارئ أولاً)"""
        waiting = [appt for appt in self.appointments if appt.status == "pending"]
        waiting.sort(key=lambda appt: (appt.patient.priority_level(), appt.time))
        return waiting

    def get_waiting_queue_iterator(self) -> WaitingQueueIterator:
        """إرجاع كاستم إيتريتور للمرور على الطابور"""
        waiting = self.sort_queue_by_priority()
        return WaitingQueueIterator(waiting)

    def calculate_total_revenue(self) -> float:
        """حساب إجمالي الأرباح من المواعيد المكتملة فقط بـ reduce"""
        completed_fees = [appt.fee for appt in self.appointments if appt.status == "completed"]
        return float(reduce(lambda total, fee: total + fee, completed_fees, 0.0))

    # ---------- Shared DRY Report Helpers (Feature 1) ----------

    def _compute_report_metrics(self) -> dict:
        """حساب إحصائيات التقرير وتجميعها في قاموس موحد منعاً للتكرار (DRY)"""
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
        """تنسيق جدول التقرير داخل فريم موحد بعرض 56 حرفاً"""
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
        """عرض التقرير اليومي في الكونسول مباشرة"""
        report = self._compute_report_metrics()
        table_str = self._format_report_table(report)
        print("\n" + table_str + "\n")
        return report

    def export_report_to_file(self, path: str = "daily_report.txt") -> bool:
        """تصدير التقرير اليومي إلى ملف نصي بنفس التنسيق مع timestamp ومعالجة الأخطاء بـ try/except"""
        if self.current_user is not None and not self.current_user.has_permission("export_report"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        try:
            report = self._compute_report_metrics()
            ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            table_str = self._format_report_table(report, timestamp=ts_str)

            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(table_str + "\n")

            print(f"\n[SUCCESS] Daily report exported successfully to '{path}'.\n")
            return True
        except Exception as e:
            print(f"\n[ERROR] Failed exporting report to '{path}': {e}\n")
            return False

    # ---------- Recursive & Memoized Patient History (Feature 3) ----------

    def get_patient_completed_visits(self, patient_id: str, return_status: bool = False):
        """استرجاع الزيارات المكتملة للمريض عبر دالة العودية مع التخزين المؤقت (Memoization)"""
        if self.current_user is not None and not self.current_user.has_permission("view_history"):
            raise ClinicError("Access denied. Your role does not permit this action.")

        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient ID '{patient_id}' not found")

        # فحص إذا كانت النتيجة مخزنة مسبقاً في الـ Cache
        if patient_id in self._visit_lookup_cache:
            completed_visits = self._visit_lookup_cache[patient_id]
            is_cache_hit = True
        else:
            # استدعاء الدالة العودية وحفظ النتيجة في الكاش
            patient = self.patients[patient_id]
            completed_visits = find_visits_recursive(patient.visit_history, 0)
            self._visit_lookup_cache[patient_id] = completed_visits
            is_cache_hit = False

        if return_status:
            return completed_visits, is_cache_hit
        return completed_visits

    # ---------- JSON Persistence & Reset ----------

    def save_to_file(self, path: str = "clinic_data.json", silent: bool = False) -> bool:
        """حفظ بيانات العيادة بالكامل في ملف JSON مع دعم الحفظ الصامت التلقائي"""
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
        """استرجاع بيانات العيادة من ملف JSON مع إنشاء الملف تلقائياً والتعامل الآمن مع أسوأ الحالات"""
        initial_data = {"patients": [], "doctors": [], "appointments": []}
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # سيناريو 1: الملف مش موجود خالص -> نعمله فوراً ببيانات نظيفة ونشتغل
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=4)
                print(f"\n[INFO] Database file '{path}' was not found. Created a fresh database file automatically.\n")
            except Exception as e:
                print(f"\n[WARNING] Could not create database file '{path}': {e}. Operating in memory.\n")
            return True

        # سيناريو 2: الملف موجود ولكن ممكن يكون فاضي (0 بايت) أو بايظ / Corrupted
        try:
            if os.path.getsize(path) == 0:
                raise ValueError(f"File '{path}' is empty (0 bytes)")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError(f"Root JSON content in '{path}' must be an object/dict")
        except Exception as e:
            # لو الفايل بايظ: ناخد منه نسخة احتياطية .bak ونعيد إنشاء فايل جديد سليم عشان البرنامج ميقفش أبداً
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
                        fee=fee
                    )
                    self.appointments.append(appt)
                    patient.add_visit(appt)

                    # إعادة بناء booked_date للمواعيد غير الملغاة فقط
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

        # مزامنة عداد الكلوزر مع عدد كشوفات الطوارئ المحفوظة
        loaded_emergency_count = sum(1 for a in self.appointments if a.patient.priority_level() == 1)
        self.fee_calculator = make_triage_calculator(base_fee=100.0, initial_emergency_count=loaded_emergency_count)
        return True

    def reset_database(self, path: str = "clinic_data.json") -> bool:
        """تصفير قاعدة بيانات العيادة بالكامل وحذف كافة السجلات من الذاكرة والملف مع فحص الصلاحية"""
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
    """طباعة عنوان القسم داخل فريم موحد ونظيف بعرض ثابت"""
    print("\n+" + "-" * width + "+")
    print("|" + title.center(width) + "|")
    print("+" + "-" * width + "+")


def action_register_patient(manager: ClinicManager):
    """تسجيل مريض جديد بواسطة موظف العيادة وتوليد ID وحفظه فورياً"""
    print_section_header("REGISTER PATIENT")
    if manager.current_user is not None and not manager.current_user.has_permission("register_patient"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return None

    # نوع المريض (يقبل 1، 2، Regular، Emergency، عادي، طوارئ)
    while True:
        raw_type = input("  Patient Type   (1: Regular, 2: Emergency) [Default: 1]: ").strip()
        p_type = parse_patient_type(raw_type)
        if p_type:
            break
        print("\n[ERROR] Please enter '1' / 'Regular' or '2' / 'Emergency'. Try again.\n")

    p_id = manager.generate_unique_patient_id()

    # الاسم
    while True:
        name = input("  Full Name      [or 'cancel' to exit]: ").strip()
        if name.lower() == "cancel":
            return None
        if name:
            break
        print("\n[ERROR] Patient name cannot be empty. Please try again.\n")

    # رقم التليفون
    while True:
        phone = input("  Phone Number   (11 digits, e.g. 01012345678) [or 'cancel']: ").strip()
        if phone.lower() == "cancel":
            return None
        if not validate_phone(phone):
            print(f"\n[ERROR] Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.\n")
            continue
        break

    # العمر
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
        # حفظ فوري تلقائي
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
    """إضافة طبيب جديد للعيادة وتعيين تخصصه وحالته"""
    print_section_header("ADD DOCTOR")
    if manager.current_user is not None and not manager.current_user.has_permission("add_doctor"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    # كود الدكتور (يقبل إدخال يدوي أو توليد تلقائي بـ randint)
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

    # الاسم
    while True:
        name = input("  Doctor Name    [or 'cancel']: ").strip()
        if name.lower() == "cancel":
            return
        if name:
            break
        print("\n[ERROR] Doctor name cannot be empty. Please try again.\n")

    # رقم التليفون
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
        # حفظ فوري تلقائي
        manager.save_to_file("clinic_data.json", silent=True)
        print(f"\n[SUCCESS] Doctor added successfully!")
        print(f"  Profile: {new_doc.display_profile()}\n")
    except ClinicError as err:
        print(f"\n[ERROR] Failed to add doctor: {err}\n")


def action_book_appointment(manager: ClinicManager):
    """حجز موعد كشف جديد مع الطبيب والتحقق من التعارض والوقت"""
    print_section_header("BOOK APPOINTMENT")
    if manager.current_user is not None and not manager.current_user.has_permission("book_appointment"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.doctors:
        print("\n[ERROR] No doctors available in the clinic. Please add a doctor first.\n")
        return
    if not manager.patients:
        print("\n[ERROR] No patients registered yet. Please register a patient first.\n")
        return

    # عرض قائمة الدكاترة المتاحين باستخدام display_profile()
    print("\nAvailable Doctors in Clinic:")
    print("  " + "-" * 75)
    for d in manager.doctors.values():
        print(f"  * {d.display_profile()}")
    print("  " + "-" * 75 + "\n")

    # اختيار المريض
    while True:
        p_id = input("  Patient ID     (e.g. patient-123) [or 'cancel' to exit]: ").strip()
        if p_id.lower() == "cancel":
            return
        if p_id not in manager.patients:
            print(f"\n[ERROR] Patient ID '{p_id}' not found in system. Please try again.\n")
            continue
        break

    # اختيار الدكتور
    while True:
        d_id = input("  Doctor ID      (e.g. doctor-101)  [or 'cancel' to exit]: ").strip()
        if d_id.lower() == "cancel":
            return
        if d_id not in manager.doctors:
            print(f"\n[ERROR] Doctor ID '{d_id}' not found in system. Please try again.\n")
            continue
        if not manager.doctors[d_id].availability:
            print(f"\n[ERROR] Dr. {manager.doctors[d_id].name} is marked as unavailable. Please choose another doctor.\n")
            continue
        break

    # تحديد الموعد
    while True:
        time_input = input("  Date & Time    (YYYY-MM-DD HH:MM) [or 'cancel' to exit]: ").strip()
        if time_input.lower() == "cancel":
            return
        try:
            appt = manager.book_appointment(p_id, d_id, time_input)
            # حفظ فوري تلقائي
            manager.save_to_file("clinic_data.json", silent=True)
            print(f"\n[SUCCESS] Booked appointment successfully!")
            print(f"   Patient : {appt.patient.name} ({appt.patient.person_id})")
            print(f"   Doctor  : Dr. {appt.doctor.name} ({appt.doctor.person_id})")
            time_disp = appt.time.strftime('%Y-%m-%d %H:%M') if isinstance(appt.time, datetime) else str(appt.time)
            print(f"   Time    : {time_disp}")
            print(f"   Fee     : ${appt.fee:.2f}\n")
            break
        except (InvalidAppointmentTimeError, DuplicateBookingError, ClinicError) as err:
            print(f"\n[ERROR] {err}. Please try again.\n")


def action_update_visit_status(manager: ClinicManager):
    """تحديث حالة موعد كشف (pending / completed / cancelled / in_progress)"""
    print_section_header("UPDATE VISIT STATUS")
    if manager.current_user is not None and not manager.current_user.has_permission("update_visit_status"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.appointments:
        print("\n[INFO] No appointments found in the system.\n")
        return

    print("\nCurrent Appointments:")
    print("  " + "-" * 75)
    for idx, a in enumerate(manager.appointments):
        time_s = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        print(f"  [{idx}] Patient: {a.patient.person_id:<12} | Dr. {a.doctor.name:<15} | Time: {time_s} | Status: {a.status.upper()}")
    print("  " + "-" * 75 + "\n")

    # اختيار رقم الموعد
    while True:
        idx_input = input("  Appointment Index [or 'cancel' to exit]: ").strip()
        if idx_input.lower() == "cancel":
            return
        try:
            idx = int(idx_input)
            if idx < 0 or idx >= len(manager.appointments):
                print(f"\n[ERROR] Index must be between 0 and {len(manager.appointments) - 1}. Please try again.\n")
                continue
            break
        except ValueError:
            print(f"\n[ERROR] '{idx_input}' is not a valid integer. Please try again.\n")

    # اختيار الحالة الجديدة (يقبل نصوص مرنة)
    while True:
        raw_status = input("  New Status (pending / completed / cancelled / in_progress) [or 'cancel']: ").strip()
        if raw_status.lower() == "cancel":
            return
        norm_status = parse_status(raw_status)
        if not norm_status:
            print(f"\n[ERROR] Invalid status '{raw_status}'. Allowed: pending, completed, cancelled, in_progress.\n")
            continue
        try:
            updated = manager.update_visit_status(idx, norm_status)
            # حفظ فوري تلقائي
            manager.save_to_file("clinic_data.json", silent=True)
            print(f"\n[SUCCESS] Updated appointment [{idx}] status to '{updated.status.upper()}'.\n")
            break
        except (ValueError, DuplicateBookingError, ClinicError) as err:
            print(f"\n[ERROR] Update failed: {err}. Please try again.\n")


def action_show_queue(manager: ClinicManager):
    """عرض طابور الانتظار المرتب بالأولوية والوقت بواسطة الكاستم إيتريتور"""
    cols = [
        ('#', 4, '<'),
        ('Priority', 15, '<'),
        ('Patient', 22, '<'),
        ('Doctor', 20, '<'),
        ('Appointment Time', 18, '<'),
        ('Fee', 10, '<'),
    ]
    header_cells = [f"{title:{align}{w}}" for title, w, align in cols]
    header_row = "| " + " | ".join(header_cells) + " |"
    sep_parts = ["-" * (w + 2) for _, w, _ in cols]
    sep = "+" + "+".join(sep_parts) + "+"
    full_w = len(sep) - 2

    print_section_header("WAITING QUEUE (Emergency First, by Priority & Time)", width=full_w)
    print(sep)
    print(header_row)
    print(sep)

    queue_iter = manager.get_waiting_queue_iterator()
    count = 0
    for appt in queue_iter:
        count += 1
        is_emergency = (appt.patient.priority_level() == 1)
        # تمييز صفوف الطوارئ بـ [!] EMERGENCY عشان تبان واضحة ومميزة
        priority_label = "[!] EMERGENCY" if is_emergency else "    REGULAR  "
        p_display = f"{appt.patient.name} ({appt.patient.person_id})"
        d_display = f"Dr. {appt.doctor.name}"
        t_display = appt.time.strftime('%Y-%m-%d %H:%M') if isinstance(appt.time, datetime) else str(appt.time)
        fee_display = f"${appt.fee:.2f}"

        row_cells = [
            f"{str(count):<4}",
            f"{priority_label:<15}",
            f"{p_display:<22}",
            f"{d_display:<20}",
            f"{t_display:<18}",
            f"{fee_display:<10}"
        ]
        print("| " + " | ".join(row_cells) + " |")

    if count == 0:
        empty_msg = "Queue is currently empty (no pending appointments in line)."
        print("| " + empty_msg.ljust(full_w - 2) + " |")

    print(sep + "\n")


def action_toggle_doctor_availability(manager: ClinicManager):
    """تبديل حالة توفر الطبيب (متاح / غير متاح)"""
    print_section_header("TOGGLE DOCTOR AVAILABILITY")
    if manager.current_user is not None and not manager.current_user.has_permission("toggle_doctor_availability"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.doctors:
        print("\n[ERROR] No doctors registered in the clinic yet.\n")
        return

    print("\nCurrent Doctors in Clinic:")
    print("  " + "-" * 75)
    for d in manager.doctors.values():
        print(f"  * {d.display_profile()}")
    print("  " + "-" * 75 + "\n")

    while True:
        d_id = input("  Doctor ID      (e.g. doctor-101)  [or 'cancel' to exit]: ").strip()
        if d_id.lower() == "cancel":
            return
        if d_id not in manager.doctors:
            print(f"\n[ERROR] Doctor ID '{d_id}' not found in clinic. Please try again.\n")
            continue
        try:
            new_avail = manager.toggle_doctor_availability(d_id)
            manager.save_to_file("clinic_data.json", silent=True)
            doc = manager.doctors[d_id]
            status_str = "AVAILABLE" if new_avail else "UNAVAILABLE (Busy)"
            print(f"\n[SUCCESS] Dr. {doc.name} is now marked as {status_str}!")
            print(f"  Updated Profile: {doc.display_profile()}\n")
            break
        except ClinicError as err:
            print(f"\n[ERROR] Failed to toggle doctor availability: {err}\n")
            break


def action_delete_appointment(manager: ClinicManager):
    """حذف موعد محدد من النظام مع تحرير وقت الطبيب وتحديث العدادات"""
    print_section_header("DELETE APPOINTMENT (One Delete Action)")
    if manager.current_user is not None and not manager.current_user.has_permission("delete_appointment"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.appointments:
        print("\n[INFO] No appointments found in the system to delete.\n")
        return

    print("\nCurrent Appointments:")
    print("  " + "-" * 75)
    for idx, a in enumerate(manager.appointments):
        time_s = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        print(f"  [{idx}] Patient: {a.patient.person_id:<12} | Dr. {a.doctor.name:<15} | Time: {time_s} | Status: {a.status.upper()}")
    print("  " + "-" * 75 + "\n")

    while True:
        idx_input = input("  Appointment Index to DELETE [or 'cancel' to exit]: ").strip()
        if idx_input.lower() == "cancel":
            return
        try:
            idx = int(idx_input)
            if idx < 0 or idx >= len(manager.appointments):
                print(f"\n[ERROR] Index must be between 0 and {len(manager.appointments) - 1}. Please try again.\n")
                continue
            confirm = input(f"  Are you sure you want to permanently delete appointment [{idx}]? (yes/no): ").strip().lower()
            if confirm not in ("yes", "y", "نعم", "موافق", "confirm", "تاكيد"):
                print("\n[INFO] Deletion cancelled. Appointment was not deleted.\n")
                return

            deleted = manager.delete_appointment(idx)
            manager.save_to_file("clinic_data.json", silent=True)
            time_disp = deleted.time.strftime('%Y-%m-%d %H:%M') if isinstance(deleted.time, datetime) else str(deleted.time)
            print(f"\n[SUCCESS] Appointment [{idx}] deleted successfully!")
            print(f"  Patient Record : {deleted.patient.display_profile()}")
            print(f"  Doctor Record  : {deleted.doctor.display_profile()}")
            print(f"  Freed Slot     : {time_disp}")
            if deleted.patient.priority_level() == 1:
                rem_emg = manager.fee_calculator.get_emergency_count() if hasattr(manager.fee_calculator, "get_emergency_count") else 0
                print(f"  Emergency Count: Decremented in triage closure (Active: {rem_emg})")
            print()
            break
        except (ValueError, ClinicError) as err:
            print(f"\n[ERROR] Deletion failed: {err}. Please try again.\n")


def action_daily_report(manager: ClinicManager):
    """عرض التقرير اليومي الشامل للعيادة"""
    manager.daily_report()


def action_save_data(manager: ClinicManager):
    """حفظ قاعدة بيانات العيادة إلى ملف JSON"""
    manager.save_to_file("clinic_data.json")


def action_reset_data(manager: ClinicManager):
    """إعادة ضبط قاعدة بيانات العيادة وتصفير كافة السجلات"""
    print_section_header("RESET CLINIC DATA")
    if manager.current_user is not None and not manager.current_user.has_permission("reset_database"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    print("  WARNING: This will permanently delete ALL registered patients,")
    print("  doctors, and scheduled appointments from memory and 'clinic_data.json'.\n")
    confirm = input("  Are you sure you want to reset all clinic data? (yes/no): ").strip().lower()
    if confirm in ("yes", "y", "نعم", "موافق", "confirm", "تاكيد"):
        try:
            manager.reset_database("clinic_data.json")
            print(f"\n[SUCCESS] All clinic data has been reset successfully. Database is now clean.\n")
        except ClinicError as err:
            print(f"\n[ERROR] Reset failed: {err}\n")
    else:
        print(f"\n[INFO] Data reset cancelled. Your existing clinic records are intact.\n")


def action_export_report(manager: ClinicManager):
    """تصدير التقرير اليومي إلى ملف نصي"""
    print_section_header("EXPORT DAILY REPORT")
    if manager.current_user is not None and not manager.current_user.has_permission("export_report"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    export_path = input("  File path to export [Default: 'daily_report.txt'] [or 'cancel']: ").strip()
    if export_path.lower() == "cancel":
        return
    target_path = export_path if export_path else "daily_report.txt"
    try:
        manager.export_report_to_file(target_path)
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


def action_patient_history(manager: ClinicManager):
    """عرض سجل الزيارات المكتملة لمريض عبر دالة العودية والتخزين المؤقت"""
    print_section_header("PATIENT HISTORY (Recursive & Memoized)")
    if manager.current_user is not None and not manager.current_user.has_permission("view_history"):
        print(f"\n[ERROR] Access denied. Your role '{manager.current_user.display_role()}' does not permit this action.\n")
        return

    if not manager.patients:
        print("\n[INFO] No registered patients in system.\n")
        return

    p_id = input("  Patient ID     (e.g. patient-123) [or 'cancel' to exit]: ").strip()
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
                print(f"  {v_idx}. Dr. {v.doctor.name:<16} ({v.doctor.specialty:<12}) | Time: {v_time} | Fee: ${v.fee:.2f}")
        print("  " + "-" * 65)
        print(f"  Total completed visits: {len(completed_visits)}\n")
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


# ---------- Patient Portal Actions (Data-Scoped by patient_id) ----------

def action_view_own_appointments(manager: ClinicManager, patient_id: str):
    """عرض كافة مواعيد المريض الحالي المسجلة في العيادة"""
    print_section_header("MY APPOINTMENTS")
    patient_appts = [a for a in manager.appointments if a.patient.person_id == patient_id]

    if not patient_appts:
        print("\n[INFO] You do not have any scheduled appointments currently.\n")
        return

    print(f"\nAppointments for Patient ID: {patient_id}")
    print("  " + "-" * 75)
    for idx, a in enumerate(patient_appts, 1):
        time_s = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
        print(f"  {idx}. Dr. {a.doctor.name:<15} ({a.doctor.specialty:<12}) | Time: {time_s} | Status: {a.status.upper()} | Fee: ${a.fee:.2f}")
    print("  " + "-" * 75)
    print(f"  Total appointments found: {len(patient_appts)}\n")


def action_view_own_queue_position(manager: ClinicManager, patient_id: str):
    """عرض ترتيب المريض الحالي في طابور الانتظار (Pending) بدقة وفقاً للأولوية"""
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
    p_level = "Emergency (High Priority)" if patient_appt.patient.priority_level() == 1 else "Regular Priority"

    print("\n+" + "=" * 54 + "+")
    print("|" + "YOUR QUEUE STATUS".center(54) + "|")
    print("+" + "=" * 54 + "+")
    pos_badge = f">>> CURRENT QUEUE POSITION: #{position} <<<"
    print("|" + pos_badge.center(54) + "|")
    print("+" + "-" * 54 + "+")
    print(f"|  Doctor        : Dr. {patient_appt.doctor.name:<33} |")
    print(f"|  Time Slot     : {time_s:<35} |")
    print(f"|  Priority      : {p_level:<35} |")
    print(f"|  Total Waiting : {str(len(waiting_queue)):<35} |")
    print("+" + "=" * 54 + "+\n")


def action_view_own_history(manager: ClinicManager, patient_id: str):
    """عرض السجل الطبي وتاريخ الزيارات المكتملة للمريض الحالي مع التخزين المؤقت"""
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
                print(f"  {v_idx}. Dr. {v.doctor.name:<16} ({v.doctor.specialty:<12}) | Time: {v_time} | Fee: ${v.fee:.2f}")
        print("  " + "-" * 65)
        print(f"  Total completed visits: {len(completed_visits)}\n")
    except ClinicError as err:
        print(f"\n[ERROR] {err}\n")


# =========================================================
# MENUS & PORTALS
# =========================================================

def run_staff_menu(manager: ClinicManager, current_user: StaffUser):
    """منيو موظف العيادة (Staff) - 13 خياراً منظماً يشمل الإدارة والتقارير والحفظ"""
    while True:
        menu_title = f"CLINIC MAIN MENU - {current_user.display_role()}"
        print("\n+" + "=" * 54 + "+")
        print("|" + menu_title.center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] Register Patient     : Add new patient record   |")
        print("|  [2] Add Doctor           : Register medical doctor  |")
        print("|  [3] Book Appointment     : Schedule a clinic visit  |")
        print("|  [4] Update Visit Status  : Manage appointment state |")
        print("|  [5] Show Waiting Queue   : View prioritized queue   |")
        print("|  [6] Toggle Doctor Status : Set available / busy     |")
        print("|  [7] Delete Appointment   : Remove record (Delete)   |")
        print("|  [8] Daily Report         : View clinic statistics   |")
        print("|  [9] Save Data Now        : Save database to JSON    |")
        print("|  [10] Reset Clinic Data   : Clear all saved records  |")
        print("|  [11] Export Report       : Save report to .txt file |")
        print("|  [12] Patient History     : Completed visits (memo)  |")
        print("|  [13] Logout / Return     : Back to main screen      |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-13): ").strip()
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
            print("\n" + "-" * 54)
            print(" Saving clinic database before returning to main screen...")
            manager.save_to_file("clinic_data.json", silent=True)
            print("+" + "=" * 54 + "+")
            print("|" + "Logged out successfully!".center(54) + "|")
            print("+" + "=" * 54 + "+\n")
            break
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please choose from 1 to 13 (e.g. '1' or 'Register').\n")


def run_doctor_menu(manager: ClinicManager, current_user: DoctorUser):
    """منيو الطبيب (Doctor) - 5 خيارات مخصصة للعمليات الطبية"""
    while True:
        doc_title = f"DOCTOR PORTAL - {current_user.username}"
        print("\n+" + "=" * 54 + "+")
        print("|" + doc_title.center(54) + "|")
        print("+" + "=" * 54 + "+")
        print("|  [1] Show Waiting Queue   : View prioritized queue   |")
        print("|  [2] Update Visit Status  : Manage appointment state |")
        print("|  [3] Daily Report         : View clinic statistics   |")
        print("|  [4] Patient History     : Completed visits (memo)  |")
        print("|  [5] Logout / Return     : Back to main screen      |")
        print("+" + "-" * 54 + "+")

        raw_choice = input("\nEnter choice (1-5): ").strip().lower()

        if raw_choice in ("1", "queue", "show queue", "show", "طابور"):
            action_show_queue(manager)
        elif raw_choice in ("2", "update", "status", "update status", "تحديث حالة"):
            action_update_visit_status(manager)
        elif raw_choice in ("3", "report", "daily report", "تقرير"):
            action_daily_report(manager)
        elif raw_choice in ("4", "history", "patient history", "completed visits", "سجل"):
            action_patient_history(manager)
        elif raw_choice in ("5", "quit", "exit", "logout", "q", "خروج"):
            print("\n" + "-" * 54)
            print(" Saving clinic database before returning to main screen...")
            manager.save_to_file("clinic_data.json", silent=True)
            print("+" + "=" * 54 + "+")
            print("|" + "Logged out successfully!".center(54) + "|")
            print("+" + "=" * 54 + "+\n")
            break
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please choose from 1 to 5.\n")


def run_patient_portal(manager: ClinicManager, patient_id: str):
    """بوابة استعلام المريض - عرض فقط دون أي إمكانية للتعديل أو الحاجة لكلمة مرور"""
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

        if raw_choice in ("1", "appointments", "my appointments", "مواعيدي"):
            action_view_own_appointments(manager, patient_id)
        elif raw_choice in ("2", "queue", "my queue", "position", "دوري"):
            action_view_own_queue_position(manager, patient_id)
        elif raw_choice in ("3", "history", "my history", "visits", "سجلي"):
            action_view_own_history(manager, patient_id)
        elif raw_choice in ("4", "back", "return", "رجوع", "خروج"):
            print(f"\nGoodbye, {patient.name}!\n")
            return
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please choose from 1 to 4.\n")


def patient_lookup(manager: ClinicManager) -> None:
    """استعلام المريض برقم الـ ID فقط - بدون أي تسجيل دخول أو كلمة مرور"""
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

        # معرف المريض مسجل وصحيح، الدخول المباشر لبوابة الاستعلام
        run_patient_portal(manager, p_id)
        return


def login_screen(manager: ClinicManager) -> User | None:
    """شاشة تسجيل دخول الطاقم الطبي والإداري فقط (Staff / Doctor)"""
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
    """الشاشة الرئيسية: تسجيل دخول الطاقم أو استعلام مريض أو الخروج من النظام"""
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
        elif raw_choice in ("2", "lookup", "patient", "استعلام"):
            patient_lookup(manager)
        elif raw_choice in ("3", "exit", "quit", "q", "خروج"):
            print("\nExiting Smart Clinic Queue System. Goodbye!\n")
            raise SystemExit
        else:
            print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please select 1, 2, or 3.\n")


# =========================================================
# MAIN ENTRY POINT
# =========================================================

def main():
    manager = ClinicManager(base_fee=100.0)

    # 1. تحميل البيانات التلقائي عند بدء التشغيل
    manager.load_from_file("clinic_data.json")

    # 2. حلقة الشاشة الرئيسية المستمرة
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
        manager.save_to_file("clinic_data.json", silent=True)
        print("[SUCCESS] All clinic records saved safely. Goodbye!\n")


if __name__ == "__main__":
    main()
