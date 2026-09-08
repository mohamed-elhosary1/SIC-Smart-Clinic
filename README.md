# Smart Clinic Queue System

مشروع كابستون الفصل الثالث — **Samsung Innovation Campus**  
**المشروع 5 — Smart Clinic Queue System**  
نظام متكامل لإدارة العيادات الذكية، طوابير الانتظار، حجز المواعيد، الفرز الطبي، والصلاحيات مع الحفظ التلقائي.

---

## 📑 الفهرس التفاعلي السريع للكود (Quick Interactive Index)

اضغط على أي عنصر في الجدول للانتقال مباشرة إلى سطور تنفيذه في ملف [`main.py`](main.py):

| المفهوم / الميزة | الملف والسطور المباشرة | ملخص الوظيفة الهندسية |
|---|---|---|
| **1. استثناءات النظام (Custom Exceptions)** | [`main.py#L16-L47`](main.py#L16-L47) | هرمية أخطاء مشتقة من `ClinicError` لمنع انهيار البرنامج وتخصيص الرسائل |
| **2. نظام الصلاحيات (RBAC & Auth)** | [`main.py#L50-L120`](main.py#L50-L120) | بوليمورفيزم `User` -> `StaffUser` و `DoctorUser` مع دالة `authenticate()` |
| **3. التحقق بالـ Regex** | [`main.py#L125-L146`](main.py#L125-L146) | دوال `re.compile()` و `fullmatch()` لفحص الـ ID والهواتف المصرية `01x` |
| **4. معالجة المدخلات (Input Parsing)** | [`main.py#L149-L204`](main.py#L149-L204) | تحويل المدخلات المرنة (أرقام، نصوص إنجليزية وعربية) إلى قيم قياسية |
| **5. كائنات الـ OOP الأساسية** | [`main.py#L209-L304`](main.py#L209-L304) | كلاسات `Person`, `Patient`, `EmergencyPatient`, `Doctor`, `Appointment` |
| **6. الإيتريتور المخصص (Iterator)** | [`main.py#L309-L325`](main.py#L309-L325) | كلاس `WaitingQueueIterator` وتطبيق بروتوكول `__iter__` و `__next__` |
| **7. الكلوزر والـ nonlocal (Closure)** | [`main.py#L327-L355`](main.py#L327-L355) | دالة `make_triage_calculator` لاحتساب الرسوم وحفظ حالة عداد الطوارئ |
| **8. الاستدعاء الذاتي (Recursion)** | [`main.py#L357-L370`](main.py#L357-L370) | دالة `find_visits_recursive` لفلترة الزيارات المكتملة بدون أي loops |
| **9. التخزين المؤقت (Memoization)** | [`main.py#L685-L708`](main.py#L685-L708) | تخزين نتائج استعلام السجل في `_visit_lookup_cache` مع إبطال الكاش التلقائي |
| **10. البرمجة الوظيفية (FP)** | [`main.py#L570-L591`](main.py#L570-L591) | تطبيق `filter` لطوارئ، و `sorted`+`lambda` للطابور، و `reduce` للأرباح |
| **11. التقرير والتصدير (DRY Report)** | [`main.py#L593-L683`](main.py#L593-L683) | توحيد الحسابات والتنسيق بين التقرير المعروض والمصدر لملف نصي |
| **12. الحفظ والاسترجاع التلقائي** | [`main.py#L710-L900`](main.py#L710-L900) | قراءة وحفظ JSON فوري مع الحماية من التلف عبر النسخ الاحتياطي `.bak` |
| **13. واجهات العمليات (Action Handlers)** | [`main.py#L906-L1459`](main.py#L906-L1459) | دوال العمليات الإدارية والطبية واستعلامات المريض المقيدة بنطاقه |
| **14. الشاشات والقوائم وبوابة المريض** | [`main.py#L1464-L1658`](main.py#L1464-L1658) | `opening_screen`, `patient_lookup`, `login_screen`, وقوائم الأدوار |
| **15. نقطة الانطلاق الرئيسية (Entry Point)** | [`main.py#L1664-L1693`](main.py#L1664-L1693) | دالة `main()` وإدارة دورة حياة البرنامج والحفظ التلقائي عند المقاطعة |

---

## 🛠️ دليل التنفيذ التفصيلي: كيف تم بناء كل ميزة؟ (Implementation Deep-Dive)

### 1. نظام الاستثناءات المخصص (Custom Exceptions Hierarchy)
- **الكود في المشروع:** [`main.py#L16-L47`](main.py#L16-L47)
- **ما وظيفته؟**  
  توفير هرمية استثناءات مخصصة تمنع انهيار البرنامج عند حدوث أخطاء تشغيلية، وتتيح للواجهة طباعة رسائل مفهومة للمستخدم.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. أنشأنا الكلاس الأساسي `ClinicError(Exception)` ليكون الأب المشترك لكافة أخطاء النظام.
  2. اشتققنا كلاسات فرعية تعبر عن كل حالة خطأ بعينها:
     - `InvalidAppointmentTimeError`: عند إدخال تاريخ في الماضي أو بصيغة غير مقبولة.
     - `DuplicateBookingError`: عند وجود موعد محجوز لنفس الطبيب أو المريض في نفس التوقيت.
     - `PatientNotFoundError` / `DoctorNotFoundError`: عند البحث عن معرف غير مسجل.
     - `InvalidFormatError`: عند فشل التحقق بصيغة الـ Regex.
  3. بفضل هذه الهرمية، يمكن اصطياد `except ClinicError as err` في أي شاشة لمعالجة كافة أخطاء النظام بكود موحد.

---

### 2. نظام الصلاحيات والأدوار (Authentication & Role-Based Access)
- **الكود في المشروع:** [`main.py#L50-L120`](main.py#L50-L120)
- **ما وظيفته؟**  
  فصل صلاحيات موظف العيادة عن الطبيب، وحماية العمليات الإدارية والطبية في واجهة المستخدم وطبقة الـ Business Logic معاً.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. كلاس أب `User` يحمل `username`, `password`, ومجموعة الصلاحيات `allowed_actions`.
  2. كلاس `StaffUser(User)` يعيد تعريف `has_permission(action)` لترجع دائماً `True` (صلاحيات مطلقة لإدارة العيادة).
  3. كلاس `DoctorUser(User)` يمتلك صلاحيات طبية مقيدة محددة في `DOCTOR_ACTIONS = {"view_queue", "update_visit_status", "daily_report", "view_history"}`.
  4. قاعدة بيانات الطاقم `USERS_DB` تحتوي على الحسابات الافتراضية ودوال مصنع (Factory Functions) لتوليد الكائنات.
  5. دالة `authenticate(username, password)` تتحقق من المدخلات وترجع كائن المستخدم المقابل أو ترفع `ClinicError`.

---

### 3. دوال التحقق وقواعد الـ Regex
- **الكود في المشروع:** [`main.py#L125-L146`](main.py#L125-L146)
- **ما وظيفته؟**  
  ضمان عدم دخول أي بيانات عشوائية أو غير مطابقة للمعايير الوطنية وصيغ النظام.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. تجهيز أنماط التعبيرات القياسية مسبقاً باستخدام `re.compile()` لتحقيق أقصى سرعة تنفيذ:
     - `PATIENT_ID_PATTERN = re.compile(r"patient-[0-9]+")`
     - `DOCTOR_ID_PATTERN = re.compile(r"doctor-[0-9]+")`
     - `PHONE_PATTERN = re.compile(r"01[0-9]{9}")` (رقم محمول مصري مكون من 11 رقماً يبدأ بـ 01).
  2. بناء دوال فحص ترجع قيمة بوليانية باستخدام `fullmatch()` للتأكد من مطابقة النص بالكامل من بدايته لنهايته.

---

### 4. هيكل الكائنات والوراثة والبوليمورفيزم (OOP Models)
- **الكود في المشروع:** [`main.py#L209-L304`](main.py#L209-L304)
- **ما وظيفته؟**  
  تمثيل كيانات العالم الحقيقي للعيادة عبر كائنات مترابطة ومرنة.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. **كلاس `Person`**: الكلاس الأساسي المشترك الذي يحوي الخصائص العامة (`person_id`, `name`, `phone`) والتحقق منها.
  2. **كلاس `Patient(Person)`**: يرث من `Person` ويضيف `age`, `case_type`, وقائمة `visit_history`.
  3. **البوليمورفيزم في المرضى**:
     - `EmergencyPatient`: يعيد `priority_level() -> 1` (أولوية قصوى تسبق الجميع في الطابور).
     - `RegularPatient`: يعيد `priority_level() -> 2` (أولوية عادية).
  4. **كلاس `Doctor(Person)`**: يرث من `Person` ويضيف `specialty`, وحالة التوفر `availability`, ودالة `toggle_availability()`.
  5. **كلاس `Appointment`**: يربط كائن مريض بكائن دكتور مع توقيت الزيارة وحالتها والرسوم المستحقة.

---

### 5. الإيتريتور المخصص لطابور الانتظار (Custom Iterator)
- **الكود في المشروع:** [`main.py#L309-L325`](main.py#L309-L325)
- **ما وظيفته؟**  
  السماح بالمرور على طابور الانتظار بشكل تسلسلي خطوة بخطوة وتطبيق بروتوكول التكرار في بايثون.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. بناء كلاس `WaitingQueueIterator` يستقبل قائمة المواعيد المرتبة مسبقاً حسب الأولوية.
  2. تعريف دالة `__iter__(self)` لترجع كائن الإيتريتور نفسه (`return self`).
  3. تعريف دالة `__next__(self)` لمتابعة مؤشر الفهرس `_index`:
     - إذا كان الفهرس أقل من طول القائمة، ترجع الموعد الحالي وتزيد العداد بـ 1.
     - عند الوصول للنهاية، ترفع استثناء `StopIteration` لإعلام حلقة التكرار بالتوقف.

---

### 6. الكلوزر واحتساب الرسوم مع المتغيرات غير المحلية (Closure & nonlocal)
- **الكود في المشروع:** [`main.py#L327-L355`](main.py#L327-L355)
- **ما وظيفته؟**  
  حساب رسوم الكشف بناءً على نوع المريض (150$ للطوارئ، 100$ للعادي) مع الاحتفاظ بحالة داخلية لعدد حالات الطوارئ التي تم حساب رسومها.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. دالة `make_triage_calculator(base_fee, initial_emergency_count)` تحتوي على متغير محلي `emergency_count`.
  2. دالة داخلية `calculate(patient)` تفحص `patient.priority_level()`:
     - إذا كانت طوارئ (1): تستخدم كلمة `nonlocal emergency_count` لزيادة العداد في البيئة المغلقة (Enclosing Scope) وترجع `base_fee * 1.5`.
     - إذا كانت عادية (2): ترجع `base_fee`.
  3. ربط دوال مساعدة كخصائص مباشرة على دالة الحساب:
     - `calculate.get_emergency_count()`: للاستعلام عن القيمة الحالية للعداد.
     - `calculate.decrement_emergency_count()`: لتنقيص العداد عند حذف كشف طوارئ.
     - `calculate.reset_count()`: لتصفير العداد عند إعادة ضبط العيادة.

---

### 7. فلترة السجل الطبي بالاستدعاء الذاتي بدون تكرار (Recursion - No Loops)
- **الكود في المشروع:** [`main.py#L357-L370`](main.py#L357-L370)
- **ما وظيفته؟**  
  استخراج المواعيد المكتملة (`completed`) من سجل المريض باستخدام الاستدعاء الذاتي التام ودون استخدام أي حلقة `for` أو `while`.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. دالة `find_visits_recursive(visits, index=0)` تستقبل قائمة المواعيد وفهرس البداية.
  2. **حالة التوقف (Base Case)**: إذا كان `index >= len(visits)`، ترجع قائمة فارغة `[]`.
  3. **الخطوة العودية (Recursive Step)**:
     - تفحص الموعد الحالي `current = visits[index]`.
     - إذا كانت حالته `completed`، تجمع `[current]` مع ناتج استدعاء الدالة لنفسها مع `index + 1`.
     - إذا لم تكن مكتملة، تستدعي الدالة لنفسها مع `index + 1` فقط.

---

### 8. التخزين المؤقت وإبطال الكاش (Memoization & Cache Invalidation)
- **الكود في المشروع:** [`main.py#L685-L708`](main.py#L685-L708)
- **ما وظيفته؟**  
  تحسين الأداء بتخزين نتائج استعلام التاريخ الطبي للمريض في الذاكرة المؤقتة، مع ضمان دقة البيانات بإفراغ الكاش تلقائياً عند أي تعديل.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. قاموس داخلي `_visit_lookup_cache` في `ClinicManager` يخزن النتائج بمفتاح `patient_id`.
  2. دالة `get_patient_completed_visits` تفحص وجود المعرف في الكاش:
     - إذا وجد، تعيد النتيجة مباشرة مع علامة `[CACHE HIT]`.
     - إذا لم يوجد، تستدعي دالة الاستدعاء الذاتي `find_visits_recursive`، وتخزن النتيجة في الكاش، وتعيدها مع علامة `[COMPUTED]`.
  3. **إبطال الكاش (Cache Invalidation)**: عند حجز موعد جديد، أو تعديل حالة موعد، أو حذف موعد، يتم استدعاء `self._visit_lookup_cache.pop(patient_id, None)` فوراً لمسح القيمة القديمة.

---

### 9. البرمجة الوظيفية (Functional Programming: filter, reduce, lambda)
- **الكود في المشروع:** [`main.py#L570-L591`](main.py#L570-L591)
- **ما وظيفته؟**  
  معالجة مجموعات البيانات بأسلوب إعلاني وظيفي نظيف وفعال.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. **`filter`**: في `get_emergency_patients()` لعزل مرضى الطوارئ:
     ```python
     filter(lambda p: p.priority_level() == 1, self.patients.values())
     ```
  2. **`sorted` مع `lambda` مركب**: في `sort_queue_by_priority()` لترتيب المواعيد أولاً بدرجة الأولوية (1 قبل 2) ثم بتوقيت الحجز زمنياً:
     ```python
     waiting.sort(key=lambda appt: (appt.patient.priority_level(), appt.time))
     ```
  3. **`reduce`**: في `calculate_total_revenue()` لجمع إجمالي رسوم الكشوفات المكتملة فقط:
     ```python
     reduce(lambda total, fee: total + fee, completed_fees, 0.0)
     ```

---

### 10. التقرير اليومي وتصديره الموحد (DRY Report Architecture)
- **الكود في المشروع:** [`main.py#L593-L683`](main.py#L593-L683)
- **ما وظيفته؟**  
  حساب وعرض وتصدير إحصائيات شاملة للعيادة مع الالتزام التام بمبدأ عدم تكرار الكود (Don't Repeat Yourself).
- **كيف تم بناؤه خطوة بخطوة؟**
  1. دالة `_compute_report_metrics()`: تحسب كافة الأرقام والإحصائيات (المرضى، الأطباء، المواعيد بحالاتها، الإيرادات، عداد الطوارئ) وتجمعها في قاموس واحد.
  2. دالة `_format_report_table(report, timestamp)`: تستقبل القاموس وتنسق جدولاً مؤطراً بعرض 56 حرفاً.
  3. دالة `daily_report()`: تستدعي الدوال المشتركة وتطبع التقرير على الشاشة.
  4. دالة `export_report_to_file()`: تستدعي نفس الدوال وتكتب المخرجات في ملف `daily_report.txt` مع توقيت التصدير دون إعادة كتابة أي منطق حسابي أو تنسيقي.

---

### 11. الحفظ والاسترجاع التلقائي والنسخ الاحتياطي (JSON Persistence)
- **الكود في المشروع:** [`main.py#L710-L900`](main.py#L710-L900)
- **ما وظيفته؟**  
  ضمان استمرارية البيانات وحمايتها من الضياع أو التلف عند إغلاق البرنامج فجأة أو تلف الملف.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. **الحفظ الفوري (`save_to_file`)**: تحويل كافة الكائنات إلى هياكل قواميس نظيفة وكتابتها بصيغة JSON مع معالجة التواريخ `isoformat()`.
  2. **الاسترداد الذكي (`load_from_file`)**:
     - إذا كان الملف غير موجود: يتم إنشاؤه تلقائياً بهيكل فارغ دون إطلاق أي أخطاء.
     - إذا كان الملف تالفاً: يتم إنشاء نسخة احتياطية فورية للملف التالف باسم `.bak`، ثم تهيئة قاعدة بيانات جديدة نظيفة لحماية البرنامج من التوقف.
  3. **الحفظ التلقائي عند الإنهاء**: في دالة `main()`، يتم اصطياد `KeyboardInterrupt` و `SystemExit` لحفظ التعديلات فوراً قبل الخروج.

---

### 12. الشاشة الافتتاحية وبوابة استعلام المريض (Opening Screen & Patient Lookup)
- **الكود في المشروع:** [`main.py#L1561-L1658`](main.py#L1561-L1658)
- **ما وظيفته؟**  
  توفير تجربة مستخدم واقعية ومرنة تفصل بين دخول الإدارة واستعلام المرضى.
- **كيف تم بناؤه خطوة بخطوة؟**
  1. **`opening_screen`**: شاشة رئيسية بـ 3 اختيارات:
     - `[1] Staff / Doctor Login` -> يفتح شاشة تسجيل الدخول المخصصة للطاقم الطبي والإداري.
     - `[2] Patient Lookup` -> يفتح بوابة استعلام المريض برقم الـ ID فقط دون كلمة مرور.
     - `[3] Exit` -> خروج آمن مع الحفظ التلقائي.
  2. **`patient_lookup`**: يطلب فقط `patient-xxx`، ويتأكد من وجود المريض في النظام، ثم يفتح مباشرة `run_patient_portal`.
  3. **`run_patient_portal`**: بوابة قراءة فقط للمريض تعرض مواعيده، دوره في طابور الانتظار، وسجله الطبي دون أي إمكانية لتعديل البيانات ودون الحاجة لأي حساب أو كلمة مرور.

---

## 👥 بيانات تسجيل دخول الطاقم (Staff Credentials)

تم إخفاء بيانات الحسابات الافتراضية من واجهات العرض لتبقى الواجهة احترافية، ويمكن استخدام الحسابات التالية لتسجيل الدخول:

| الدور الوظيفي (Role) | اسم المستخدم (Username) | كلمة المرور (Password) | الصلاحيات ونطاق الوصول |
|---|---|---|---|
| **Staff** | `staff` | `staff123` | إدارة كاملة لكافة العمليات دون قيود (تسجيل مرضى وأطباء، حجز، تعديل، حذف، تصفير، تقارير). |
| **Doctor** | `doctor` | `doc123` | معاينة طابور الانتظار، تحديث حالة الكشف، التقرير اليومي، والاطلاع على تاريخ المريض المكتمل. |
| **Patient** | *لا يوجد حساب* | *بدون كلمة مرور نهائيًا* | استعلام مباشر برقم الكود/البطاقة (`Patient ID`) فقط عبر خيار `[2] Patient Lookup`. |

---

## 📱 القوائم المخصصة حسب الدور (Role-Specific Menus)

1. **قائمة موظف العيادة (Staff Menu — 13 خياراً):**
   - `[1] Register Patient`
   - `[2] Add Doctor`
   - `[3] Book Appointment`
   - `[4] Update Visit Status`
   - `[5] Show Waiting Queue`
   - `[6] Toggle Doctor Status`
   - `[7] Delete Appointment`
   - `[8] Daily Report`
   - `[9] Save Data Now`
   - `[10] Reset Clinic Data`
   - `[11] Export Report`
   - `[12] Patient History`
   - `[13] Quit (Auto-Save)`

2. **بوابة الطبيب (Doctor Portal — 5 خيارات):**
   - `[1] Show Waiting Queue`
   - `[2] Update Visit Status`
   - `[3] Daily Report`
   - `[4] Patient History`
   - `[5] Quit (Auto-Save)`

3. **بوابة استعلام المريض (Patient Portal — 4 خيارات استعلامية مقيدة بـ Patient ID):**
   - `[1] My Appointments`
   - `[2] My Queue Position`
   - `[3] My Visit History`
   - `[4] Back to Main Screen`

---

## 🏛️ هيكل الكلاسات (Class Structure Summary)

| الكلاس | النوع | الوصف |
|---|---|---|
| `Person` | Base Class | الكلاس الأب المشترك لكافة الأشخاص (ID، الاسم، الهاتف مع Regex) |
| `Patient(Person)` | Subclass | بيانات المريض + سجل الزيارات `visit_history` + مستوى الأولوية |
| `EmergencyPatient(Patient)` | Subclass | مريض طوارئ — أولوية قصوى (Priority: 1) مع سعر كشف أعلى |
| `RegularPatient(Patient)` | Subclass | مريض عادي — أولوية عادية (Priority: 2) |
| `Doctor(Person)` | Subclass | بيانات الطبيب والتخصص وحالة التوفر (Available/Unavailable) |
| `Appointment` | Class | يمثل كشف طبي يربط المريض بالطبيب والوقت والحالة والرسوم |
| `WaitingQueueIterator` | Iterator Class | كاستم إيتريتور للمرور على طابور الانتظار خطوة بخطوة |
| `User` | Auth Base Class | الكلاس الأساسي للمستخدمين مع إدارة الصلاحيات ومجموعات العمليات |
| `StaffUser(User)` | Auth Subclass | موظف العيادة — صلاحيات كاملة لإدارة النظام، الأطباء، المرضى، والحجوزات |
| `DoctorUser(User)` | Auth Subclass | طبيب — صلاحيات المعاينة، تحديث الكشوفات، التقرير اليومي، والتاريخ الطبي |
| `ClinicManager` | Manager Class | المايسترو المشرف على النظام وقواعد البيانات والكاش والتقارير |

---

## 💡 جدول مفاهيم بايثون البرمجية (Python Core Concepts Table)

| المفهوم (Concept) | مكان الاستخدام في الكود | الغرض الهندسي والوظيفة |
|---|---|---|
| **Closure + nonlocal** | [`main.py#L327-L355`](main.py#L327-L355) | دالة `make_triage_calculator()` لحساب رسوم الكشف والاحتفاظ بعداد حالات الطوارئ في البيئة المغلقة |
| **Recursion (No Loops)** | [`main.py#L357-L370`](main.py#L357-L370) | دالة `find_visits_recursive()` لاستخراج المواعيد المكتملة عودياً مع Base Case نظيف دون loops |
| **Memoization / Caching** | [`main.py#L685-L708`](main.py#L685-L708) | تخزين نتائج استعلام الزيارات في `_visit_lookup_cache` مع إبطال الكاش فورياً عند التعديل |
| **Custom Iterator** | [`main.py#L309-L325`](main.py#L309-L325) | كلاس `WaitingQueueIterator` وتطبيق بروتوكول التكرار `__iter__` و `__next__` |
| **Lambda (Composite Key)** | [`main.py#L575-L580`](main.py#L575-L580) | مفتاح ترتيب مركب `(priority, time)` في `sort_queue_by_priority()` لفرز الطابور |
| **filter (Functional Tool)** | [`main.py#L570-L574`](main.py#L570-L574) | فلترة مرضى الطوارئ باستخدام دالة برمجية وظيفية `filter()` |
| **reduce (Functional Tool)** | [`main.py#L586-L590`](main.py#L586-L590) | تجميع إجمالي الإيرادات المالية من المواعيد المكتملة في `calculate_total_revenue()` |
| **Regex Precompilation** | [`main.py#L125-L146`](main.py#L125-L146) | استخدام `re.compile()` و `fullmatch()` لفحص المعرفات وأرقام الهواتف المصرية `01x` |
| **Custom Exceptions** | [`main.py#L16-L47`](main.py#L16-L47) | هرمية أخطاء مشتقة من `ClinicError` لتأمين العمليات ومنع توقف البرنامج |
| **Inheritance & Polymorphism** | [`main.py#L209-L304`](main.py#L209-L304) | تطبيق البوليمورفيزم في `Person → Patient/Doctor` و `Emergency/Regular` و `User → Staff/Doctor` |
| **DRY Report Engine** | [`main.py#L593-L683`](main.py#L593-L683) | توحيد الحسابات والتنسيق بين التقرير المعروض على الشاشة والمصدر لملف `daily_report.txt` |
| **JSON Persistence & Recovery** | [`main.py#L710-L900`](main.py#L710-L900) | حفظ واسترجاع تلقائي مع توليد نسخ احتياطية `.bak` عند تلف الملف لمنع الانهيار |
