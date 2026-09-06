# Smart Clinic Queue System - ERD & Class Diagrams
**Samsung Innovation Campus (SIC) - Capstone Project**

---

## 1. Full Logical Entity Relationship Diagram (ERD)

مخطط العلاقات الكيانية المنطقي (Crow's Foot Notation) يوضح الكيانات الأساسية، الحقول، المفاتيح الأساسية والخارجية (PK/FK)، والعلاقات بين الجداول:

```mermaid
erDiagram
    PERSON {
        string person_id PK "Format: 'patient-num' or 'doctor-num'"
        string name "Full Name (Mandatory)"
        string phone "11-digit Egyptian Mobile (01xxxxxxxxx)"
    }

    PATIENT {
        string person_id PK, FK "References PERSON.person_id"
        int age "Valid range: 1 - 130"
        string case_type "Diagnosis / Medical Case"
        string patient_type "Discriminator: 'Regular' | 'Emergency'"
        int priority_level "1 for Emergency | 2 for Regular"
    }

    REGULAR_PATIENT {
        string person_id PK, FK "References PATIENT.person_id"
        int priority_level "Fixed: 2 (Normal queue)"
    }

    EMERGENCY_PATIENT {
        string person_id PK, FK "References PATIENT.person_id"
        int priority_level "Fixed: 1 (Preempts queue)"
    }

    DOCTOR {
        string person_id PK, FK "References PERSON.person_id"
        string specialty "Medical Specialty"
        boolean availability "True = Available | False = Busy"
    }

    APPOINTMENT {
        int appointment_id PK "Surrogate Key / Unique Index"
        string patient_id FK "References PATIENT.person_id"
        string doctor_id FK "References DOCTOR.person_id"
        datetime appointment_time "Scheduled Date & Time (Future)"
        string status "pending | in_progress | completed | cancelled"
        float fee "Calculated via Triage Closure ($100 or $150)"
    }

    CLINIC_SCHEDULE {
        string doctor_id PK, FK "References DOCTOR.person_id"
        datetime booked_slot PK "Unique Active Slot (Double Booking Guard)"
    }

    %% Inheritance / Subtyping relationships (Class Table Inheritance)
    PERSON ||--o| PATIENT : "is extended by"
    PERSON ||--o| DOCTOR : "is extended by"
    PATIENT ||--o| REGULAR_PATIENT : "specializes into"
    PATIENT ||--o| EMERGENCY_PATIENT : "specializes into"

    %% Operational Relationships
    PATIENT ||--o{ APPOINTMENT : "books / attends (1:N)"
    DOCTOR ||--o{ APPOINTMENT : "is assigned to (1:N)"
    DOCTOR ||--o{ CLINIC_SCHEDULE : "maintains schedule (1:N)"
```

---

## 2. Object-Oriented Class Diagram (OOP Design & Polymorphism)

مخطط الأصناف الموجهة للكائنات (Class Diagram) يوضح الوراثة، البوليمورفيزم، العلاقات، والـ Orchestrator (`ClinicManager`):

```mermaid
classDiagram
    class Person {
        +str person_id
        +str name
        +str phone
        +display_profile() str
        +__str__() str
    }

    class Patient {
        +int age
        +str case_type
        +list visit_history
        +display_profile() str
        +priority_level() int
        +add_visit(visit)
    }

    class RegularPatient {
        +priority_level() int : returns 2
        +display_profile() str
    }

    class EmergencyPatient {
        +priority_level() int : returns 1
        +display_profile() str
    }

    class Doctor {
        +str specialty
        +bool availability
        +display_profile() str
        +toggle_availability()
    }

    class Appointment {
        +Patient patient
        +Doctor doctor
        +datetime time
        +str status
        +float fee
        +update_status(new_status)
        +__str__() str
    }

    class WaitingQueueIterator {
        -list _appointments
        -int _index
        +__iter__() self
        +__next__() Appointment
    }

    class ClinicManager {
        +dict patients
        +dict doctors
        +list appointments
        +dict booked_date
        +callable fee_calculator
        +generate_unique_patient_id() str
        +generate_unique_doctor_id() str
        +register_patient(patient) Patient
        +add_doctor(doctor) Doctor
        +toggle_doctor_availability(doctor_id) bool
        +book_appointment(patient_id, doctor_id, time) Appointment
        +update_visit_status(index, status) Appointment
        +delete_appointment(index) Appointment
        +get_emergency_patients() list
        +sort_queue_by_priority() list
        +get_waiting_queue_iterator() WaitingQueueIterator
        +calculate_total_revenue() float
        +daily_report() dict
        +save_to_file(path) bool
        +load_from_file(path) bool
        +reset_database(path) bool
    }

    Person <|-- Patient : Inheritance
    Person <|-- Doctor : Inheritance
    Patient <|-- RegularPatient : Polymorphic Specialization
    Patient <|-- EmergencyPatient : Polymorphic Specialization

    Patient "1" o-- "0..*" Appointment : visit_history
    Doctor "1" o-- "0..*" Appointment : assigned_appointments
    Appointment ..> Patient : references
    Appointment ..> Doctor : references
    WaitingQueueIterator ..> Appointment : iterates over

    ClinicManager *-- "0..*" Patient : manages
    ClinicManager *-- "0..*" Doctor : manages
    ClinicManager *-- "0..*" Appointment : manages
    ClinicManager ..> WaitingQueueIterator : constructs
```

---

## 3. Relational Schema in 3rd Normal Form (3NF)

الهيكل العلائقي المكافئ لقواعد البيانات العلائقية (RDBMS) في الصيغة المعيارية الثالثة (3NF):

```sql
-- 1. جدول المرضى (يرث خواص Person)
CREATE TABLE Patients (
    person_id      VARCHAR(20) PRIMARY KEY, -- regex: ^patient-[0-9]+$
    name           VARCHAR(100) NOT NULL,
    phone          CHAR(11) NOT NULL,       -- regex: ^01[0-9]{9}$
    age            INT CHECK (age BETWEEN 1 AND 130),
    case_type      VARCHAR(200) NOT NULL,
    patient_type   VARCHAR(10) CHECK (patient_type IN ('Regular', 'Emergency')),
    priority_level INT CHECK (priority_level IN (1, 2))
);

-- 2. جدول الأطباء (يرث خواص Person)
CREATE TABLE Doctors (
    person_id      VARCHAR(20) PRIMARY KEY, -- regex: ^doctor-[0-9]+$
    name           VARCHAR(100) NOT NULL,
    phone          CHAR(11) NOT NULL,       -- regex: ^01[0-9]{9}$
    specialty      VARCHAR(100) NOT NULL,
    availability   BOOLEAN DEFAULT TRUE
);

-- 3. جدول المواعيد الطبية (Associative Entity يفك علاقة Many-to-Many)
CREATE TABLE Appointments (
    appointment_id   INT AUTO_INCREMENT PRIMARY KEY,
    patient_id       VARCHAR(20) NOT NULL,
    doctor_id        VARCHAR(20) NOT NULL,
    appointment_time DATETIME NOT NULL,
    status           VARCHAR(15) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    fee              DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES Patients(person_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(person_id) ON DELETE CASCADE
);

-- 4. جدول حماية المواعيد ومنع التكرار (Double Booking Guard)
CREATE TABLE Doctor_Booked_Slots (
    doctor_id   VARCHAR(20) NOT NULL,
    booked_time DATETIME NOT NULL,
    PRIMARY KEY (doctor_id, booked_time),
    FOREIGN KEY (doctor_id) REFERENCES Doctors(person_id) ON DELETE CASCADE
);
```

---

## 4. Comprehensive Data Dictionary (قاموس البيانات التفصيلي)

| Entity / Table | Field Name | Data Type | Key / Constraint | Validation / Business Rule | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Person** | `person_id` | `VARCHAR(20)` | **PK** | Regex: `^(patient\|doctor)-[0-9]+$` | المعرف الفريد للشخص في النظام |
| | `name` | `VARCHAR(100)` | NOT NULL | Non-empty string | الاسم الكامل للشخص |
| | `phone` | `CHAR(11)` | NOT NULL | Regex: `^01[0-9]{9}$` | رقم الهاتف المحمول المصري المكون من 11 رقماً |
| **Patient** | `age` | `INT` | NOT NULL | 1 <= age <= 130 | عمر المريض بالسنوات |
| | `case_type` | `VARCHAR(200)` | DEFAULT `'General Checkup'` | Text | وصف الحالة المرضية / التشخيص |
| | `patient_type` | `VARCHAR(10)` | ENUM | `'Regular'` أو `'Emergency'` | نوع المريض لتحديد المسار العلاجي |
| | `priority_level`| `INT` | COMPUTED | `1` (Emergency) أو `2` (Regular) | مستوى الأولوية المستخدم في ترتيب طابور الانتظار |
| **Doctor** | `specialty` | `VARCHAR(100)` | NOT NULL | Text | التخصص الطبي للطبيب |
| | `availability`| `BOOLEAN` | DEFAULT `TRUE` | `True` (Available) / `False` (Busy) | حالة توفر الطبيب لاستقبال كشوفات جديدة |
| **Appointment** | `appointment_id`| `INT` | **PK** | Surrogate / Array Index | المعرف التسلسلي للموعد |
| | `patient_id` | `VARCHAR(20)` | **FK** | Must exist in `Patients` | معرّف المريض صاحب الحجز |
| | `doctor_id` | `VARCHAR(20)` | **FK** | Must exist in `Doctors` | معرّف الطبيب المعالج |
| | `time` | `DATETIME` | NOT NULL | Must be future datetime | تاريخ ووقت الزيارة المحددة |
| | `status` | `VARCHAR(15)` | DEFAULT `'pending'` | `pending`, `in_progress`, `completed`, `cancelled` | الحالة الحالية للموعد الطبي |
| | `fee` | `DECIMAL(6,2)`| NOT NULL | Base: $100.00, Emergency: $150.00 | تكلفة الكشف المحسوبة عبر دالة الكلوزر |

---

## 5. Business Rules & Cardinalities (قواعد العمل والعلاقات)

1. **Patient <-> Appointment (1 : N):**
   - المريض الواحد يمكن أن يمتلك 0 أو عدة مواعيد مجدولة (0..*).
   - الموعد الواحد يتبع بالضرورة مريضًا واحدًا فقط (1).
2. **Doctor <-> Appointment (1 : N):**
   - الطبيب الواحد يمكن أن يُسند إليه 0 أو عدة مواعيد (0..*).
   - الموعد الواحد يتبع طبيبًا واحدًا فقط (1).
3. **Double Booking Guard (`Doctor_Booked_Slots` / `booked_date`):**
   - لا يمكن لنفس الطبيب أن يكون لديه أكثر من موعد غير ملغي في نفس التوقيت `(doctor_id, time) is UNIQUE`.
   - إلغاء الموعد يحرر الوقت فورًا، وحذف الموعد يحرر الوقت وينقص عداد الطوارئ في الكلوزر.
4. **Reactivation Guard:**
   - عند محاولة إعادة تفعيل موعد ملغي (`cancelled` -> `pending`)، يتم التحقق أولاً من أن الطبيب لم يستقبل مريضاً آخر في نفس التوقيت أثناء فترة الإلغاء.
5. **Queue Prioritization:**
   - يتم ترتيب طابور الانتظار أولاً بحسب `priority_level` تصاعدياً (حالات الطوارئ `1` تسبق الحالات العادية `2`)، ثم بوقت الموعد `time`.

---

## 6. JSON Data Persistence Mapping (`clinic_data.json`)

طريقة تمثيل وتخزين الكيانات والعلاقات في ملف التخزين المحلي `clinic_data.json`:

```json
{
    "patients": [
        {
            "type": "Emergency",
            "person_id": "patient-102",
            "name": "Hossam",
            "phone": "01233334444",
            "age": 45,
            "case_type": "Cardiac"
        }
    ],
    "doctors": [
        {
            "person_id": "doctor-201",
            "name": "Adel",
            "phone": "01544445555",
            "specialty": "Cardiology",
            "availability": true
        }
    ],
    "appointments": [
        {
            "patient_id": "patient-102",
            "doctor_id": "doctor-201",
            "time": "2026-11-01T10:00:00",
            "status": "pending",
            "fee": 150.0
        }
    ]
}
```
