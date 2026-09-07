# Smart Clinic Queue System

مشروع كابستون الفصل الثالث — **Samsung Innovation Campus**  
**المشروع 5 — Smart Clinic Queue System**  
نظام متكامل لإدارة العيادات الذكية، طوابير الانتظار، حجز المواعيد، الفرز الطبي، والصلاحيات مع الحفظ التلقائي.

---

## بنية الملفات (Single-File Architecture)

تم دمج كامل عناصر النظام داخل ملف واحد رئيسي وفقاً لمعايير المشروع:
* `main.py` — يحتوي على كامل استثناءات النظام، نماذج البيانات (OOP)، التحقق (Regex)، العمليات الوظيفية (Closure/Iterators/Recursion/Memoization)، نظام الصلاحيات، والواجهة التفاعلية (CLI).
* `clinic_data.json` — ملف التخزين الدائم لقاعدة بيانات المرضى والأطباء والمواعيد مع الحفظ التلقائي والاسترداد الذاتي.
* `ERD.md` — مخطط العلاقات البرمجية وقواعد البيانات.

---

## شاشة تسجيل الدخول والصلاحيات (Authentication & RBAC)

عند تشغيل النظام، تظهر شاشة تسجيل دخول إلزامية. تتوفر ثلاثة حسابات تجريبية مدمجة:

| الدور الوظيفي (Role) | اسم المستخدم (Username) | كلمة المرور (Password) | الصلاحيات الأساسية |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | كافة الصلاحيات كاملة بدون أي قيود (إدارة، حذف، تصفير، تقارير). |
| **Receptionist** | `receptionist` | `recep123` | تسجيل المرضى، إضافة دكاترة، حجز المواعيد، تحديث الحالات، تبديل توفر الطبيب، عرض الطابور، تاريخ المريض، وتصدير التقرير. |
| **Doctor** | `doctor` | `doc123` | معاينة طابور الانتظار، تحديث حالة الكشف، والاطلاع على تاريخ المريض المكتمل. |

### مصفوفة الصلاحيات (Role Permissions Matrix)

| العملية (Action) | Administrator | Receptionist | Doctor |
|---|:---:|:---:|:---:|
| `[1] Register Patient` | نعم | نعم | لا |
| `[2] Add Doctor` | نعم | نعم | لا |
| `[3] Book Appointment` | نعم | نعم | لا |
| `[4] Update Visit Status` | نعم | نعم | نعم |
| `[5] Show Waiting Queue` | نعم | نعم | نعم |
| `[6] Toggle Doctor Status` | نعم | نعم | لا |
| `[7] Delete Appointment` | نعم | لا | لا |
| `[8] Daily Report` | نعم | نعم | نعم |
| `[9] Save Data Now` | نعم | نعم | نعم |
| `[10] Reset Clinic Data` | نعم | لا | لا |
| `[11] Quit (Auto-Save)` | نعم | نعم | نعم |
| `[12] Export Report` | نعم | نعم | لا |
| `[13] Patient History (Memo)` | نعم | نعم | نعم |

---

## المميزات الرئيسية (Main Features)

1. **نظام صلاحيات متقدم (RBAC):** استخدام البوليمورفيزم عبر هرمية `User` لتحديد الصلاحيات بدقة مع حماية الواجهة والـ Business Logic.
2. **الفرز والتحقق الذكي (Triage & Regex):** تمييز حالات الطوارئ وتقديمها في الطابور تلقائياً مع فحص أرقام الهواتف المصرية (01x) ومعرفات المرضى والأطباء.
3. **التصدير اليومي الموحد (Export Daily Report):** تصدير تقرير شامل إلى ملف نصي (`daily_report.txt`) بتنسيق موحد مع Timestamp مع تطبيق مبدأ DRY كاملاً.
4. **سجل المرضى العودي المخزن مؤقتاً (Recursive & Memoized History):** فلترة الزيارات المكتملة بدالة عودية (`find_visits_recursive`) بدون loops، مع استخدام التخزين المؤقت (Memoization) لتحقيق أقصى سرعة استجابة وإفراغ الكاش تلقائياً (Cache Invalidation) عند أي تعديل.
5. **إلغاء المواعيد وتعديل الطوارئ:** إمكانية حذف موعد محدد مع تنقيص عداد الطوارئ في الكلوزر تلقائياً وتحرير الموعد في جدول الطبيب.
6. **الحفظ التلقائي والاسترداد الذاتي:** حفظ فوري لجميع البيانات مع معالجة ذكية للملفات المفقودة والتالفة (إنشاء تلقائي وأخذ نسخ احتياطية `.bak`).

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
| `AdminUser(User)` | Auth Subclass | مدير النظام — صلاحيات كاملة دائماً |
| `ReceptionistUser(User)` | Auth Subclass | موظف استقبال — صلاحيات العمليات اليومية والحجز |
| `DoctorUser(User)` | Auth Subclass | طبيب — صلاحيات المعاينة وتحديث الكشوفات |
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
| **Inheritance & Polymorphism** | `Person → Patient/Doctor`, `Patient → Emergency/Regular`, `User → Admin/Recep/Doc` | تطبيق تعددي حقيقي في `display_profile()`, `priority_level()`, و `has_permission()` |
| **File I/O & JSON Recovery** | `save_to_file()`, `load_from_file()` | حفظ البيانات بصيغة JSON مع معالجة الاسترداد والنسخ الاحتياطي التلقائي `.bak` |
