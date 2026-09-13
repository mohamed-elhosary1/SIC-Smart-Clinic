# الدليل التشريحي والتعليمي الشامل لمشروع العيادة الذكية (Smart Clinic Queue System)
## دليل التتبع التنفيذي خطوة بخطوة في الذاكرة (From RUN START to RUN END)

---

## المرحلة 1 — خريطة المشروع وتدفق البيانات قبل الضغط على Run

مشروعنا مبني بمعمارية **الملف الشامل (Single-File Architecture)**، حيث يحتوي الملف الرئيسي على كامل المنطق البرمجي، متصلاً بملفات التخزين والتقارير:

```text
               [المستخدم في الـ Terminal]
                          │
                          ▼
                      main.py  <── (الملف التنفيذي الشامل للكود)
                     /        \
                    ▼          ▼
           clinic_data.json   daily_report.txt  <── (ملفات القرص الصلب)
```

* **`main.py`**: هو الملف الوحيد الذي يبدأ منه وينتهي فيه البرنامج. يحتوي على كل الاستثناءات، الصلاحيات، الكلاسات، الفرز الطبي، الدوال العودية، وقائمة الأوامر.
* **`clinic_data.json`**: ملف قاعدة البيانات الدائمة على الهارد ديسك؛ يقرأ منه `main.py` عند بدء التشغيل لاستعادة البيانات، ويكتب فيه تلقائياً بعد كل عملية.
* **مسار التنفيذ المتوقع:** يبدأ المفسر بقراءة `main.py` من السطر الأول حتى الأخير لبناء الهياكل في الذاكرة، ثم يصل إلى نقطة الانطلاق `if __name__ == "__main__":`، فيستدعي `main()`، لتبدأ الشاشة التفاعلية.

---

## المرحلة 2 — اضغط Run معي (التنفيذ الفعلي خطوة بخطوة)

```text
============================================================
                        RUN START
============================================================
```

عند كتابة الأمر `python main.py` والضغط على Enter، لا يدخل المفسر مباشرة إلى دالة `main()`، بل يمر أولاً بمرحلة **تحميل الموديول وبناء الهياكل في الذاكرة (Module Loading & Definition Phase)**:

---

### الخطوة 1: استيراد المكتبات (Imports)

#### السطور 2 - 8:
```python
import json
import os
import random
import re
import shutil
from functools import reduce
from datetime import datetime
```

* **البرنامج وصل للسطور دي.**
* **ماذا يحدث الآن في الـ Memory؟**
  1. يبحث بايثون في مكتباته المدمجة عن موديول `json` ويحمله في الذاكرة، ويضع متغيراً عاماً اسمه `json` يشير إليه.
  2. يكرر نفس الشيء مع `os` (للتعامل مع مسارات الملفات وأحجامها).
  3. يستورد `random` (لتوليد أرقام عشوائية).
  4. يستورد `re` (للتحقق من الأنماط النصية Regex).
  5. يستورد `shutil` (لنسخ الملفات احتياطياً).
  6. في السطر 7: يدخل موديول `functools`، ولا يستورده كله، بل يستخرج منه دالة `reduce` فقط ويضعها في الذاكرة.
  7. في السطر 8: يستخرج كلاس `datetime` من موديول `datetime`.
* **البيانات:** كود بايثون الداخلي فقط.
* **بعد التنفيذ:** أصبح لدينا 7 مراجع برمجية جاهزة للاستخدام في الذاكرة.
* **ثم:** ينتقل للسطر 14.

---

### الخطوة 2: تجهيز كلاسات الاستثناءات المخصصة (Custom Exceptions)

#### السطور 14 - 41:
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

* **البرنامج وصل للسطور دي.**
* **ماذا يحدث الآن؟**
  بايثون **لا يطلق أي خطأ الآن**! هو فقط يبني قوالب استثناءات مخصصة داخل الذاكرة:
  ```text
  Exception (كلاس بايثون الأصلي)
      └── ClinicError (أب استثناءات العيادة)
            ├── InvalidAppointmentTimeError
            ├── DuplicateBookingError
            ├── PatientNotFoundError
            ├── DoctorNotFoundError
            └── InvalidFormatError
  ```
