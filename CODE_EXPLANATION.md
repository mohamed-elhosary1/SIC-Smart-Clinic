# الدليل التشريحي الشامل والتحليل التنفيذي لنظام العيادة الذكية (Smart Clinic Queue System)

هذا المستند يقدم شرحاً تشريحياً حرفياً متكاملاً لكود ملف `main.py` سطرًا بسطر، وبالترتيب الفعلي الذي يتم فيه تنفيذ الكود في الذاكرة (Runtime / Run Order) من لحظة تشغيل البرنامج وحتى إغلاقه.

---

## فهرس المحتويات
1. [آلية بدء البرنامج وترتيب التنفيذ في الذاكرة (Runtime Architecture)](#1-آلية-بدء-البرنامج-وترتيب-التنفيذ-في-الذاكرة)
2. [المرحلة الأولى: تحميل الموديول وبناء الهياكل البرمجية (Module Loading Phase)](#2-المرحلة-الأولى-تحميل-الموديول-وبناء-الهياكل-البرمجية)
   - [المكتبات والاستدعاءات (Imports)](#المكتبات-والاستدعاءات-imports)
   - [نظام الاستثناءات المخصصة (Custom Exceptions)](#نظام-الاستثناءات-المخصصة-custom-exceptions)
   - [نظام الصلاحيات والمستخدمين (RBAC Architecture)](#نظام-الصلاحيات-والمستخدمين-rbac-architecture)
   - [أدوات التحقق بالـ Regex ودوال المرونة (Validators & Parsers)](#أدوات-التحقق-بالـ-regex-ودوال-المرونة)
   - [نماذج بيانات النظام البرمجية (OOP Domain Models)](#نماذج-بيانات-النظام-البرمجية-oop-domain-models)
   - [الأدوات المتقدمة: الإيتريتور، الكلوزر، والعودية (Iterator, Closure & Recursion)](#الأدوات-المتقدمة-الإيتريتور-الكلوزر-والعودية)
   - [كلاس المايسترو التنفيذي (ClinicManager)](#كلاس-المايسترو-التنفيذي-clinicmanager)
3. [المرحلة الثانية: بدء التشغيل الفعلي وسيناريو التفاعل الكامل (Execution & CLI Lifecycle)](#3-المرحلة-الثانية-بدء-التشغيل-الفعلي-وسيناريو-التفاعل-الكامل)
   - [نقطة الانطلاق (Entry Point)](#نقطة-الانطلاق-entry-point)
   - [داخل دالة main() خطوة بخطوة](#داخل-دالة-main-خطوة-بخطوة)
   - [تتبع الخيارات الـ 13 بالتفصيل الممل](#تتبع-الخيارات-الـ-13-بالتفصيل-الممل)
4. [المخطط التنفيذي الشامل (Full Execution Trace: START → END)](#4-المخطط-التنفيذي-الشامل-full-execution-trace)
5. [جدول العناصر البرمجية الشامل (Complete Reference Table)](#5-جدول-العناصر-البرمجية-الشامل)
6. [قصة عمل البرنامج المتكاملة (The System Story)](#6-قصة-عمل-البرنامج-المتكاملة)

---

## 1. آلية بدء البرنامج وترتيب التنفيذ في الذاكرة

عند تنفيذ الأمر `python main.py`، يمر مفسر بايثون (Python Interpreter) بمرحلتين أساسيتين:

1. **مرحلة التحميل والتعريف (Module Loading & Definition Phase):**
   * يقرأ بايثون الملف تسلسلياً من السطر 1 حتى السطر الأخير.
   * يقوم بتنفيذ أسطر `import` لحجز مساحات للمكتبات في الذاكرة.
   * عند المرور على كلمة `class`، يُنشئ بايثون **Class Object** في الذاكرة ويربط دواله به كـ Attributes.
   * عند المرور على كلمة `def`، يُنشئ بايثون **Function Object** ويخزن الكود الداخلي كـ Bytecode جاهز للتنفيذ دون الدخول فيه الآن.
   * يقوم بتجميع تعبيرات الـ Regex وإنشاء القواميس العامة مثل `USERS_DB`.

2. **مرحلة التشغيل الفعلي (Execution Phase):**
   * يصل المفسر إلى السطر 1479 ويجد شرط: `if __name__ == "__main__":`.
   * نظراً لتشغيل الملف كبرنامج رئيسي، تكون قيمة `__name__` هي `"__main__"`، فيتحقق الشرط ويتم استدعاء `main()`.
   * تبدأ حينها رحلة البرنامج التفاعلية من حجز كائن العيادة، تسجيل الدخول، تحميل قاعدة البيانات، وتشغيل حلقة القائمة الرئيسية.

---

## 2. المرحلة الأولى: تحميل الموديول وبناء الهياكل البرمجية

### المكتبات والاستدعاءات (Imports)

#### السطر 2:
```python
import json
```
* **ماذا يحدث؟** يستورد موديول `json` القياسي ويحمله في الـ Memory تحت المرجع `json`.
* **لماذا؟** لتسجيل واسترجاع بيانات العيادة (المرضى، الأطباء، الكشوفات) من وإلى ملف بصيغة مهيكلة `clinic_data.json`.
* **البيانات:** كود المكتبة المدمجة في بايثون.
* **النتيجة:** Module Object في جدول الرموز العام (Global Symbol Table).
* **بعده:** ينتقل للسطر 3.

#### السطر 3:
```python
import os
```
* **ماذا يحدث؟** يستورد موديول التعامل مع نظام التشغيل والمسارات `os`.
* **لماذا؟** للتحقق من وجود الملفات (`os.path.exists`)، معرفة حجم الملف (`os.path.getsize`) لمنع قراءة ملفات فارغة، وإنشاء المجلدات (`os.makedirs`).
* **النتيجة:** Module Object باسم `os`.
* **بعده:** ينتقل للسطر 4.

#### السطر 4:
```python
import random
```
* **ماذا يحدث؟** يستورد موديول توليد الأرقام العشوائية `random`.
* **لماذا؟** لتوليد معرفات (IDs) فريدة وتلقائية للمرضى والأطباء عبر `random.randint(1, 1000)`.
* **النتيجة:** Module Object باسم `random`.
* **بعده:** ينتقل للسطر 5.

#### السطر 5:
```python
import re
```
* **ماذا يحدث؟** يستورد مكتبة التعبيرات النمطية (Regular Expressions) `re`.
* **لماذا؟** للتحقق الصارم من صحة صياغة أرقام الهواتف ومعرفات المرضى والأطباء.
* **النتيجة:** Module Object باسم `re`.
* **بعده:** ينتقل للسطر 6.

#### السطر 6:
```python
import shutil
```
* **ماذا يحدث؟** يستورد موديول العمليات المتقدمة على الملفات `shutil`.
* **لماذا؟** لعمل نسخة احتياطية فورية (`.bak`) من قاعدة البيانات عند اكتشاف أي تلف في ملف الـ JSON لضمان عدم ضياع بيانات العيادة.
* **النتيجة:** Module Object باسم `shutil`.
* **بعده:** ينتقل للسطر 7.

#### السطر 7:
```python
from functools import reduce
```
* **ماذا يحدث؟** يستورد دالة `reduce` تحديداً من موديول `functools`.
* **لماذا؟** لحساب إجمالي الإيرادات المالية من المواعيد المكتملة عبر تجميع رسوم الكشوفات في قيمة رقمية تراكمية واحدة (Functional Programming).
* **النتيجة:** تسجيل مؤشر دالة `reduce` في النطاق العام.
* **بعده:** ينتقل للسطر 8.

#### السطر 8:
```python
from datetime import datetime
```
* **ماذا يحدث؟** يستورد كلاس `datetime` لإدارة التواريخ والأوقات.
* **لماذا؟** لجدولة المواعيد، التحقق من أن الموعد في المستقبل، تسجيل الـ Timestamp في التقارير المصدرة، والتحويل بين النصوص وكائنات التاريخ.
* **النتيجة:** تسجيل الكلاس `datetime` في الـ Globals.
* **بعده:** ينتقل للسطر 14.

---

### نظام الاستثناءات المخصصة (Custom Exceptions)

#### الأسطر 14 - 41:
```python
class ClinicError(Exception):
    pass

class InvalidAppointmentTimeError(ClinicError):
    pass

class DuplicateBookingError(ClinicError):
    pass

class PatientNotFoundError(ClinicError):
    pass

class DoctorNotFoundError(ClinicError):
    pass

class InvalidFormatError(ClinicError):
    pass
```
* **ماذا يحدث؟** يُنشئ بايثون ستة كلاسات استثناء في الذاكرة. الكلاس الأب هو `ClinicError` (يرث من `Exception`)، والخمسة الآخرون يرثون منه.
* **لماذا؟** لبناء هرمية أخطاء مخصصة (Custom Exception Hierarchy) تمكننا من:
  1. اصطياد أخطاء معينة بدقة مثل `DuplicateBookingError` لمعالجة تضارب المواعيد.
  2. اصطياد كافة أخطاء النظام بكود موحد عبر `except ClinicError:`.
  3. حماية البرنامج من الانهيار المفاجئ وعزل أخطاء النظام عن أخطاء لغة بايثون العامة.
* **بعده:** ينتقل للسطر 48.

---

### نظام الصلاحيات والمستخدمين (RBAC Architecture)

#### الأسطر 48 - 63: كلاس `User` (Base Class)
```python
class User:
    def __init__(self, username: str, password: str, allowed_actions: set):
        self.username = username
        self.password = password
        self.allowed_actions = allowed_actions

    def has_permission(self, action: str) -> bool:
        return action in self.allowed_actions

    def display_role(self) -> str:
        return "Generic User"
```
* **ما هو؟** الكلاس الأب المجرد لجميع مستخدمي النظام.
* **الـ Attributes:**
  * `self.username`: اسم المستخدم (String).
  * `self.password`: كلمة المرور (String).
  * `self.allowed_actions`: مجموعة نصوص (`set`) بأسماء العمليات المسموح بها، وتتميز بالبحث فائق السرعة $O(1)$.
* **الـ Methods:**
  * `has_permission(action)`: تفحص هل العملية موجودة في مجموعة الصلاحيات وترجع `True` أو `False`.
  * `display_role()`: ترجع مسمى الدور الوظيفي للمستخدم.
* **بعده:** ينتقل للسطر 65.

#### الأسطر 65 - 76: كلاس `AdminUser(User)`
```python
class AdminUser(User):
    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=set())

    def has_permission(self, action: str) -> bool:
        return True

    def display_role(self) -> str:
        return "Administrator"
```
* **ماذا يمثل؟** مدير النظام (Administrator).
* **البوليمورفيزم (Polymorphism):** تم عمل Override لميثود `has_permission` لترجع دائماً وبشكل مطلق `True`، مما يمنحه كامل الصلاحيات دون استثناء (حذف، تصفير، حجز، تعديل، تصدير).
* **بعده:** ينتقل للسطر 79.

#### الأسطر 79 - 98: كلاس `ReceptionistUser(User)`
```python
class ReceptionistUser(User):
    RECEPTIONIST_ACTIONS = {
        "register_patient", "add_doctor", "book_appointment",
        "update_visit_status", "view_queue", "toggle_doctor_availability",
        "view_history", "export_report",
    }

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=self.RECEPTIONIST_ACTIONS)

    def display_role(self) -> str:
        return "Receptionist"
```
* **ماذا يمثل؟** موظف الاستقبال (Receptionist).
* **الصلاحيات:** يمتلك صلاحيات العمليات اليومية التشغيلية فقط، وممنوع تماماً من العمليات الحساسة التدميرية (`delete_appointment` و `reset_database`).
* **بعده:** ينتقل للسطر 100.

#### الأسطر 100 - 114: كلاس `DoctorUser(User)`
```python
class DoctorUser(User):
    DOCTOR_ACTIONS = {"view_queue", "update_visit_status", "view_history"}

    def __init__(self, username: str, password: str):
        super().__init__(username, password, allowed_actions=self.DOCTOR_ACTIONS)

    def display_role(self) -> str:
        return "Doctor"
```
* **ماذا يمثل؟** الطبيب (Doctor).
* **الصلاحيات:** مسموح له فقط بمعاينة طابور الانتظار، تحديث حالة الكشف إلى مكتمل، واستعراض تاريخ المريض.
* **بعده:** ينتقل للسطر 117.

#### الأسطر 117 - 130: قاعدة بيانات المستخدمين `USERS_DB`
```python
USERS_DB: dict[str, dict] = {
    "admin": {
        "password": "admin123",
        "factory": lambda u, p: AdminUser(u, p),
    },
    "receptionist": {
        "password": "recep123",
        "factory": lambda u, p: ReceptionistUser(u, p),
    },
    "doctor": {
        "password": "doc123",
        "factory": lambda u, p: DoctorUser(u, p),
    },
}
```
* **ماذا يحدث في الذاكرة؟** يُنشأ قاموس ثابت في النطاق العام يربط اسم المستخدم بكلمة سره ودالة مصنع مجهولة (`lambda factory`) تُنشئ كائن المستخدم المناسب فور تسجيل الدخول.
* **بعده:** ينتقل للسطر 133.

#### الأسطر 133 - 165: دوال تسجيل الدخول (`authenticate` و `login_screen`)
* **`authenticate(username, password)` (الأسطر 133 - 139):**
  * تنظف اسم المستخدم بـ `.strip().lower()` ليكون غير حساس لحالة الأحرف.
  * تبحث في `USERS_DB.get(u_key)`. لو الحساب غير موجود أو الباسورد خطأ، ترفع `ClinicError("Invalid credentials...")`.
  * لو سليم، تستدعي دالة المصنع `factory` وتنتج كائن المستخدم المطلوب.
* **`login_screen()` (الأسطر 142 - 165):**
  * تدير حلقة إدخال تفاعلية `while True` تعرض الحسابات الافتراضية، تستقبل البيانات، وتصطاد أي خطأ وتكرر المحاولة حتى ينجح تسجيل الدخول، ثم ترجع كائن المستخدم المسجل.
* **بعده:** ينتقل للسطر 172.

---

### أدوات التحقق بالـ Regex ودوال المرونة

#### الأسطر 172 - 190: تجميع الأنماط ودوال الفحص
```python
PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")
PHONE_PATTERN = re.compile(r"01[0-9]{9}")

def validate_patient_id(patient_id: str) -> bool:
    return bool(PATIENT_ID_PATTERN.fullmatch(patient_id.strip()))

def validate_doctor_id(doctor_id: str) -> bool:
    return bool(DOCTOR_ID_PATTERN.fullmatch(doctor_id.strip()))

def validate_phone(phone: str) -> bool:
    return bool(PHONE_PATTERN.fullmatch(phone.strip()))
```
* **التجميع المسبق (`re.compile`):** يحول النصوص النمطية إلى كائنات C-Level في الذاكرة لسرعة الفحص دون إعادة تفسيرها في كل استدعاء.
* **الأنماط:**
  * معرف المريض: يبدأ بـ `patient-` ويتبعه رقم واحد على الأقل.
  * معرف الطبيب: يبدأ بـ `doctor-` ويتبعه رقم واحد على الأقل.
  * رقم الهاتف: يبدأ بـ `01` ويتبعه 9 أرقام بالضبط (إجمالي 11 رقماً وهو نمط الهاتف المصري).
* **بعده:** ينتقل للسطر 197.

#### الأسطر 197 - 249: دوال التحليل النصي المرن (Parsers)
* **`parse_patient_type(val)`:** تقبل `"1"` أو `"regular"` أو `"عادي"` للمريض العادي، و `"2"` أو `"emergency"` أو `"طوارئ"` لمريض الطوارئ.
* **`parse_status(val)`:** تقبل الحالات بمختلف صيغها وترجع الصيغة المعيارية (`"pending"`, `"completed"`, `"cancelled"`, `"in_progress"`).
* **`parse_menu_choice(val)`:** تدعم إدخال أرقام الخيارات من 1 إلى 13، أو الكلمات الدلالية المقابلة لها (مثل `"export"` و `"تصدير"` للخيار 12، أو `"history"` للخيار 13).
* **بعده:** ينتقل للسطر 256.

---

### نماذج بيانات النظام البرمجية (OOP Domain Models)

#### الأسطر 256 - 271: كلاس `Person` (Base Class)
```python
class Person:
    def __init__(self, person_id: str, name: str, phone: str):
        if not validate_phone(phone):
            raise InvalidFormatError(f"Invalid phone number '{phone}'. Must be 11 digits starting with 01.")
        self.person_id = person_id.strip()
        self.name = name.strip()
        self.phone = phone.strip()

    def display_profile(self) -> str:
        return f"[{self.person_id}] {self.name} | Phone: {self.phone}"

    def __str__(self) -> str:
        return self.display_profile()
```
* **الوظيفة:** يمثل الكيان البشري الأساسي في العيادة.
* **التحقق الفوري:** يفحص رقم الهاتف في `__init__` فوراً؛ إذا لم يكن 11 رقماً تبدأ بـ 01 يرفع `InvalidFormatError` لمنع وجود كائن غير صالح في الذاكرة.
* **بعده:** ينتقل للسطر 273.

#### الأسطر 273 - 291: كلاس `Patient(Person)`
```python
class Patient(Person):
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
        return 2

    def add_visit(self, visit):
        self.visit_history.append(visit)
```
* **الوراثة والسمات:** يرث من `Person`، ويضيف `age` (العمر)، `case_type` (التشخيص)، و `visit_history` (قائمة كشوفات المريض).
* **الـ Methods:** `priority_level()` ترجع الأولوية الافتراضية (2)، و `add_visit()` تضيف كشفاً جديداً لسجله.
* **بعده:** ينتقل للسطر 294.

#### الأسطر 294 - 312: كلاسات المرضى المتخصصة
* **`EmergencyPatient(Patient)`:**
  * تعيد تعريف `priority_level()` لترجع `1` (أولوية قصوى للحالات الحرجة).
  * تعيد تعريف `display_profile()` لإضافة وسم `Priority: Emergency (High)`.
* **`RegularPatient(Patient)`:**
  * تحافظ على أولوية `2` العادية وتطبع وسم `Priority: Regular (Normal)`.
* **بعده:** ينتقل للسطر 314.

#### الأسطر 314 - 330: كلاس `Doctor(Person)`
```python
class Doctor(Person):
    def __init__(self, person_id: str, name: str, phone: str, specialty: str, availability: bool = True):
        if not validate_doctor_id(person_id):
            raise InvalidFormatError(f"Invalid doctor ID format: '{person_id}'. Expected 'doctor-<number>'")
        super().__init__(person_id, name, phone)
        self.specialty = specialty.strip()
        self.availability = availability

    def display_profile(self) -> str:
        status_str = "Available" if self.availability else "Unavailable"
        doc_name = self.name if self.name.lower().startswith("dr.") else f"Dr. {self.name}"
        return f"[{self.person_id}] {doc_name} | Phone: {self.phone} | Specialty: {self.specialty} | Status: [{status_str}]"

    def toggle_availability(self):
        self.availability = not self.availability
```
* **السمات:** `specialty` (التخصص)، و `availability` (هل الطبيب متاح لاستقبال المرضى أم مشغول).
* **الميثودز:** `toggle_availability()` لتبديل حالة التوفر منطقياً بـ `not`.
* **بعده:** ينتقل للسطر 332.

#### الأسطر 332 - 350: كلاس `Appointment`
* يربط بين كائن مريض وكائن طبيب وموعد `datetime` وحالة كشف ورسوم مالية.
* يحتوي على ميثود `update_status(new_status)` لتغيير حالة الكشف نصياً، وميثود `__str__` لتنسيق الموعد عند الطباعة.
* **بعده:** ينتقل للسطر 356.

---

### الأدوات المتقدمة: الإيتريتور، الكلوزر، والعودية

#### الأسطر 356 - 371: كلاس `WaitingQueueIterator` (Custom Iterator)
```python
class WaitingQueueIterator:
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
```
* **التطبيق الهندسي:** يطبق بروتوكول التكرار في بايثون (`__iter__` و `__next__`).
* **الآلية:** يتحرك على عناصر القائمة عبر مؤشر `_index`. إذا وصل للنهاية يرفع `StopIteration`، مما يسمح باستخدامه مباشرة داخل حلقات `for` للمرور على طابور الانتظار عنصرًا تلو الآخر.
* **بعده:** ينتقل للسطر 374.

#### الأسطر 374 - 401: دالة `make_triage_calculator` (Closure with `nonlocal`)
```python
def make_triage_calculator(base_fee: float = 100.0, initial_emergency_count: int = 0):
    emergency_count = initial_emergency_count

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return float(base_fee * 1.5)
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
```
* **المفهوم البرمجي للـ Closure:**
  * دالة حاضنة تحتفظ بمتغير محلي `emergency_count`.
  * الدوال الداخلية تحتفظ بالوصول إلى هذا المتغير في الذاكرة حتى بعد خروج الدالة الخارجية من مكدس الاستدعاءات (Call Stack).
  * كلمة `nonlocal` تسمح بتعديل المتغير الأصلي في النطاق الأب.
* **الدوال الملحقة (Function Attributes):**
  * `calculate(patient)`: تزيد عداد الطوارئ بحالة الطوارئ وتحسب الرسوم بزيادة 50% ($150.0) أو السعر العادي ($100.0).
  * `get_emergency_count()`: ترجع العدد الحالي لحالات الطوارئ.
  * `decrement_emergency_count()`: تنقص العداد بمقدار 1 عند حذف كشف طوارئ لضمان دقة الحسابات.
  * `reset_count()`: تصفير العداد عند تصفير العيادة.
* **بعده:** ينتقل للسطر 404.

#### الأسطر 404 - 416: دالة `find_visits_recursive` (Pure Recursion)
```python
def find_visits_recursive(visits: list, index: int = 0) -> list:
    if index >= len(visits):
        return []

    current_visit = visits[index]
    remaining_visits = find_visits_recursive(visits, index + 1)

    if current_visit.status == "completed":
        return [current_visit] + remaining_visits
    return remaining_visits
```
* **المفهوم:** دالة عودية نقية لاستخراج المواعيد المكتملة بدون أي استخدام لحلقات التكرار (`for` أو `while`).
* **حالة التوقف (Base Case):** عندما يتجاوز الـ Index طول القائمة `index >= len(visits)`، ترجع قائمة فارغة `[]` ويبدأ الارتداد العكسي.
* **الخطوة العودية (Recursive Step):** تفحص الموعد الحالي؛ إذا كان مكتملًا تضيفه إلى ناتج استدعاء نفسها على باقي العناصر `[current_visit] + remaining_visits`.
* **بعده:** ينتقل للسطر 423.

---

### كلاس المايسترو التنفيذي `ClinicManager`

#### الأسطر 423 - 439: التهيئة والسمات
* **`self.patients`:** قاموس `{patient_id: Patient}` للبحث السريع $O(1)$.
* **`self.doctors`:** قاموس `{doctor_id: Doctor}`.
* **`self.appointments`:** قائمة بجميع كائنات `Appointment`.
* **`self.booked_date`:** قاموس `{doctor_id: [datetime]}` يسجل المواعيد المحجوزة لكل طبيب لمنع التضارب.
* **`self.fee_calculator`:** كائن الكلوزر لحساب الأسعار وتتبع الطوارئ.
* **`self.current_user`:** كائن المستخدم الحالي لتطبيق صلاحيات الـ RBAC.
* **`self._visit_lookup_cache`:** قاموس التخزين المؤقت للبحث العودي (Memoization Cache).

#### الأسطر 443 - 613: العمليات التشغيلية المحمية بالصلاحيات
* **`register_patient` و `add_doctor` و `toggle_doctor_availability`:**
  * تفحص أولاً صلاحية المستخدم الحالي عبر `self.current_user.has_permission(...)`.
  * تمنع التكرار وتخزن الكائنات في القواميس.
* **`book_appointment`:**
  * تفحص الصلاحية ووجود المريض والطبيب.
  * تتأكد أن التاريخ والوقت في المستقبل.
  * تتأكد أن الطبيب متاح (`availability == True`).
  * تمنع حجز الطبيب في نفس الوقت وتمنع حجز المريض لموعدين في نفس الوقت.
  * تحسب الرسوم بالكلوزر وتضيف الحجز لقوائم المواعيد وسجل المريض.
  * **إبطال الكاش (Cache Invalidation):** تحذف كاش المريض فوراً `self._visit_lookup_cache.pop(patient_id, None)`.
* **`update_visit_status`:**
  * تفحص الصلاحية وتغير حالة الكشف.
  * تعالج تحرير وقت الطبيب عند الإلغاء، أو إعادة حجز الموعد إذا أُعيد تفعيله بعد التأكد من عدم شغله لمريض آخر.
  * تبطل كاش المريض فوراً.
* **`delete_appointment`:**
  * محصورة بالأدمن فقط.
  * تحذف الموعد، تحرر وقت الطبيب، تحذفه من سجل المريض، **وتنقص عداد الطوارئ في الكلوزر تلقائياً إذا كان المريض حالة طوارئ**، وتبطل الكاش.

#### الأسطر 617 - 636: الأدوات الوظيفية (Functional Tools)
* **`get_emergency_patients()`:** فلترة بـ `filter(lambda p: p.priority_level() == 1, self.patients.values())`.
* **`sort_queue_by_priority()`:** ترتيب بـ `sorted` بمفتاح مركب `(priority, time)` ليأتي مرضى الطوارئ أولاً، ثم الأقدم حجزاً.
* **`get_waiting_queue_iterator()`:** تغليف القائمة المرتبة داخل كائن `WaitingQueueIterator`.
* **`calculate_total_revenue()`:** تجميع إجمالي رسوم الكشوفات المكتملة بـ `reduce`.

#### الأسطر 640 - 728: ميزة تصدير التقرير ومبدأ DRY (Feature 1)
* **`_compute_report_metrics()`:** تجمع كافة إحصائيات النظام في قاموس موحد منعاً لتكرار الكود.
* **`_format_report_table(report, timestamp=None)`:** تنسق جدول التقرير داخل فريم بعرض 56 حرفاً مع إضافة الـ Timestamp.
* **`daily_report()`:** تطبع التقرير في الكونسول مباشرة.
* **`export_report_to_file(path="daily_report.txt")`:** تفحص الصلاحية، تولد الـ Timestamp الحالي، وتكتب الجدول في ملف نصي مع معالجة الأخطاء بكتلة `try/except` وطباعة `[SUCCESS]` أو `[ERROR]`.

#### الأسطر 732 - 753: سجل المريض العودي المخزن مؤقتاً (Feature 3: Memoization)
* **`get_patient_completed_visits(patient_id, return_status=False)`:**
  * تفحص صلاحية `"view_history"`.
  * **فحص الكاش:** إذا كان المريض مسجلاً في `self._visit_lookup_cache`، ترجع النتيجة فوراً بـ $O(1)$ مع وسم `is_cache_hit = True`.
  * **في حال عدم وجوده:** تستدعي الدالة العودية `find_visits_recursive`، تحفظ النتيجة في الكاش، وترجعها مع وسم `is_cache_hit = False`.

#### الأسطر 757 - 946: التخزين الدائم والاسترداد التلقائي (JSON Persistence)
* **`save_to_file(path, silent=False)`:** حفظ كامل قاعدة البيانات في ملف JSON مع دعم اللغة العربية.
* **`load_from_file(path)`:**
  * لو الملف غير موجود: تنشئه تلقائياً بهيكل فارغ نظيف.
  * لو الملف تالف أو فارغ: تأخذ منه نسخة احتياطية `.bak` وتنشئ ملفاً جديداً لضمان عدم توقف النظام أبداً.
  * تعيد بناء كافة الكائنات في الذاكرة مع إعادة بناء جدول أوقات الأطباء ومزامنة عداد الطوارئ في الكلوزر.
* **`reset_database(path)`:** تفحص صلاحية الأدمن، وتصفر الذاكرة والملف بالكامل.

---

## 3. المرحلة الثانية: بدء التشغيل الفعلي وسيناريو التفاعل الكامل

### نقطة الانطلاق (Entry Point)

#### الأسطر 1479 - 1481:
```python
if __name__ == "__main__":
    main()
```
* بايثون يتحقق من المتغير الخاص `__name__`، ويجد قيمته مساوية لـ `"__main__"` لأن الملف تم تشغيله كبرنامج رئيسي، فيبدأ فوراً في تنفيذ دالة `main()`.

---

### داخل دالة `main()` خطوة بخطوة

1. **السطر 961: تهيئة مدير العيادة:**
   ```python
   manager = ClinicManager(base_fee=100.0)
   ```
   يُنشأ كائن `ClinicManager` في الذاكرة ويجهز القواميس وقوائم المواعيد ومصنع الكلوزر.

2. **الأسطر 964 - 965: تسجيل الدخول وتثبيت الصلاحيات:**
   ```python
   current_user = login_screen()
   manager.set_current_user(current_user)
   ```
   * يُطلب اسم المستخدم وكلمة المرور من الكونسول.
   * يتم التحقق واسترجاع كائن المستخدم المناسب (`AdminUser` أو `ReceptionistUser` أو `DoctorUser`).
   * يتم ربط الكائن بمدير النظام طوال الجلسة لضبط الصلاحيات.

3. **السطر 968: استرجاع البيانات المحفوظة:**
   ```python
   manager.load_from_file("clinic_data.json")
   ```
   يتم تحميل البيانات من القرص الصلب إلى الذاكرة ومزامنة العدادات تلقائياً.

4. **الأسطر 970 - 1472: حلقة القائمة الرئيسية `while True`:**
   * يعرض رأس القائمة دور المستخدم الحالي: `menu_title = f"CLINIC MAIN MENU - {current_user.display_role()}"`.
   * تُطبع الخيارات الـ 13 بالتفصيل.
   * يستقبل البرنامج إدخال المستخدم ويمرره لـ `parse_menu_choice`.

---

### تتبع الخيارات الـ 13 بالتفصيل الممل

* **[1] تسجيل مريض (Register Patient):**
  يفحص صلاحية `"register_patient"`، يستقبل نوع المريض (1 عادي، 2 طوارئ)، الاسم، الهاتف (11 رقماً تبدأ بـ 01)، العمر، والتشخيص. يولد المعرف تلقائياً، ينشئ كائن المريض، يحفظه في الـ JSON، ويطبع كارت المريض المنسق.
* **[2] إضافة طبيب (Add Doctor):**
  يفحص صلاحية `"add_doctor"`، يستقبل المعرف أو يولده تلقائياً، الاسم، الهاتف، والتخصص، وينشئ كائن الطبيب ويحفظه في الـ JSON.
* **[3] حجز موعد (Book Appointment):**
  يفحص صلاحية `"book_appointment"`، يعرض الأطباء المتاحين بملفاتهم الشخصية `display_profile()`، يستقبل بيانات الحجز، يتحقق من التوفر وعدم التعارض، يحسب الرسوم بالكلوزر، يبطل كاش المريض، ويحفظ البيانات.
* **[4] تحديث حالة الكشف (Update Visit Status):**
  يفحص الصلاحية، يستقبل رقم الموعد والحالة الجديدة، يغير الحالة، يحرر أو يحجز وقت الطبيب، ويبطل كاش المريض.
* **[5] عرض طابور الانتظار (Show Waiting Queue):**
  يستخرج كائن `WaitingQueueIterator` لطابور الحالات المنتظرة مرتبة بالأولوية والوقت، ويمر عليها بحلقة `for` مع تمييز حالات الطوارئ بـ `[!] EMERGENCY`.
* **[6] تبديل حالة الطبيب (Toggle Doctor Status):**
  يفحص الصلاحية، ويعكس حالة توفر الطبيب بين متاح ومشغول.
* **[7] حذف موعد (Delete Appointment):**
  مسموح للأدمن فقط ومرفوض لغيره. يطلب تأكيد الحذف، يحذف الكشف، يحرر موعد الطبيب، يمسح الكشف من سجل المريض، **وينقص عداد الطوارئ في الكلوزر تلقائياً إذا كان طوارئ**، ويبطل الكاش.
* **[8] التقرير اليومي (Daily Report):**
  يحسب الإحصائيات ويطبع جدول التقرير اليومي والإيرادات المالية في الكونسول.
* **[9] حفظ البيانات الآن (Save Data Now):**
  يكتب كافة البيانات الحالية في ملف `clinic_data.json`.
* **[10] تصفير بيانات العيادة (Reset Clinic Data):**
  للأدمن فقط. يطلب تأكيداً صريحاً، ويقوم بمسح كافة السجلات من الذاكرة والملف وتصفير عداد الكلوزر والكاش.
* **[11] الخروج مع الحفظ التلقائي (Quit):**
  يحفظ قاعدة البيانات تلقائياً، يطبع رسالة وداع، ويكسر الحلقة بـ `break`.
* **[12] تصدير التقرير إلى ملف نصي (Export Daily Report):**
  يفحص الصلاحية، يستقبل مسار الملف (افتراضياً `daily_report.txt`)، وينشئ الملف متضمناً الـ Timestamp والجدول المنسق بدقة.
* **[13] استعراض تاريخ المريض مع التخزين المؤقت (Patient History):**
  يفحص الصلاحية، يستقبل ID المريض، ويستدعي `get_patient_completed_visits` لطباعة الكشوفات المكتملة فقط مع إظهار `[CACHE HIT]` أو `[COMPUTED]`.
* **الحماية من المقاطعة الفجائية (Interrupt Protection):**
  إذا ضغط المستخدم `Ctrl + C` في أي وقت، تصطاد كتلة `except (KeyboardInterrupt, SystemExit):` الحدث وتقوم بحفظ البيانات تلقائياً قبل الخروج لمنع ضياع أي ملفات.

---

## 4. المخطط التنفيذي الشامل (Full Execution Trace)

```
[START: تشغيل البرنامج]
   │
   ▼
[تحميل واستيراد المكتبات: json, os, random, re, shutil, functools.reduce, datetime]
   │
   ▼
[بناء هرمية الاستثناءات في الذاكرة: ClinicError ومشتقاتها الخمسة]
   │
   ▼
[بناء نظام الصلاحيات: User, AdminUser, ReceptionistUser, DoctorUser, USERS_DB]
   │
   ▼
[تجميع أنماط Regex وحفظ دوال التحقق ودوال تحليل المدخلات]
   │
   ▼
[بناء نماذج البيانات: Person, Patient, EmergencyPatient, RegularPatient, Doctor, Appointment]
   │
   ▼
[بناء الأدوات المتقدمة: WaitingQueueIterator, make_triage_calculator, find_visits_recursive]
   │
   ▼
[بناء كلاس ClinicManager بكافة دواله الإدارية والتقارير والكاش والملفات]
   │
   ▼
[التحقق من شرط __name__ == '__main__' -> استدعاء main()]
   │
   ▼
[داخل main: إنشاء كائن manager = ClinicManager(100.0)]
   │
   ▼
[استدعاء login_screen() -> التحقق من المستخدم وتعيين الصلاحيات عبر set_current_user]
   │
   ▼
[استدعاء manager.load_from_file('clinic_data.json') -> استرجاع البيانات ومزامنة العدادات]
   │
   ▼
[دخول حلقة while True -> طباعة القائمة الرئيسية مع عرض الدور الوظيفي للمستخدم]
   │
   ├─► اختيار [1 - 4]: إدارة المرضى، الأطباء، والمواعيد مع الحفظ التلقائي وإبطال الكاش.
   ├─► اختيار [5 - 6]: عرض الطابور عبر الإيتريتور أو تبديل توفر الأطباء.
   ├─► اختيار [7]: حذف موعد مع تحرير الوقت وتنقيص عداد الطوارئ في الكلوزر (Admin فقط).
   ├─► اختيار [8 - 10]: التقارير، الحفظ اليدوي، أو تصفير البيانات (Admin فقط).
   ├─► اختيار [12]: تصدير التقرير لملف نصي بـ Timestamp عبر دالة export_report_to_file.
   ├─► اختيار [13]: استعراض زيارات المريض المكتملة بالدالة العودية مع التخزين المؤقت (Cache Hit/Computed).
   └─► اختيار [11]: الحفظ التلقائي للبيانات والخروج النظيف من البرنامج بـ break.
   │
   ▼
[END: إنهاء البرنامج بسلام وحفظ كامل البيانات]
```

---

## 5. جدول العناصر البرمجية الشامل

| العنصر البرمجي | النوع | مكانه في الكود | وظيفته الهندسية | البيانات التي يستقبلها | مصدر البيانات | ماذا ينتج / يرجع |
|---|---|---|---|---|---|---|
| `ClinicError` | Exception Class | أسطر 14-16 | الكلاس الأساسي لجميع استثناءات العيادة | رسالة الخطأ | المبرمج عند الرفع | كائن استثناء |
| `User` | Base Class | أسطر 48-63 | تمثيل المستخدم وإدارة الصلاحيات | `username, password, allowed_actions` | كلاسات الأبناء | كائن مستخدم أساسي |
| `AdminUser` | Subclass | أسطر 65-76 | تمثيل مدير النظام بصلاحيات مطلقة | `username, password` | دالة التحقق | كائن أدمن |
| `ReceptionistUser` | Subclass | أسطر 79-98 | تمثيل موظف الاستقبال بصلاحيات تشغيلية | `username, password` | دالة التحقق | كائن موظف استقبال |
| `DoctorUser` | Subclass | أسطر 100-114 | تمثيل الطبيب بصلاحيات معاينة وتحديث | `username, password` | دالة التحقق | كائن طبيب مستخدم |
| `USERS_DB` | Global Dict | أسطر 117-130 | قاعدة بيانات الحسابات المدمجة | بيانات الحسابات والمصانع | ثابتة في الكود | قاموس الحسابات |
| `authenticate` | Function | أسطر 133-139 | فحص بيانات الدخول واستخراج كائن المستخدم | `username, password` | شاشة الدخول | كائن `User` مشتق |
| `login_screen` | Function | أسطر 142-165 | واجهة تسجيل الدخول التفاعلية مع التكرار | مدخلات الكونسول | المستخدم | كائن المستخدم المسجل |
| `validate_phone` | Function | أسطر 187-189 | فحص صحة الموبايل المصري عبر Regex | `phone: str` | واجهة المستخدم | `bool` (True / False) |
| `Person` | Base Class | أسطر 256-271 | تمثيل الكائن البشري (اسم، هاتف، كود) | `person_id, name, phone` | كلاسات المرضى والأطباء | كائن شخص أساسي |
| `Patient` | Subclass | أسطر 273-291 | تمثيل المريض مع سجل الزيارات والأولوية | `id, name, phone, age, case` | كلاسات المرضى الفرعية | كائن مريض |
| `EmergencyPatient` | Subclass | أسطر 294-302 | مريض طوارئ بأولوية قصوى (1) | نفس مدخلات المريض | واجهة التسجيل | كائن مريض طوارئ |
| `RegularPatient` | Subclass | أسطر 304-312 | مريض عادي بأولوية عادية (2) | نفس مدخلات المريض | واجهة التسجيل | كائن مريض عادي |
| `Doctor` | Subclass | أسطر 314-330 | تمثيل الطبيب والتخصص وتوفر العمل | `id, name, phone, spec, avail` | واجهة إضافة الأطباء | كائن طبيب |
| `Appointment` | Class | أسطر 332-350 | ربط المريض بالطبيب والوقت والحالة والرسوم | `patient, doc, time, status, fee` | دالة الحجز | كائن كشف طبي |
| `WaitingQueueIterator`| Iterator Class| أسطر 356-371 | المرور التكراري المخصص على الطابور | قائمة المواعيد مرتبة | `ClinicManager` | كشف تلو الآخر عبر `next` |
| `make_triage_calculator`| Closure Func | أسطر 374-401 | حساب الرسوم وحفظ وتعديل عداد الطوارئ | `base_fee, initial_emergency` | `ClinicManager` | دالة `calculate` بالعداد |
| `find_visits_recursive`| Recursive Func| أسطر 404-416 | استخراج الكشوفات المكتملة عودياً بدون loops | `visits: list, index: int` | ميثود تاريخ المريض | قائمة الكشوفات المكتملة |
| `ClinicManager` | Manager Class | أسطر 423-948 | إدارة النظام وقواعد البيانات والكاش والتقارير | `base_fee: float` | دالة `main()` | كائن المدير التنفيذي |
| `_visit_lookup_cache`| Instance Dict| سطر 435 | التخزين المؤقت لنتائج البحث (Memoization) | نتائج استعلامات الزيارات | الدالة العودية | كاش الزيارات $O(1)$ |
| `main` | Main Function | أسطر 960-1472| تشغيل دورة حياة التطبيق والقائمة التفاعلية | لا يوجد | مفسر بايثون عند التشغيل | إنهاء البرنامج بنجاح |

---

## 6. قصة عمل البرنامج المتكاملة

1. **الاستيقاظ والتهيئة في الذاكرة:**
   يبدأ البرنامج بتجهيز نفسه في الذاكرة فور الضغط على زر التشغيل؛ يستدعي مكتبات التعامل مع البيانات والوقت والملفات، يجمع أنماط الـ Regex لتسريع فحص البيانات لاحقاً، ويبني قوالب الكلاسات للهيكل البرمجي ونظام الصلاحيات.
2. **شاشة الدخول والمصادقة الأمنية:**
   يستقبل البرنامج المستخدم بشاشة تسجيل دخول تطالبه باسم المستخدم وكلمة المرور. بمجرد إدخال البيانات (مثل `receptionist` و `recep123`)، يتحقق النظام من صحتها، ويحدد رتبة المستخدم ويثبت صلاحياته في جلسة العمل.
3. **استرجاع الذاكرة الدائمة (Auto-Recovery):**
   يتوجه البرنامج إلى ملف `clinic_data.json` ليقرأ قاعدة البيانات؛ وإذا وجد الملف مفقوداً ينشئه فوراً بهيكل سليم، وإذا وجده تالفاً يأخذ منه نسخة احتياطية `.bak` ويبدأ بملف جديد حتى لا يتعطل العمل في أسوأ الظروف.
4. **تفاعل يوم العمل بالعيادة:**
   تفتح القائمة الرئيسية معلنة دور المستخدم الحالي في رأسها.
   - يسجل موظف الاستقبال مريض طوارئ، فيفحص الـ Regex هاتفه المصري، ويولد له معرفاً فريداً، ويمنحه أولوية قصوى.
   - عند حجز موعد مع طبيب متاح، يستدعي البرنامج دالة الكلوزر لحساب السعر تلقائياً مع زيادة 50% لحالات الطوارئ ($150.0)، ويمنع أي تضارب زمني.
   - عند طلب عرض الطابور عبر الخيار [5]، يرتب البرنامج المرضى واضعاً حالات الطوارئ أولاً لإنقاذ المريض، ثم يستعرضهم الإيتريتور خطوة بخطوة مع وسم `[!] EMERGENCY`.
   - عند طلب سجل المريض عبر الخيار [13]، تنطلق الدالة العودية لفلترة الزيارات المكتملة بدون أي حلقات `for` أو `while`، وتخزن النتيجة في الكاش (`[COMPUTED]`). وإذا طُلب السجل مرة أخرى لنفس المريض، يجلبه البرنامج في كسر من الثانية مباشرة من الكاش (`[CACHE HIT]`).
   - عند تصدير التقرير عبر الخيار [12]، يجمع البرنامج مؤشراته بدقة ويصدر ملف `daily_report.txt` بـ Timestamp وتنسيق احترافي.
   - وإذا حاول موظف الاستقبال أو الطبيب حذف موعد أو تصفير النظام، يتصدى نظام الصلاحيات بحزم ويمنعه لعدم امتلاكه رتبة مدير النظام (`Admin`).
5. **الإغلاق الآمن وحماية البيانات:**
   سواء اختار المستخدم الخيار [11] للخروج، أو حدث انقطاع مفاجئ بالضغط على `Ctrl + C`، يتكفل كود الحماية بحفظ كافة التعديلات في ملف الـ JSON فوراً، ليظل كل سجل محفوظاً وجاهزاً لليوم التالي بأعلى درجات الموثوقية الهندسية.
