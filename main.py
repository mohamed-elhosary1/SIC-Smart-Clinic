#------------------- المكتبات -----------------
import json
import os
import random
import re
from functools import reduce
from datetime import datetime, timedelta
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
    if v in ("6", "report", "daily report", "تقرير"):
        return "6"
    if v in ("7", "save", "save data", "حفظ"):
        return "7"
    if v in ("8", "quit", "exit", "q", "خروج"):
        return "8"
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
        return f"{self.person_id} {self.name} {self.phone}"

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
        # بروفايل المريض
        return f"{self.person_id} {self.name} {self.phone} {self.age} {self.case_type}"

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
        # تمييز مريض الطوارئ
        base_profile = super().display_profile()
        return f"{base_profile} high priority"


class RegularPatient(Patient):
    def priority_level(self) -> int:
        # أولوية 2 عادية
        return 2

    def display_profile(self) -> str:
        base_profile = super().display_profile()
        return f"{base_profile} regular priority"


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
        return f"{self.person_id} {self.name} {self.phone} {self.specialty} [{status_str}]"

    def toggle_availability(self):
        self.availability = not self.availability


class Appointment:
    def __init__(self, patient: Patient, doctor: Doctor, time: datetime, status: str = "pending", fee: float = 0.0):
        self.patient = patient
        self.doctor = doctor
        self.time = time
        norm_status = parse_status(status) or status.strip().lower()
        self.status = "pending" if norm_status == "scheduled" else norm_status
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


def make_triage_calculator(base_fee: float = 100.0):
    """كلوزر لحساب سعر الكشف مع عداد حالات الطوارئ بـ nonlocal"""
    emergency_count = 0

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return float(base_fee * 1.5)  # زيادة 50% لحالات الطوارئ
        return float(base_fee)

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
        """تحديث حالة الكشف مع معالجة الإلغاء وتفريغ الوقت المحجوز"""
        if appointment_index < 0 or appointment_index >= len(self.appointments):
            raise IndexError(f"Invalid appointment index {appointment_index}")

        norm_status = parse_status(new_status)
        if not norm_status:
            raise ValueError(f"Invalid visit status '{new_status}'. Allowed: pending, completed, cancelled, in_progress")

        appt = self.appointments[appointment_index]
        old_status = appt.status
        appt.update_status(norm_status)

        # حل مشكلة الإلغاء: لما status يبقى cancelled نشيل الوقت من booked_date للدكتور
        doc_id = appt.doctor.person_id
        if appt.status == "cancelled":
            if doc_id in self.booked_date and appt.time in self.booked_date[doc_id]:
                self.booked_date[doc_id].remove(appt.time)
        elif old_status == "cancelled" and appt.status != "cancelled":
            # لو رجع من ملغي لحالة تانية نعيد حجز الوقت
            if doc_id not in self.booked_date:
                self.booked_date[doc_id] = []
            if appt.time not in self.booked_date[doc_id]:
                self.booked_date[doc_id].append(appt.time)

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
        completed = len([a for a in self.appointments if a.status == "completed"])
        pending = len([a for a in self.appointments if a.status == "pending"])
        cancelled = len([a for a in self.appointments if a.status == "cancelled"])
        in_progress = len([a for a in self.appointments if a.status == "in_progress"])
        revenue = self.calculate_total_revenue()

        report = {
            "total_patients": len(self.patients),
            "total_doctors": len(self.doctors),
            "emergency_patients": emergency_count,
            "completed_visits": completed,
            "pending_visits": pending,
            "cancelled_visits": cancelled,
            "in_progress_visits": in_progress,
            "total_revenue": revenue
        }

        print("\n" + "=" * 45)
        print("          CLINIC DAILY REPORT          ")
        print("=" * 45)
        print(f" Registered Patients: {report['total_patients']}")
        print(f" Registered Doctors : {report['total_doctors']}")
        print(f" Total Appointments : {len(self.appointments)}")
        print(f"   - Pending        : {report['pending_visits']}")
        print(f"   - Completed      : {report['completed_visits']}")
        print(f"   - Cancelled      : {report['cancelled_visits']}")
        print(f"   - In Progress    : {report['in_progress_visits']}")
        print(f" Emergency Cases    : {report['emergency_patients']}")
        print(f" Total Revenue      : ${report['total_revenue']:.2f}")
        print("=" * 45 + "\n")

        return report

    # ---------- JSON Persistence ----------

    def save_to_file(self, path: str = "clinic_data.json") -> bool:
        """حفظ بيانات العيادة بالكامل في ملف JSON"""
        try:
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
            print(f" Success: Clinic data saved to '{path}'.")
            return True
        except Exception as e:
            print(f" Error saving data to '{path}': {e}")
            return False

    def load_from_file(self, path: str = "clinic_data.json") -> bool:
        """استرجاع بيانات العيادة من ملف JSON وإعادة بناء الكائنات والـ booked_date"""
        if not os.path.exists(path):
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f" Error reading '{path}': {e}")
            return False

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
                print(f" Warning: Could not reconstruct patient {p_data}: {e}")

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
                print(f" Warning: Could not reconstruct doctor {d_data}: {e}")

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
                    print(f" Warning: Could not reconstruct appointment {a_data}: {e}")

        print(f" Loaded data successfully from '{path}': {len(self.patients)} Patients, {len(self.doctors)} Doctors, {len(self.appointments)} Appointments.")
        return True