* **لماذا؟** حتى نتمكن لاحقاً من رفع واصطياد أخطاء العيادة دون أن ينهار البرنامج.
* **بعد التنفيذ:** الكلاسات مسجلة كأنواع في جدول الرموز العام (Global Symbol Table).
* **ثم:** ينتقل للسطر 48.

---

### الخطوة 3: تجهيز نظام الصلاحيات والمستخدمين (RBAC)

#### السطور 48 - 114:
```python
class User: ...
class AdminUser(User): ...
class ReceptionistUser(User): ...
class DoctorUser(User): ...
```

* **البرنامج وصل للسطور دي.**
* **ماذا يحدث في الذاكرة؟**
  بايثون **لم ينشئ أي مستخدم (Object) حتى الآن**! هو فقط خزن في الذاكرة القواعد التالية:
  * `User`: كلاس أساسي لديه ميثود `has_permission(action)`.
  * `AdminUser`: ميثود `has_permission` عنده تعيد دائماً `True` (صلاحيات مطلقة).
  * `ReceptionistUser`: لديه قائمة صلاحيات محددة `RECEPTIONIST_ACTIONS` (حجز، تسجيل، تقارير، ولكن لا يملك صلاحية حذف أو تصفير).
  * `DoctorUser`: لديه `DOCTOR_ACTIONS` (معاينة الطابور، تحديث الكشف، وسجل المريض فقط).
* **ثم:** ينتقل للسطر 117.

#### السطور 117 - 130:
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

* **ماذا يحدث الآن؟**
  يُنشئ بايثون قاموساً اسمه `USERS_DB` يحتوي على الحسابات الافتراضية، ومعه دالة مصنع صغيرة (`lambda`) مسؤولة عن إنتاج الـ Object المناسب عند تسجيل الدخول.
* **الذاكرة:** `USERS_DB` أصبح متغيراً عاماً يحتوي على 3 حسابات جاهزة.
* **ثم:** ينتقل للسطر 133 لتسجيل دالتي `authenticate` و `login_screen` كتعريفات في الذاكرة دون تنفيذهما الآن.

---

### الخطوة 4: تجميع أنماط الـ Regex ودوال التحليل

#### السطور 172 - 190:
```python
PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")
DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")
PHONE_PATTERN = re.compile(r"01[0-9]{9}")

def validate_patient_id(patient_id: str) -> bool: ...
def validate_doctor_id(doctor_id: str) -> bool: ...
def validate_phone(phone: str) -> bool: ...
```

* **ماذا يحدث في الذاكرة؟**
  يترجم بايثون نصوص الـ Regex مسبقاً عبر `re.compile()` إلى كائنات نمط مجمعة في الـ C-Level لضمان أقصى سرعة فحص.
* **ثم:** يسجل دوال الفحص (`validate_*`) ودوال تحليل المدخلات المرنة (`parse_patient_type`, `parse_status`, `parse_menu_choice`).
* **ثم:** ينتقل للسطر 256.

---

### الخطوة 5: تجهيز كلاسات الكيانات، الإيتريتور، الكلوزر، والدالة العودية

#### السطور 256 - 416:
* يمر المفسر على:
  * `Person` (الأب الأساسي الذي يتحقق من الهاتف فوراً).
  * `Patient`, `EmergencyPatient`, `RegularPatient` (المرضى وتحديد درجات الأولوية 1 للطوارئ و 2 للعادي).
  * `Doctor`, `Appointment`.
  * `WaitingQueueIterator` (كاستم إيتريتور يطبق بروتوكول `__iter__` و `__next__`).
  * `make_triage_calculator` (مصنع الكلوزر مع متغير `nonlocal`).
  * `find_visits_recursive` (الدالة العودية لاستخراج الكشوفات المكتملة بدون أي loops).
