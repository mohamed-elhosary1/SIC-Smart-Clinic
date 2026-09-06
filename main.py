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
# EXCEPTIONS
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
# REGEX VALIDATORS
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
    """قبول الاختيارات من المنيو كرقم أو ككلمة"""
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
    if v in ("11", "quit", "exit", "q", "خروج"):
        return "11"
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
# ITERATOR & CLOSURE
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

    def reset_count():
        nonlocal emergency_count
        emergency_count = 0

    calculate.get_emergency_count = get_emergency_count
    calculate.reset_count = reset_count
    return calculate


# =========================================================
# CLINIC MANAGER (MAIN ORCHESTRATOR)
# =========================================================

class ClinicManager:
    """إدارة العيادة بالكامل: المرضى، الدكاترة، المواعيد، الحفظ والاسترجاع"""

    def __init__(self, base_fee: float = 100.0):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []
        # booked_date instance attribute مش class attribute مشترك
        self.booked_date: dict[str, list[datetime]] = {}
        self.fee_calculator = make_triage_calculator(base_fee=base_fee)

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
        """تسجيل مريض جديد والتأكد إن رقمه مش متكرر"""
        if patient.person_id in self.patients:
            raise DuplicateBookingError(f"Patient with ID '{patient.person_id}' already exists")
        self.patients[patient.person_id] = patient
        return patient

    def add_doctor(self, doctor: Doctor):
        """إضافة دكتور جديد للعيادة"""
        if doctor.person_id in self.doctors:
            raise DuplicateBookingError(f"Doctor with ID '{doctor.person_id}' already exists")
        self.doctors[doctor.person_id] = doctor
        if doctor.person_id not in self.booked_date:
            self.booked_date[doctor.person_id] = []
        return doctor

    def toggle_doctor_availability(self, doctor_id: str) -> bool:
        """تبديل حالة توفر الطبيب (متاح / غير متاح)"""
        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor ID '{doctor_id}' not found")
        doc = self.doctors[doctor_id]
        doc.toggle_availability()
        return doc.availability

    # ---------- Appointments ----------

    def book_appointment(self, patient_id: str, doctor_id: str, time):
        """حجز موعد جديد مع منع التكرار والتحقق من التوفر"""
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
        return new_appt

    def update_visit_status(self, appointment_index: int, new_status: str):
        """تحديث حالة الكشف مع معالجة الإلغاء وتفريغ الوقت المحجوز والتحقق من التعارض عند إعادة التفعيل"""
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
        return appt

    def delete_appointment(self, appointment_index: int) -> Appointment:
        """حذف موعد محدد من النظام وتحرير وقت الطبيب وتاريخ المريض (One Delete Action)"""
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

    def daily_report(self) -> dict:
        """تقرير يومي بإحصائيات العيادة"""
        emergency_count = len(self.get_emergency_patients())
        closure_count = self.fee_calculator.get_emergency_count() if hasattr(self.fee_calculator, "get_emergency_count") else 0
        completed = len([a for a in self.appointments if a.status == "completed"])
        pending = len([a for a in self.appointments if a.status == "pending"])
        cancelled = len([a for a in self.appointments if a.status == "cancelled"])
        in_progress = len([a for a in self.appointments if a.status == "in_progress"])
        revenue = self.calculate_total_revenue()

        report = {
            "total_patients": len(self.patients),
            "total_doctors": len(self.doctors),
            "emergency_patients": emergency_count,
            "emergency_fees_calculated": closure_count,
            "completed_visits": completed,
            "pending_visits": pending,
            "cancelled_visits": cancelled,
            "in_progress_visits": in_progress,
            "total_revenue": revenue
        }

        # عرض التقرير في frame منظم بعرض موحد 56 حرف ومحاذاة الأرقام يمين والتسميات شمال
        border = "+" + "=" * 54 + "+"
        mid_sep = "+" + "-" * 39 + "+" + "-" * 14 + "+"

        print("\n" + border)
        print("|" + "CLINIC DAILY REPORT".center(54) + "|")
        print(border)
        lbl_h, val_h = "Metric Description", "Count / Sum"
        print(f"| {lbl_h:<37} | {val_h:>12} |")
        print(mid_sep)

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
            print(f"| {m_label:<37} | {m_val:>12} |")

        print(mid_sep)
        rev_str = f"${report['total_revenue']:.2f}"
        rev_label = "Total Revenue Collected"
        print(f"| {rev_label:<37} | {rev_str:>12} |")
        print(border + "\n")

        return report

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
        """تصفير قاعدة بيانات العيادة بالكامل وحذف كافة السجلات من الذاكرة والملف"""
        self.patients.clear()
        self.doctors.clear()
        self.appointments.clear()
        self.booked_date.clear()
        if hasattr(self.fee_calculator, "reset_count"):
            self.fee_calculator.reset_count()
        return self.save_to_file(path, silent=True)


