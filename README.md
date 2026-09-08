# Smart Clinic Queue System

— **Samsung Innovation Campus**  
**المشروع 5 — Smart Clinic Queue System**  
---

## بنية الملفات (Single-File Architecture)

* `clinic_data.json` — ملف التخزين  لقاعدة بيانات المرضى والأطباء والمواعيد مع الحفظ  والاسترداد .
* `ERD.md` — مخطط العلاقات  وقواعد البيانات.

---

## الشاشة الافتتاحية والصلاحيات (Opening Screen & RBAC)

عند تشغيل النظام، تظهر شاشة رئيسية بثلاثة مسارات واضحة ومنفصلة:
1. **`[1] Staff / Doctor Login`**: شاشة تسجيل دخول مخصصة للطاقم الطبي والإداري فقط بواسطة اسم المستخدم وكلمة المرور.
2. **`[2] Patient Lookup`**: استعلام فوري للمريض برقم الهاتف/الاي دي  (`Patient ID)
3. **`[3] Exit`**: إغلاق النظام مع حفظ البيانات .

### حسابات الطاقم الافتراضية (Default Staff Credentials)

| الدور الوظيفي (Role) | اسم المستخدم (Username) | كلمة المرور (Password) | الصلاحيات ونطاق الوصول |
|---|---|---|---|
| **Staff** | `staff` | `staff123` | إدارة كاملة لكافة العمليات دون قيود (تسجيل مرضى وأطباء، حجز، تعديل، حذف، تصفير، تقارير). |
| **Doctor** | `doctor` | `doc123` | معاينة طابور الانتظار، تحديث حالة الكشف، التقرير اليومي، والاطلاع على تاريخ المريض المكتمل. |
| **Patient** | *لا يوجد* (استعلام برقم `ID`) | *بدون كلمة مرور* |    (Patient Portal) برقم   (عرض مواعيده، ترتيبه في الطابور، سجله الطبي). |

### واجهات القوائم المخصصة حسب الدور (Role-Specific Menus)

1. **قائمة موظف العيادة (Staff Menu — 13):**
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

2. ** الطبيب (Doctor Portal — 5 خيارات):**
   - `[1] Show Waiting Queue`
   - `[2] Update Visit Status`
   - `[3] Daily Report`
   - `[4] Patient History`
   - `[5] Quit (Auto-Save)`

3. ** المريض (Patietient ID):**
   - `[1] My Appointments`
   - `[2] My Queue Position`
   - `[3] My Visit History`
   - `[4] Back to Main Screen`

---

## المميزات الرئيسية (Main Features)

مكسل اكتب والله هكتبها فالبريزنتيشن 
---

## هيكل الكلاسات (Class Structure Summary)

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

## جدول مفاهيم بايثون البرمجية (Concept Mapping Table)

| المفهوم (Concept) | مكان الاستخدام في الكود | الغرض الهندسي والوظيفة |
|---|---|---|
| **Closure + nonlocal** | `make_triage_calculator()` | حساب رسوم الكشف مع الاحتفاظ بعداد حالات الطوارئ وتعديله بـ `decrement_emergency_count` و `reset_count` |
| **Recursion** | `find_visits_recursive()` | استعراض سجل زيارات المريض واستخراج المكتملة منها بطريقة عودية نظيفة دون استخدام حلقات تكرارية (No Loops) |
| **Memoization / Caching** | `ClinicManager.get_patient_completed_visits()` | تخزين نتائج استعلام الزيارات المكتملة في `_visit_lookup_cache` لتحسين الأداء مع إفراغ الكاش تلقائياً عند أي تعديل |
| **Lambda** | `sort_queue_by_priority()` | كـ مفتاح فرز مركب `(priority, time)` لترتيب طابور الكشف |
| **filter** | `get_emergency_patients()` | فلترة مرضى الطوارئ باستخدام دالة برمجية وظيفية |
| **reduce** | `calculate_total_revenue()` | تجميع إجمالي الإيرادات المالية من المواعيد المكتملة فقط |
| **Regex** | `validate_patient_id()`, `validate_doctor_id()`, `validate_phone()` | التحقق الصارم من صيغ المعرفات وأرقام الهواتف المصرية المكونة من 11 رقماً |
| **Custom Exceptions** | `ClinicError`, `DuplicateBookingError`, `InvalidAppointmentTimeError`, ... | معالجة دقيقة ومنظمة لكافة حالات الخطأ المحتملة في النظام |
| **Custom Iterator** | `WaitingQueueIterator` (`__iter__` / `__next__`) | تكرار مخصص على عناصر الطابور بشكل متسلسل ومباشر |
| **Inheritance & Polymorphism** | `Person → Patient/Doctor`, `Patient → Emergency/Regular`, `User → Staff/Doctor/Patient` | تطبيق تعددي حقيقي في `display_profile()`, `priority_level()`, و `has_permission()` |
| **File I/O & JSON Recovery** | `save_to_file()`, `load_from_file()` | حفظ البيانات في JSON مع معالجة الاسترداد والنسخ الاحتياطي التلقائي `.bak` |