* **تأثير الذاكرة:** كلها أصبحت تعريفات (Definitions) مسجلة كقوالب. لا يوجد مريض واحد ولا كشف واحد تم إنشاؤه في الذاكرة حتى الآن!
* **ثم:** يمر على كلاس `ClinicManager` (السطور 423 - 948) ويسجل دواله.
* **ثم:** يمر على دالة `main()` (السطور 960 - 1472) ويسجلها كدالة.
* **ثم:** يصل أخيراً إلى السطر 1479!

---

### الخطوة 6: نقطة الانطلاق وبداية التشغيل الفعلي (Entry Point)

#### السطور 1479 - 1480:
```python
if __name__ == "__main__":
    main()
```

* **البرنامج وصل للسطر ده.**
* **ماذا يحدث الآن؟**
  بايثون يفحص المتغير الخاص الداخلي `__name__`.
  * بما أننا شغلنا الملف مباشرة، فإن `__name__ == "__main__"` قيمته `True`.
* **الـ Call Stack الآن:**
  ```text
  [Global Scope]
      ↓
  CALL main()
  ```
* **الانتقال:** يقفز مؤشر التنفيذ مباشرة إلى **السطر 960 داخل دالة `main()`**!

---

## المرحلة 3 — داخل دالة `main()` وتتبع الذاكرة والسيناريوهات

نحن الآن داخل دالة `main()`، وسنتتبع كل خطوة بالتفصيل الدقيق:

---

### الخطوة 7: إنشاء كائن مدير العيادة `ClinicManager`

#### السطر 961:
```python
manager = ClinicManager(base_fee=100.0)
```

* **ماذا يحدث خطوة بخطوة؟**
  1. بايثون يستدعي كلاس `ClinicManager`.
  2. يُحجز كائن جديد في الـ Heap، ويُمرر مرجعه إلى `__init__` كمعامل `self` مع تمرير `base_fee = 100.0`.
  3. **داخل `__init__` (السطر 426):**
     * `self.patients = {}`: قاموس فارغ للمرضى.
     * `self.doctors = {}`: قاموس فارغ للأطباء.
     * `self.appointments = []`: قائمة فارغة للمواعيد.
     * `self.booked_date = {}`: قاموس فارغ لجدول أوقات الأطباء (Instance Attribute).
     * `self.fee_calculator = make_triage_calculator(base_fee=100.0)`:
       * يدخل دالة `make_triage_calculator` (السطر 374).
       * يُنشأ متغير مغلق عليه في الـ Enclosing Scope اسمه `emergency_count = 0`.
       * ترجع الدالة الداخلية `calculate` ومحمل بها دوال التحكم بالعداد (`decrement_emergency_count`, إلخ).
     * `self.current_user = None`: لا يوجد مستخدم حالي بعد.
     * `self._visit_lookup_cache = {}`: قاموس التخزين المؤقت (Memoization) فارغ.
  4. يرجع الكائن المكتمل، ويتم تخزينه في المتغير المحلي `manager` داخل `main()`.

* **حالة الذاكرة بعد الخطوة 7:**
  ```text
  manager (ClinicManager Object)
    ├── patients: {}
    ├── doctors: {}
    ├── appointments: []
    ├── fee_calculator: (Closure with emergency_count = 0)
    ├── _visit_lookup_cache: {}
    └── current_user: None
  ```

---

### الخطوة 8: شاشة تسجيل الدخول (Authentication)

#### السطر 964:
```python
current_user = login_screen()
```

* **الـ Call Stack:**
  ```text
  main()
    ↓
  login_screen() (السطر 142)
  ```
* **ماذا يحدث؟**
  1. يطبع البرنامج فريم شاشة الدخول والحسابات الافتراضية.
  2. يدخل حلقة `while True:` وكتلة `try:`.
  3. يقف البرنامج عند السطر 156: `username = input("
  Username: ").strip()`.

---

#### سيناريو الدخول A (كلمة مرور خاطئة -> حدوث Exception واصطياده):
المستخدم يكتب:
* `Username:` `"admin"`
* `Password:` `"wrong123"`