# =========================================================
# INTERACTIVE CLI
# =========================================================

def print_section_header(title: str, width: int = 54):
    """طباعة عنوان القسم داخل فريم موحد ونظيف بعرض ثابت"""
    print("\n+" + "-" * width + "+")
    print("|" + title.center(width) + "|")
    print("+" + "-" * width + "+")


def main():
    manager = ClinicManager(base_fee=100.0)

    # رسالة الترحيب في بداية البرنامج
    print("\n+" + "=" * 54 + "+")
    print("|" + "WELCOME TO SMART CLINIC QUEUE SYSTEM".center(54) + "|")
    print("|" + "Samsung Innovation Campus".center(54) + "|")
    print("+" + "=" * 54 + "+")

    # تحميل تلقائي موثوق عند بدء التشغيل (مع إنشاء الملف فوراً لو مش موجود ومعالجة أي تلف)
    manager.load_from_file("clinic_data.json")

    try:
        while True:
            # المنيو الرئيسية في فريم منظم وأيقونات نصية آمنة (بدون مشاكل ترميز)
            print("\n+" + "=" * 54 + "+")
            print("|" + "CLINIC MAIN MENU".center(54) + "|")
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
            print("|  [11] Quit (Auto-Save)    : Save data and exit       |")
            print("+" + "-" * 54 + "+")

            raw_choice = input("\nEnter choice (1-11): ").strip()
            choice = parse_menu_choice(raw_choice)

            if choice == "1":
                print_section_header("REGISTER PATIENT")
                
                # نوع المريض (يقبل 1، 2، Regular، Emergency، عادي، طوارئ)
                while True:
                    raw_type = input("  Patient Type   (1: Regular, 2: Emergency) [Default: 1]: ").strip()
                    p_type = parse_patient_type(raw_type)
                    if p_type:
                        break
                    print("\n[ERROR] Please enter '1' / 'Regular' or '2' / 'Emergency'. Try again.\n")

                # توليد ID تلقائي من 1 لـ 1000 باستخدام randint مع التأكد من عدم التكرار
                p_id = manager.generate_unique_patient_id()

                # الاسم
                while True:
                    name = input("  Full Name      [or 'cancel' to exit]: ").strip()
                    if name.lower() == "cancel":
                        break
                    if name:
                        break
                    print("\n[ERROR] Patient name cannot be empty. Please try again.\n")
                if name.lower() == "cancel":
                    continue

                # رقم التليفون
                while True:
                    phone = input("  Phone Number   (11 digits, e.g. 01012345678) [or 'cancel']: ").strip()
                    if phone.lower() == "cancel":
                        break
                    if not validate_phone(phone):
                        print(f"\n[ERROR] Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.\n")
                        continue
                    break
                if phone.lower() == "cancel":
                    continue

                # العمر
                while True:
                    age_input = input("  Patient Age    [or 'cancel']: ").strip()
                    if age_input.lower() == "cancel":
                        break
                    try:
                        age = int(age_input)
                        if age <= 0 or age > 130:
                            raise ValueError
                        break
                    except ValueError:
                        print(f"\n[ERROR] Age must be a valid positive integer between 1 and 130. Got '{age_input}'. Please try again.\n")
                if age_input.lower() == "cancel":
                    continue

                case_type = input("  Diagnosis/Case [or 'cancel']: ").strip()
                if case_type.lower() == "cancel":
                    continue

                try:
                    if p_type == "2":
                        new_p = EmergencyPatient(p_id, name, phone, age, case_type)
                    else:
                        new_p = RegularPatient(p_id, name, phone, age, case_type)
                    manager.register_patient(new_p)
                    # حفظ فوري تلقائي لضمان عدم ضياع أي بيانات تحت أي ظرف
                    manager.save_to_file("clinic_data.json", silent=True)
                    
                    # كارت بيانات التسجيل بنجاح مع إبراز الـ ID التلقائي
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
                except ClinicError as err:
                    print(f"\n[ERROR] Registration failed: {err}\n")

            elif choice == "2":
                print_section_header("ADD DOCTOR")
                
                # كود الدكتور (يقبل إدخال يدوي أو توليد تلقائي بـ randint لو داس Enter)
                while True:
                    d_id = input("  Doctor ID      (Press Enter for auto-id, or doctor-<num>) [or 'cancel']: ").strip()
                    if d_id.lower() == "cancel":
                        break
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
                if d_id.lower() == "cancel":
                    continue

                # الاسم
                while True:
                    name = input("  Doctor Name    [or 'cancel']: ").strip()
                    if name.lower() == "cancel":
                        break
                    if name:
                        break
                    print("\n[ERROR] Doctor name cannot be empty. Please try again.\n")
                if name.lower() == "cancel":
                    continue

                # رقم التليفون
                while True:
                    phone = input("  Phone Number   (11 digits, e.g. 01112345678) [or 'cancel']: ").strip()
                    if phone.lower() == "cancel":
                        break
                    if not validate_phone(phone):
                        print(f"\n[ERROR] Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.\n")
                        continue
                    break
                if phone.lower() == "cancel":
                    continue

                specialty = input("  Specialty      [or 'cancel']: ").strip()
                if specialty.lower() == "cancel":
                    continue

                try:
                    new_doc = Doctor(d_id, name, phone, specialty)
                    manager.add_doctor(new_doc)
                    # حفظ فوري تلقائي
                    manager.save_to_file("clinic_data.json", silent=True)
                    print(f"\n[SUCCESS] Doctor added successfully!")
                    print(f"  Profile: {new_doc.display_profile()}\n")
                except ClinicError as err:
                    print(f"\n[ERROR] Failed to add doctor: {err}\n")

            elif choice == "3":
                print_section_header("BOOK APPOINTMENT")
                if not manager.doctors:
                    print("\n[ERROR] No doctors available in the clinic. Please add a doctor first.\n")
                    continue
                if not manager.patients:
                    print("\n[ERROR] No patients registered yet. Please register a patient first.\n")
                    continue

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
                        break
                    if p_id not in manager.patients:
                        print(f"\n[ERROR] Patient ID '{p_id}' not found in system. Please try again.\n")
                        continue
                    break
                if p_id.lower() == "cancel":
                    continue

                # اختيار الدكتور
                while True:
                    d_id = input("  Doctor ID      (e.g. doctor-101)  [or 'cancel' to exit]: ").strip()
                    if d_id.lower() == "cancel":
                        break
                    if d_id not in manager.doctors:
                        print(f"\n[ERROR] Doctor ID '{d_id}' not found in system. Please try again.\n")
                        continue
                    if not manager.doctors[d_id].availability:
                        print(f"\n[ERROR] Dr. {manager.doctors[d_id].name} is marked as unavailable. Please choose another doctor.\n")
                        continue
                    break
                if d_id.lower() == "cancel":
                    continue

                # تحديد الموعد
                while True:
                    time_input = input("  Date & Time    (YYYY-MM-DD HH:MM) [or 'cancel' to exit]: ").strip()
                    if time_input.lower() == "cancel":
                        break
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

            elif choice == "4":
                print_section_header("UPDATE VISIT STATUS")
                if not manager.appointments:
                    print("\n[INFO] No appointments found in the system.\n")
                    continue

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
                        break
                    try:
                        idx = int(idx_input)
                        if idx < 0 or idx >= len(manager.appointments):
                            print(f"\n[ERROR] Index must be between 0 and {len(manager.appointments) - 1}. Please try again.\n")
                            continue
                        break
                    except ValueError:
                        print(f"\n[ERROR] '{idx_input}' is not a valid integer. Please try again.\n")
                if idx_input.lower() == "cancel":
                    continue

                # اختيار الحالة الجديدة (يقبل نصوص مرنة)
                while True:
                    raw_status = input("  New Status (pending / completed / cancelled / in_progress) [or 'cancel']: ").strip()
                    if raw_status.lower() == "cancel":
                        break
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
                    except (ValueError, DuplicateBookingError) as err:
                        print(f"\n[ERROR] Update failed: {err}. Please try again.\n")

            elif choice == "5":
                # قائمة انتظار المرضى في جدول منظم بمحاذاة ثابتة وتمييز حالات الطوارئ
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

            elif choice == "6":
                print_section_header("TOGGLE DOCTOR AVAILABILITY")
                if not manager.doctors:
                    print("\n[ERROR] No doctors registered in the clinic yet.\n")
                    continue

                print("\nCurrent Doctors in Clinic:")
                print("  " + "-" * 75)
                for d in manager.doctors.values():
                    print(f"  * {d.display_profile()}")
                print("  " + "-" * 75 + "\n")

                while True:
                    d_id = input("  Doctor ID      (e.g. doctor-101)  [or 'cancel' to exit]: ").strip()
                    if d_id.lower() == "cancel":
                        break
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

            elif choice == "7":
                print_section_header("DELETE APPOINTMENT (One Delete Action)")
                if not manager.appointments:
                    print("\n[INFO] No appointments found in the system to delete.\n")
                    continue

                print("\nCurrent Appointments:")
                print("  " + "-" * 75)
                for idx, a in enumerate(manager.appointments):
                    time_s = a.time.strftime("%Y-%m-%d %H:%M") if isinstance(a.time, datetime) else str(a.time)
                    print(f"  [{idx}] Patient: {a.patient.person_id:<12} | Dr. {a.doctor.name:<15} | Time: {time_s} | Status: {a.status.upper()}")
                print("  " + "-" * 75 + "\n")

                while True:
                    idx_input = input("  Appointment Index to DELETE [or 'cancel' to exit]: ").strip()
                    if idx_input.lower() == "cancel":
                        break
                    try:
                        idx = int(idx_input)
                        if idx < 0 or idx >= len(manager.appointments):
                            print(f"\n[ERROR] Index must be between 0 and {len(manager.appointments) - 1}. Please try again.\n")
                            continue
                        confirm = input(f"  Are you sure you want to permanently delete appointment [{idx}]? (yes/no): ").strip().lower()
                        if confirm not in ("yes", "y", "نعم", "موافق", "confirm", "تاكيد"):
                            print("\n[INFO] Deletion cancelled. Appointment was not deleted.\n")
                            break

                        deleted = manager.delete_appointment(idx)
                        manager.save_to_file("clinic_data.json", silent=True)
                        time_disp = deleted.time.strftime('%Y-%m-%d %H:%M') if isinstance(deleted.time, datetime) else str(deleted.time)
                        print(f"\n[SUCCESS] Appointment [{idx}] deleted successfully!")
                        print(f"  Patient Record : {deleted.patient.display_profile()}")
                        print(f"  Doctor Record  : {deleted.doctor.display_profile()}")
                        print(f"  Freed Slot     : {time_disp}\n")
                        break
                    except ValueError:
                        print(f"\n[ERROR] '{idx_input}' is not a valid integer. Please try again.\n")

            elif choice == "8":
                manager.daily_report()

            elif choice == "9":
                manager.save_to_file("clinic_data.json")

            elif choice == "10":
                print_section_header("RESET CLINIC DATA")
                print("  WARNING: This will permanently delete ALL registered patients,")
                print("  doctors, and scheduled appointments from memory and 'clinic_data.json'.\n")
                confirm = input("  Are you sure you want to reset all clinic data? (yes/no): ").strip().lower()
                if confirm in ("yes", "y", "نعم", "موافق", "confirm", "تاكيد"):
                    manager.reset_database("clinic_data.json")
                    print(f"\n[SUCCESS] All clinic data has been reset successfully. Database is now clean.\n")
                else:
                    print(f"\n[INFO] Data reset cancelled. Your existing clinic records are intact.\n")

            elif choice == "11":
                print("\n" + "-" * 54)
                print(" Saving clinic database before exiting...")
                manager.save_to_file("clinic_data.json", silent=True)
                print("+" + "=" * 54 + "+")
                print("|" + "Thank you for using Smart Clinic Queue System!".center(54) + "|")
                print("|" + "Data saved successfully. Goodbye!".center(54) + "|")
                print("+" + "=" * 54 + "+\n")
                break

            else:
                print(f"\n[ERROR] Invalid choice '{raw_choice}'. Please choose from 1 to 11 (e.g. '1' or 'Register').\n")

    except (KeyboardInterrupt, SystemExit):
        print("\n\n[INFO] Program interrupted. Auto-saving clinic database before exit...")
        manager.save_to_file("clinic_data.json", silent=True)
        print("[SUCCESS] All clinic records saved safely. Goodbye!\n")


if __name__ == "__main__":
    main()