# =========================================================
# INTERACTIVE CLI
# =========================================================

def main():
    manager = ClinicManager(base_fee=100.0)

    print("\n" + "=" * 50)
    print("  WELCOME TO SMART CLINIC QUEUE SYSTEM  ")
    print("=" * 50)

    # محاولة التحميل التلقائي لو الملف موجود
    if not manager.load_from_file("clinic_data.json"):
        print("No existing data file found. Starting with a fresh database.")

    while True:
        print("\n----- MAIN MENU -----")
        print("1. Register patient")
        print("2. Add doctor")
        print("3. Book appointment")
        print("4. Update visit status")
        print("5. Show waiting queue")
        print("6. Daily report")
        print("7. Save data now")
        print("8. Quit (Auto-save)")

        raw_choice = input("\nEnter your choice (1-8): ").strip()
        choice = parse_menu_choice(raw_choice)

        if choice == "1":
            print("\n--- Register Patient ---")
            
            # نوع المريض (يقبل 1، 2، Regular، Emergency، عادي، طوارئ)
            while True:
                raw_type = input("Patient Type (1: Regular, 2: Emergency) [Default: Regular]: ").strip()
                p_type = parse_patient_type(raw_type)
                if p_type:
                    break
                print(" Error: Please enter '1' / 'Regular' or '2' / 'Emergency'. Try again.")

            # توليد ID تلقائي من 1 لـ 1000 باستخدام randint مع التأكد من عدم التكرار
            p_id = manager.generate_unique_patient_id()

            # الاسم
            while True:
                name = input("Full Name [or 'cancel' to exit]: ").strip()
                if name.lower() == "cancel":
                    break
                if name:
                    break
                print(" Error: Name cannot be empty. Please try again.")
            if name.lower() == "cancel":
                continue

            # رقم التليفون
            while True:
                phone = input("Phone (11 digits, e.g. 01012345678) [or 'cancel']: ").strip()
                if phone.lower() == "cancel":
                    break
                if not validate_phone(phone):
                    print(f" Error: Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.")
                    continue
                break
            if phone.lower() == "cancel":
                continue

            # العمر
            while True:
                age_input = input("Age [or 'cancel']: ").strip()
                if age_input.lower() == "cancel":
                    break
                try:
                    age = int(age_input)
                    if age <= 0 or age > 130:
                        raise ValueError
                    break
                except ValueError:
                    print(f" Error: Age must be a valid positive integer (e.g. 25). Got '{age_input}'. Please try again.")
            if age_input.lower() == "cancel":
                continue

            case_type = input("Case description: ").strip()

            try:
                if p_type == "2":
                    new_p = EmergencyPatient(p_id, name, phone, age, case_type)
                else:
                    new_p = RegularPatient(p_id, name, phone, age, case_type)
                manager.register_patient(new_p)
                print("\n" + "-" * 40)
                print(f" Registration Successful!")
                print(f" >>> YOUR ASSIGNED PATIENT ID: {p_id} <<<")
                print(f" Details: {new_p.display_profile()}")
                print("-" * 40)
            except ClinicError as err:
                print(f" Error: {err}")

        elif choice == "2":
            print("\n--- Add Doctor ---")
            
            # كود الدكتور (يقبل إدخال يدوي أو توليد تلقائي بـ randint لو داس Enter)
            while True:
                d_id = input("Doctor ID (Press Enter for auto-generated ID, or type doctor-<num>) [or 'cancel']: ").strip()
                if d_id.lower() == "cancel":
                    break
                if not d_id:
                    d_id = manager.generate_unique_doctor_id()
                    print(f" Generated Doctor ID: {d_id}")
                    break
                if not validate_doctor_id(d_id):
                    print(f" Error: Invalid doctor ID format: '{d_id}'. Expected 'doctor-<number>'. Please try again.")
                    continue
                if d_id in manager.doctors:
                    print(f" Error: Doctor with ID '{d_id}' already exists. Please enter a different ID.")
                    continue
                break
            if d_id.lower() == "cancel":
                continue

            # الاسم
            while True:
                name = input("Doctor Name: ").strip()
                if name:
                    break
                print(" Error: Doctor name cannot be empty. Please try again.")

            # رقم التليفون
            while True:
                phone = input("Phone (11 digits, e.g. 01112345678): ").strip()
                if not validate_phone(phone):
                    print(f" Error: Invalid phone number: '{phone}'. Expected 11 digits starting with 01. Please try again.")
                    continue
                break

            specialty = input("Specialty: ").strip()

            try:
                new_doc = Doctor(d_id, name, phone, specialty)
                manager.add_doctor(new_doc)
                print(f" Success: Added Doctor [{d_id}] - {new_doc.display_profile()}")
            except ClinicError as err:
                print(f" Error: {err}")

        elif choice == "3":
            print("\n--- Book Appointment ---")
            if not manager.doctors:
                print("No doctors available. Please add a doctor first.")
                continue
            if not manager.patients:
                print("No patients registered. Please register a patient first.")
                continue

            print("Available Doctors:")
            for d in manager.doctors.values():
                print(f"  {d.display_profile()}")

            # مريض
            while True:
                p_id = input("Enter Patient ID (e.g. patient-123) [or 'cancel' to exit]: ").strip()
                if p_id.lower() == "cancel":
                    break
                if p_id not in manager.patients:
                    print(f" Error: Patient ID '{p_id}' not found in system. Please try again.")
                    continue
                break
            if p_id.lower() == "cancel":
                continue

            # دكتور
            while True:
                d_id = input("Enter Doctor ID (e.g. doctor-101) [or 'cancel' to exit]: ").strip()
                if d_id.lower() == "cancel":
                    break
                if d_id not in manager.doctors:
                    print(f" Error: Doctor ID '{d_id}' not found in system. Please try again.")
                    continue
                if not manager.doctors[d_id].availability:
                    print(f" Error: Dr. {manager.doctors[d_id].name} is marked as unavailable. Please choose another doctor.")
                    continue
                break
            if d_id.lower() == "cancel":
                continue

            # موعد
            while True:
                time_input = input("Appointment Time (YYYY-MM-DD HH:MM) [or 'cancel' to exit]: ").strip()
                if time_input.lower() == "cancel":
                    break
                try:
                    appt = manager.book_appointment(p_id, d_id, time_input)
                    print(f" Success: Booked appointment!\n   {appt}")
                    break
                except (InvalidAppointmentTimeError, DuplicateBookingError, ClinicError) as err:
                    print(f" Error: {err}. Please try again.")

        elif choice == "4":
            print("\n--- Update Visit Status ---")
            if not manager.appointments:
                print("No appointments found.")
                continue

            for idx, a in enumerate(manager.appointments):
                print(f"[{idx}] {a}")

            # اختيار رقم الموعد
            while True:
                idx_input = input("Enter appointment index to update [or 'cancel' to exit]: ").strip()
                if idx_input.lower() == "cancel":
                    break
                try:
                    idx = int(idx_input)
                    if idx < 0 or idx >= len(manager.appointments):
                        print(f" Error: Index must be between 0 and {len(manager.appointments) - 1}. Please try again.")
                        continue
                    break
                except ValueError:
                    print(f" Error: '{idx_input}' is not a valid number. Please try again.")
            if idx_input.lower() == "cancel":
                continue

            # اختيار الحالة الجديدة (يقبل نصوص مرنة)
            while True:
                raw_status = input("Enter new status (pending / completed / cancelled / in_progress) [or 'cancel']: ").strip()
                if raw_status.lower() == "cancel":
                    break
                norm_status = parse_status(raw_status)
                if not norm_status:
                    print(f" Error: Invalid status '{raw_status}'. Allowed: pending, completed, cancelled, in_progress. Please try again.")
                    continue
                try:
                    updated = manager.update_visit_status(idx, norm_status)
                    print(f" Success: Updated appointment [{idx}] to '{updated.status.upper()}'")
                    break
                except ValueError as err:
                    print(f" Error: {err}. Please try again.")

        elif choice == "5":
            print("\n--- Waiting Queue (Priority Sorted: Emergency First) ---")
            queue_iter = manager.get_waiting_queue_iterator()
            count = 0
            for appt in queue_iter:
                count += 1
                priority_label = "EMERGENCY" if appt.patient.priority_level() == 1 else "REGULAR"
                print(f"{count}. [{priority_label}] Patient: {appt.patient.name} ({appt.patient.person_id}) | "
                      f"Dr. {appt.doctor.name} | Time: {appt.time.strftime('%Y-%m-%d %H:%M')} | Fee: ${appt.fee:.2f}")
            if count == 0:
                print("Queue is currently empty (no pending appointments).")

        elif choice == "6":
            manager.daily_report()

        elif choice == "7":
            manager.save_to_file("clinic_data.json")

        elif choice == "8":
            print("\nSaving data before exit...")
            manager.save_to_file("clinic_data.json")
            print("Thank you for using Smart Clinic Queue System. Goodbye!\n")
            break

        else:
            print(f" Invalid choice '{raw_choice}'. Please choose from 1 to 8 (e.g. '1' or 'Register').")


if __name__ == "__main__":
    main()