**تتبع التنفيذ:**
```text
username = "admin"
password = "wrong123"
  ↓
استدعاء authenticate("admin", "wrong123") (السطر 133)
  ↓
داخل authenticate:
u_key = "admin"
user_record = USERS_DB.get("admin") -> وجد السجل!
user_record["password"] -> "admin123"
مقارنة: "admin123" != "wrong123" -> الشرط True!
  ↓
السطر 138:
raise ClinicError("Invalid credentials. Please check username and password.")
```

* **لحظة الـ `raise`:**
  1. يتم إنشاء كائن استثناء من نوع `ClinicError`.
  2. يتوقف تنفيذ `authenticate` فوراً.
  3. يرجع بايثون للخلف في الـ Call Stack باحثاً عن `except`.
  4. في `login_screen()` يجد:
     ```python
     except ClinicError as err:
         print(f"
[ERROR] {err} Try again.")
     ```
  5. يطبع على الشاشة:
     `[ERROR] Invalid credentials. Please check username and password. Try again.`
  6. **البرنامج لم يتوقف أو ينهار!** بل يعود لحلقة `while True` ويطلب الإدخال مجدداً.

---

#### سيناريو الدخول B (تسجيل دخول صحيح بنجاح):
المستخدم يكتب:
* `Username:` `"admin"`
* `Password:` `"admin123"`

**تتبع التنفيذ:**
```text
authenticate("admin", "admin123")
  ↓
user_record["password"] == "admin123" -> سليم!
  ↓
السطر 139:
return user_record["factory"]("admin", "admin123")
  ↓
تستدعى Lambda -> AdminUser("admin", "admin123")
  ↓
ينشأ Object من كلاس AdminUser:
  - username = "admin"
  - password = "admin123"
  - has_permission = دائماً True
  ↓
return user إلى login_screen()
  ↓
يطبع: [SUCCESS] Welcome, Administrator (admin)!
  ↓
return user إلى main()
```

* **العودة إلى `main()` (السطور 964 - 965):**
  ```python
  current_user = user  # أصبح نوعه AdminUser
  manager.set_current_user(current_user)  # تم ربط صلاحيات الأدمن بمدير العيادة
  ```

---

### الخطوة 9: استرجاع قاعدة البيانات التلقائي (Load Data)

#### السطر 968:
```python
manager.load_from_file("clinic_data.json")
```

* **تتبع مسار الملف:**
  1. يفتح الملف `clinic_data.json` ويقرأ محتوياته عبر `json.load(f)`.
  2. يعيد بناء كائنات المرضى (`EmergencyPatient` أو `RegularPatient`) ويضعها في قاموس `self.patients`.
  3. يعيد بناء كائنات الأطباء والمواعيد، ويعيد بناء جدول أوقات الدكاترة `self.booked_date`.
  4. **السطر 930: مزامنة عداد الطوارئ في الكلوزر:**
     ```python
     loaded_emergency_count = sum(1 for a in self.appointments if a.patient.priority_level() == 1)
     self.fee_calculator = make_triage_calculator(base_fee=100.0, initial_emergency_count=loaded_emergency_count)
     ```
     يقوم بعدّ حالات الطوارئ المخزنة فعلياً، ويعيد تهيئة الكلوزر ليبدأ العداد من الرقم الصحيح!
  5. يطبع رسالة النجاح: `[SUCCESS] Loaded data successfully...`.
  6. يعود إلى `main()`.

---

## المرحلة 4 — حلقة القائمة الرئيسية والسيناريوهات التفاعلية

البرنامج الآن في السطر 971 داخل حلقة `while True:`:
* يعرض عنوان القائمة شاملاً رتبة المستخدم: `CLINIC MAIN MENU - Administrator`.
* يطبع الخيارات الـ 13.
* ينتظر إدخال المستخدم: `choice = parse_menu_choice(input())`.

---

### سيناريو كامل 1: حجز موعد جديد ( الخيار 3 )

المستخدم يدخل `3`.

1. **فحص الصلاحية (السطر 1146):**
   `current_user.has_permission("book_appointment")` ترجع `True` لأن المستخدم أدمن.
