# Smart Clinic Queue System

مشروع Chapter 3 Capstone — Samsung Innovation Campus (Effective Python Programming)

## Selected Option
**Option 5 — Smart Clinic Queue System**
إدارة المرضى، الدكاترة، الحجوزات، التريـاچ (الأولوية)، وطابور الانتظار.

## How to Run
```bash
python clinic_system.py
```
هيظهر منيو تفاعلي في الـ terminal فيه الاختيارات دي:
1. Register patient
2. Add doctor
3. Book appointment
4. Update visit status
5. Show waiting queue
6. Daily report
7. Quit

> **ملاحظة:** الكود الحالي سكيلتون (هيكل) — الميثودز فيها `#TODO` لسه محتاجة تتنفذ من الفريق قبل التشغيل الفعلي.

## Main Features
- تسجيل مرضى (عاديين وطوارئ) ودكاترة مع التحقق من صحة الـ ID ورقم التليفون
- حجز مواعيد مع منع التكرار والتحقق من صحة الوقت
- ترتيب طابور الانتظار حسب الأولوية (الطوارئ أولاً)
- حساب رسوم الزيارة تلقائيًا حسب نوع الحالة
- تقرير يومي بعدد الحالات، الطوارئ، والإيرادات

## Class Structure Summary

| الكلاس | النوع | الوصف |
|---|---|---|
| `Person` | Base Class | الأساس المشترك (id, name, phone) |
| `Patient(Person)` | Subclass | بيانات المريض + `priority_level()` |
| `EmergencyPatient(Patient)` | Subclass | مريض حالة طارئة — أولوية عالية |
| `RegularPatient(Patient)` | Subclass | مريض حالة عادية — أولوية أقل |
| `Doctor(Person)` | Subclass | بيانات الدكتور والتخصص |
| `Appointment` | Class | ربط مريض بدكتور في وقت معين |
| `WaitingQueueIterator` | Iterator Class | معالجة طابور الانتظار عنصر عنصر |
| `ClinicManager` | Manager Class | المايستر — بيدير كل حاجة في النظام |

**الوراثة:** `Person` هو الأب لـ `Patient` و `Doctor`، و `Patient` هو الأب لـ `EmergencyPatient` و `RegularPatient`.
**البوليمورفيزم:** في `display_profile()` (مختلف بين Patient/Doctor) وفي `priority_level()` (مختلف بين Emergency/Regular).

## Concept Mapping Table

| Concept | فين اتستخدم | ليه |
|---|---|---|
| **Closure + nonlocal** | `make_triage_calculator()` داخل `ClinicManager` | لحساب رسوم الزيارة مع الاحتفاظ بعدد الحالات الطارئة بين الاستدعاءات |
| **Lambda** | `sort_queue_by_priority()` | كـ key في `sorted()` لترتيب الطابور |
| **filter** | `get_emergency_patients()` | استخراج المرضى الطارئين بس من القائمة |
| **reduce** | `calculate_total_revenue()` | حساب إجمالي الإيرادات من المواعيد المكتملة |
| **Regex** | `validate_patient_id()`, `validate_phone()` | التحقق من صحة الـ ID ورقم التليفون |
| **Exceptions** | `InvalidAppointmentTimeError`, `DuplicateBookingError`, `PatientNotFoundError`, `DoctorNotFoundError`, `InvalidFormatError` | معالجة كل حالات الخطأ المحتملة أثناء الحجز والتسجيل |
| **Iterator** | `WaitingQueueIterator` (`__iter__` / `__next__`) | معالجة طابور الانتظار عنصر عنصر بدل استخدام list عادي |
| **Inheritance / Polymorphism** | `Person → Patient/Doctor`, `Patient → EmergencyPatient/RegularPatient` | سلوك مختلف فعليًا في `display_profile()` و `priority_level()` |

## Known Limitations
- المشروع حاليًا في مرحلة السكيلتون — الميثودز الأساسية (`#TODO`) لسه ملهاش تنفيذ فعلي
- مفيش تخزين دائم (JSON save/load) — البيانات بتتفقد بعد إغلاق البرنامج
- الـ `main()` لسه فاضية ومحتاجة تتوصل بالـ `ClinicManager`