2. **عرض الدكاترة:** يمر على `manager.doctors` ويطبع ملفاتهم بـ `display_profile()`.
3. **إدخال البيانات:**
   * المريض: `patient-238`.
   * الطبيب: `doctor-101`.
   * الوقت: `2026-10-15 14:00`.
4. **تنفيذ الحجز داخل `manager.book_appointment` (السطر 496):**
   * يحول النص لكائن `datetime`.
   * يفحص هل الوقت في المستقبل: `True`.
   * يفحص عدم تكرار الطبيب والمريض: `True`.
   * **حساب الرسوم بالكلوزر (السطر 537):**
     `new_appt.fee = self.fee_calculator(target_patient)`
     إذا كان المريض عادياً ترجع `100.0`، ولو كان طوارئ لزاد العداد ورجع `150.0`.
   * يضيف الحجز لـ `booked_date` وقائمة `appointments` وسجل المريض `visit_history`.
   * **إبطال الكاش (Cache Invalidation - السطر 545):**
     `self._visit_lookup_cache.pop(patient_id, None)`
     تم مسح سجل المريض من الكاش لتحديثه لاحقاً!
5. **الحفظ التلقائي:** يستدعي `manager.save_to_file("clinic_data.json", silent=True)`.
6. يطبع تفاصيل الحجز بنجاح.

---

### سيناريو كامل 2: سجل المريض مع الدالة العودية والتخزين المؤقت ( الخيار 13 )

المستخدم يدخل `13`.

#### المرة الأولى (الحساب الفعلي - COMPUTED):
1. يدخل كود المريض: `patient-238`.
2. يستدعي: `manager.get_patient_completed_visits("patient-238", return_status=True)`.
3. **داخل الدالة (السطر 732):**
   * يفحص الكاش: `if "patient-238" in self._visit_lookup_cache:` -> `False`.
   * يستدعي الدالة العودية: `find_visits_recursive(patient.visit_history, 0)`.
4. **تتبع الدالة العودية `find_visits_recursive` في الذاكرة:**
   لنفترض أن المريض لديه زيارتان: [زيارة 0 مكتملة، زيارة 1 معلقة].
   ```text
   الاستدعاء 1: find_visits_recursive(visits, index=0)
       index (0) < 2
       current_visit = visits[0] (completed)
       يستدعي: find_visits_recursive(visits, index=1)
           │
           ▼
   الاستدعاء 2: find_visits_recursive(visits, index=1)
       index (1) < 2
       current_visit = visits[1] (pending)
       يستدعي: find_visits_recursive(visits, index=2)
           │
           ▼
   الاستدعاء 3 (Base Case): find_visits_recursive(visits, index=2)
       index (2) >= 2 -> تحقق شرط التوقف!
       return []
           │
           ▼
   الارتداد للاستدعاء 2:
       الحالة pending -> return []
           │
           ▼
   الارتداد للاستدعاء 1:
       الحالة completed -> return [visits[0]] + [] -> [visits[0]]
   ```
5. **تخزين النتيجة في الكاش:**
   `self._visit_lookup_cache["patient-238"] = [visits[0]]`
   `is_hit = False`
6. يطبع على الشاشة:
   `[COMPUTED] Completed visits for Patient Mohamed (patient-238):`

#### المرة الثانية فوراً لنفس المريض (الكاش - CACHE HIT):
المستخدم يختار `13` لنفس المريض ثانية:
1. يفحص الكاش: `if "patient-238" in self._visit_lookup_cache:` -> **`True`**!
2. يسحب النتيجة مباشرة من الذاكرة بـ $O(1)$ دون استدعاء الدالة العودية ودون فحص أي سجلات.
3. يعين: `is_hit = True`.
4. يطبع على الشاشة فوراً:
   `[CACHE HIT] Completed visits for Patient Mohamed (patient-238):`

---

### سيناريو كامل 3: طابور الانتظار والإيتريتور المخصص ( الخيار 5 )

المستخدم يدخل `5`.

1. يستدعي: `queue_iter = manager.get_waiting_queue_iterator()`.
2. يرتب المواعيد المنتظرة بـ `lambda appt: (appt.patient.priority_level(), appt.time)`.
   (حالات الطوارئ ذات الأولوية 1 تسبق العادي ذات الأولوية 2 تلقائياً).
3. يُنشأ كائن `WaitingQueueIterator(waiting)`.
4. **حلقة `for appt in queue_iter:` (السطر 1283):**
   * يستدعي `__next__()`:
     * الدورة 1: يرجع الموعد الأول ويزيد `_index`.
     * الدورة 2: يرجع الموعد الثاني ويزيد `_index`.
     * الدورة 3: وصل لنهاية القائمة فيطلق `raise StopIteration`.
   * حلقة `for` تلتقط `StopIteration` وتتوقف بسلام.
5. يطبع جدول الطابور مع تمييز صفوف الطوارئ بـ `[!] EMERGENCY`.

---

### سيناريو كامل 4: حذف موعد وتنقيص عداد الكلوزر ( الخيار 7 )

المستخدم يختار `7` لحذف كشف طوارئ:
1. يفحص الصلاحية: مسموحة للأدمن فقط ومرفوضة لغيره.
2. يستقبل رقم الموعد (Index) ويطلب التأكيد `yes/no`.
3. يستدعي `manager.delete_appointment(idx)`:
   * يسحب الموعد عبر `self.appointments.pop(idx)`.
   * يحرر وقت الطبيب من `booked_date`.
   * يحذف الموعد من سجل زيارات المريض.
   * **تعديل عداد الكلوزر بـ `nonlocal` (السطر 606):**
     ```python
     if appt.patient.priority_level() == 1:
         self.fee_calculator.decrement_emergency_count()
     ```
     يدخل دالة `decrement_emergency_count` وينقص المتغير `emergency_count` المخزن في الذاكرة بمقدار 1!
   * يبطل كاش المريض.
4. يحفظ التغييرات في الـ JSON ويطبع رسالة النجاح وقيمة عداد الطوارئ المتبقية.

---

### سيناريو كامل 5: تصدير التقرير اليومي ومبدأ DRY ( الخيار 12 )

المستخدم يختار `12`:
1. يفحص الصلاحية: مسموحة للأدمن وموظف الاستقبال، ومرفوضة للطبيب.
2. يستقبل مسار الملف (افتراضياً `daily_report.txt`).
3. يستدعي `manager.export_report_to_file("daily_report.txt")`:
   * يستدعي `_compute_report_metrics()` التي تجمع كافة مؤشرات الأداء والأرباح المحسوبة بـ `reduce`.
   * يستدعي `_format_report_table()` لصناعة الفريم الموحد مع الـ Timestamp.
   * يفتح الملف ويكتب التقرير بداخله مع معالجة الأخطاء بـ `try/except`.
4. يطبع: `[SUCCESS] Daily report exported successfully to 'daily_report.txt'.`

---

### سيناريو كامل 6: رفض الصلاحيات (Role-Based Access Control)

لنفترض أن المستخدم الذي دخل كان **الطبيب** (`doctor` / `doc123`):
* حاول الطبيب اختيار **[1] تسجيل مريض**:
  1. السطر 998: `if not current_user.has_permission("register_patient"):`
  2. يستدعي `has_permission` على كائن `DoctorUser`.
  3. الطبيب لا يملك هذه الصلاحية -> ترجع `False`.
  4. النفي يجعل الشرط `True`، فيطبع فوراً:
     `[ERROR] Access denied. Your role 'Doctor' does not permit this action.`
  5. ينفذ السطر 1000: `continue` ويعود للقائمة الرئيسية دون إحداث أي تغيير!

---

### الخطوة 10: إنهاء البرنامج والحفظ الآمن (Exit & Auto-Save)

#### السيناريو الطبيعي (الخيار 11):
المستخدم يختار `11`.
* يستدعي `manager.save_to_file("clinic_data.json", silent=True)`.
* يطبع رسالة الوداع: `Data saved successfully. Goodbye!`.
* ينفذ `break` فتنكسر حلقة `while True` وتخرج دالة `main()`، ويغلق بايثون العملية بسلام.

#### سيناريو الإغلاق الفجائي (Ctrl + C):
إذا تم الضغط على `Ctrl + C` في أي وقت، يطلق بايثون `KeyboardInterrupt`.
السطر 1473 يلتقطه فوراً:
```python
except (KeyboardInterrupt, SystemExit):
    print("

[INFO] Program interrupted. Auto-saving clinic database before exit...")
    manager.save_to_file("clinic_data.json", silent=True)
    print("[SUCCESS] All clinic records saved safely. Goodbye!
")
```
يحفظ كل البيانات تلقائياً على القرص الصلب قبل الإغلاق، مما يحمي قاعدة البيانات من التلف.

```text
============================================================
                         RUN END
============================================================
```

---

## المرحلة 5 — الجداول المرجعية الشاملة

### 1. جدول الكلاسات (Classes)

| Class | لماذا موجود؟ | Objects منه أثناء التشغيل | أهم البيانات (Attributes) | أهم Methods |
|---|---|---|---|---|
| `User` | كلاس أب لنظام الصلاحيات | لا ينشأ أوبجكت مباشر منه (Abstract) | `username`, `password`, `allowed_actions` | `has_permission`, `display_role` |
| `AdminUser` | مدير النظام بصلاحيات كاملة | كائن واحد عند دخول الأدمن (`current_user`) | يرث بيانات `User` | `has_permission` ترجع `True` دائماً |
| `ReceptionistUser` | موظف الاستقبال | كائن واحد عند دخول موظف الاستقبال | يرث بيانات `User` مع قائمة محددة | `has_permission` |
| `DoctorUser` | الطبيب | كائن واحد عند دخول الدكتور | يرث بيانات `User` مع صلاحيات معاينة | `has_permission` |
| `Person` | كلاس أب للأفراد مع فحص الهاتف | لا ينشأ مباشرة بل عبر أبنائه | `person_id`, `name`, `phone` | `display_profile`, `__str__` |
| `Patient` | تمثيل المريض العام | ينشأ عبر أبنائه المتخصصين | يرث `Person` + `age`, `case_type`, `visit_history` | `priority_level` (ترجع 2), `add_visit` |
| `EmergencyPatient`| مريض طوارئ | كائن لكل مريض طوارئ مسجل | نفس بيانات المريض | `priority_level` (ترجع 1) |
| `RegularPatient` | مريض عادي | كائن لكل مريض عادي مسجل | نفس بيانات المريض | `priority_level` (ترجع 2) |
| `Doctor` | تمثيل الطبيب | كائن لكل طبيب مسجل في العيادة | يرث `Person` + `specialty`, `availability` | `toggle_availability`, `display_profile` |
| `Appointment` | كشف طبي يربط المريض بالطبيب | كائن لكل كشف محجوز | `patient`, `doctor`, `time`, `status`, `fee` | `update_status`, `__str__` |
| `WaitingQueueIterator`| إيتريتور للمرور على الطابور | ينشأ عند عرض الطابور (الخيار 5) | `_appointments`, `_index` | `__iter__`, `__next__` |
| `ClinicManager` | المايسترو المشرف على النظام | كائن واحد `manager` طوال فترة تشغيل البرنامج | `patients`, `doctors`, `appointments`, `booked_date`, `_visit_lookup_cache` | `book_appointment`, `daily_report`, `export_report_to_file`, إلخ |

---

### 2. جدول الدوال الأساسية (Functions)

| Function | من يستدعيها؟ | تستقبل ماذا؟ | البيانات من أين؟ | ماذا تفعل؟ | ماذا ترجع؟ | ترجع لمن؟ |
|---|---|---|---|---|---|---|
| `authenticate` | `login_screen` | `username, password` | مدخلات المستخدم بالكونسول | تفحص الحساب في `USERS_DB` | كائن مشتق من `User` | دالة `login_screen` |
| `login_screen` | `main` | لا شيء | مدخلات الكونسول | تدير حلقة الدخول مع الـ Exception | كائن المستخدم المصادق عليه | دالة `main` |
| `validate_phone` | `Person.__init__` | `phone: str` | مدخلات تسجيل المريض/الطبيب | تفحص تطابق نمط الهاتف المصري | `True / False` | كلاس `Person` |
| `parse_menu_choice` | `main` | `val: str` | إدخال المستخدم في القائمة | تحول أي كلمة أو رقم للرقم المعياري | نص رقم الخيار (`"1"` إلى `"13"`) | دالة `main` |
| `make_triage_calculator`| `ClinicManager.__init__` | `base_fee, initial_emergency` | مدير العيادة عند التهيئة | تبني كلوزر بمتغير `nonlocal` | دالة `calculate` بالعداد | سمة `manager.fee_calculator` |
| `find_visits_recursive` | `get_patient_completed_visits` | `visits: list, index: int` | سجل زيارات المريض | تستخرج الزيارات المكتملة عودياً | قائمة المواعيد المكتملة | ميثود تاريخ المريض بالكاش |

---

### 3. جدول أهم المتغيرات (Variables Tracing)

| Variable | نوعه | قيمته لحظة إنشائه | أخذها منين؟ | تستخدم فين؟ | هل تتغير قيمته؟ |
|---|---|---|---|---|---|
| `manager` | `ClinicManager` | كائن جديد فارغ | `ClinicManager(100.0)` | في كل عمليات دالة `main` | كائن ثابت ولكن تتغير محتويات قواميسه |
| `current_user` | مشتق من `User` | كائن المستخدم المسجل | دالة `login_screen()` | لفحص الصلاحيات وعرض الدور بالمنيو | ثابت طوال الجلسة |
| `emergency_count`| `int` داخل الكلوزر| 0 (أو عدد المحفوظ) | معامل الدالة الحاضنة | لتسعير الطوارئ والتقارير | تتغير بـ `+= 1` عند الحجز و `-= 1` عند الحذف |
| `_visit_lookup_cache`| `dict` | قاموس فارغ `{}` | تهيئة `ClinicManager` | لتخزين واسترجاع سجل المرضى $O(1)$ | تضاف له مفاتيح، ويتم إفراغها عند أي تعديل للمريض |
| `choice` | `str` | رقم الخيار المختار | دالة `parse_menu_choice` | داخل شروط `if / elif` لتوجيه التنفيذ | يتغير في كل دورة للقائمة |

---

### 4. جدول الاستثناءات (Exceptions)

| Exception | حصلت فين؟ | لماذا حدثت؟ | مين مسكها؟ (`except`) | البرنامج عمل إيه بعدها؟ |
|---|---|---|---|---|
| `ClinicError` | في `authenticate` | كلمة المرور أو اسم المستخدم غير مطابق | `login_screen` | طبعت رسالة خطأ وكررت المحاولة للمستخدم |
| `ClinicError` | داخل ميثودز `ClinicManager` | المستخدم حاول تنفيذ أمر غير مصرح لدوره | الكونسول في القائمة الرئيسية | طبعت رفض الصلاحية وأكمل البرنامج دورته |
| `InvalidFormatError` | في `Person.__init__` | رقم الهاتف ليس 11 رقماً أو لا يبدأ بـ 01 | واجهة التسجيل بالمنيو | منعت تسجيل المريض وطالبت بإدخال سليم |
| `DuplicateBookingError`| في `book_appointment` | الطبيب محجوز في نفس التوقيت لمريض آخر | شاشة الحجز بالمنيو | نبهت المستخدم بتعارض الموعد لإدخال وقت آخر |
| `StopIteration` | داخل `WaitingQueueIterator` | وصل المؤشر لنهاية طابور الانتظار | حلقة `for` تلقائياً | أنهت طباعة جدول الطابور بسلام |
| `KeyboardInterrupt` | في أي مكان بالبرنامج | المستخدم ضغط `Ctrl + C` لمقاطعة البرنامج | بلوك الأمان في نهاية `main` | حفظت كافة البيانات تلقائياً وخرجت بأمان تام |

---

## المرحلة 6 — قصة عمل البرنامج المتكاملة

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
