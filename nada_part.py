# ==============================================================================
# كود ندى (NADA) - مراجعة تفصيلية قبل وبعد التعديل
# يحتوي هذا الملف على:
# 1. كود ندى قبل التعديل (في كومنت)
# 2. ذكر الخطأ (The Error)
# 3. سبب الخطأ وتأثيره (The Reason)
# 4. كود ندى بعد التعديل والتصحيح
# ==============================================================================

from functools import reduce
from datetime import datetime

# استيراد كلاسات عمر ودوال الفحص عشان ندى معتمدة عليها
from omar_part_reviewed import (
    Person, Patient, Doctor, Appointment, EmergencyPatient, RegularPatient,
    validate_patient_id, validate_doctor_id, validate_phone,
    ClinicError, InvalidFormatError, DuplicateBookingError,
    PatientNotFoundError, DoctorNotFoundError, InvalidAppointmentTimeError
)


# ==============================================================================
# الجزء 1: كلاس WaitingQueueIterator (الـ Custom Iterator للطابور)
# ==============================================================================

# [قبل التعديل]:
# class WaitingQueueItrerator:
#     def __init__(self,appointments):
#         self.appointments=appointments
#         self.index=0
#     def __iter__(self):
#         return self
#     def __next__(self):
#         if self.index>=len(self.appointments):
#             raise StopIteration
#         appointment=self.appointments[self.index]
#         self.index+=1
#         return appointment
#
# الخطأ:
# 1. حرف r زيادة في اسم الكلاس (WaitingQueueItrerator بدل WaitingQueueIterator).
# 2. كارثة مسافات (Indentation): ندى دخلت دالة الـ closure وكلاس الـ ClinicManager
#    جوه كلاس الـ Iterator كأنهم تابعين ليه!
#
# السبب:
# حرف الـ r الزيادة ده NameError فوري عند الاستدعاء في main.
# وتداخل المسافات بيخلي بايثون تعتبر ClinicManager كلاس داخلي ومحدش يقدر يوصل له برة!
#
# [بعد التعديل]:
class WaitingQueueIterator:
    """
    Custom iterator that walks through the waiting queue one
    appointment at a time.
    """

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


# توفير وقت وتوافق لاسم ندى اللي فيه حرف زيادة
WaitingQueueItrerator = WaitingQueueIterator


# ==============================================================================
# الجزء 2: دالة حساب الرسوم (make_triage_calculator - Closures + nonlocal)
# ==============================================================================

# [قبل التعديل]:
#     def make_triage_calculator(base_fee):
#         emergency_count=0
#
#         def calculate(patient):
#             nonlocal emergency_count
#
#             if patient.priority_level()==1:
#                 emergency_count+=1
#                 return base_fee*2
#             return calculate
#
# الخطأ:
# 1. سطر return calculate محطوط جوه دالة calculate نفسها! فلو المريض مش طوارئ هترجع الدالة نفسها بدل السعر العادي!
# 2. دالة make_triage_calculator الكبيرة مش بترجع حاجة (بتطلع None)!
# 3. مكانها كان معمول له Indent جوه كلاس الـ Iterator بالغلط.
#
# السبب:
# لما تستدعي make_triage_calculator(100) هترجعلك None، ولما تيجي تناديها بعدها هتديك:
# TypeError: 'NoneType' object is not callable وتفرقع البرنامج!
#
# [بعد التعديل]:
def make_triage_calculator(base_fee: float = 100.0):
    """
    Returns a closure function that calculates a visit fee based on
    patient priority_level(). Uses `nonlocal` to track emergency cases.
    """
    emergency_count = 0  # state that changes inside the closure

    def calculate(patient: Patient) -> float:
        nonlocal emergency_count
        if patient.priority_level() == 1:
            emergency_count += 1
            return float(base_fee * 1.5)  # أو base_fee * 2 حسب الرغبة
        return float(base_fee)  # يرجع السعر العادي للمريض العادي

    return calculate  # الـ closure يرجع الدالة نفسها هنا برة!


# ==============================================================================
# الجزء 3: كلاس ClinicManager وتجهيز القوائم
# ==============================================================================

# [قبل التعديل]:
#     class ClinicManager:
#         def __init__(self):
#             self.patients ={}
#             self.doctors={}
#             self.appointments={}
#             self.fee_calculator = make_triage_calculator(100)
#
# الخطأ:
# 1. عملت self.appointments = {} كـ dictionary قاموس!
# 2. الكلاس كله كان متزحزح بمسافات (Indentation) جوه الـ Iterator.
#
# السبب:
# المواعيد لازم تكون list مش dict؛ لأن ندى نفسها في باقي الكود بتنادي .append()
# وبتنادي index وبتعمل for loop، وده كان هيدي:
# AttributeError: 'dict' object has no attribute 'append'
#
# [بعد التعديل]:
class ClinicManager:
    """
    Central orchestrator class managing patients, doctors, and appointments.
    """

    def __init__(self, base_fee: float = 100.0):
        self.patients: dict[str, Patient] = {}
        self.doctors: dict[str, Doctor] = {}
        self.appointments: list[Appointment] = []  # قائمة list مش dictionary عشان append تشتغل!
        self.fee_calculator = make_triage_calculator(base_fee=base_fee)

    # --------------------------------------------------------------------------
    # الجزء 4: تسجيل المرضى والدكاترة (Registration)
    # --------------------------------------------------------------------------

    # [قبل التعديل]:
    # def register_patient(self, patient):
    #     if not validate_patient_id(patient.person_id):
    #         raise InvalidFormatError("Invalid patient ID")
    #     if patient.person_id in self.patients:
    #         raise InvalidFormatError("Patient ID already exists")
    #     self.patients[patient.person_id] = patient
    #     return patient
    #
    # def add_doctor(self,doctor):
    #     if not validate_doctor_id(doctor.person_id):
    #         raise InvalidFormateError("Invalid doctor ID")
    #     if doctor.person_id in self.doctors:
    #         raise InvalidFormatError(" Doctor ID already exists")
    #     self.doctors[doctor.person_id]=doctor
    #     return doctor
    #
    # الخطأ:
    # 1. في add_doctor كتبت InvalidFormateError بحرف e زيادة!
    # 2. رفع InvalidFormatError لو الـ ID متكرر؛ الصح إنه DuplicateBookingError أو رسالة توضح التكرار.
    #
    # السبب:
    # InvalidFormateError بالـ e مش موجودة أصلاً وهتضرب NameError فوراً.
    #
    # [بعد التعديل]:
    def register_patient(self, patient: Patient):
        if not validate_patient_id(patient.person_id):
            raise InvalidFormatError(f"Invalid patient ID: '{patient.person_id}'")

        if patient.person_id in self.patients:
            raise DuplicateBookingError(f"Patient with ID '{patient.person_id}' already exists")

        self.patients[patient.person_id] = patient
        return patient

    def add_doctor(self, doctor: Doctor):
        if not validate_doctor_id(doctor.person_id):
            raise InvalidFormatError(f"Invalid doctor ID: '{doctor.person_id}'")  # صلحنا الـ e الزيادة

        if doctor.person_id in self.doctors:
            raise DuplicateBookingError(f"Doctor with ID '{doctor.person_id}' already exists")

        self.doctors[doctor.person_id] = doctor
        return doctor

    # --------------------------------------------------------------------------
    # الجزء 5: حجز المواعيد (book_appointment) - الكارثة الكبرى
    # --------------------------------------------------------------------------

    # [قبل التعديل]:
    # def book_appointment(self,patient_id,doctor_id,time):
    #     if patient_id not in self.patients:
    #         raise PatientNotfoundError("patient not found")
    #     if doctor_id not in self.doctors:
    #         raise DoctorNotFoundError("doctor not found")
    #     if time <=datetime.now():
    #         raise InvalidAppointmentTimeError("Invalid appointment time")
    #     for appointment in self.appointments:
    #         if appointment.doctor.person_id ==doctor_id and appointment.time==time:
    #             raise DuplicateBookingError("Doctor already have an appointment at this time")
    #         if appointment.patient.person_id ==patient_id and appointment.time==time:
    #             raise DuplicateBookError("patient aready have an appointment at this time")
    #
    #         patient=self.patients[patient_id]
    #         doctor=self.doctors[doctor_id]
    #         appointment=appointment(patient,doctor,time)
    #         appointment.fee=self.fee_calculator(patient)
    #         self.appointments.append(appointment)
    #         return appointment
    #
    # الخطأ:
    # 1. أخطاء أسماء: PatientNotfoundError بحرف f صغير بدل F، و DuplicateBookError ناقصة ing!
    # 2. كارثة المسافات (Indentation): أسطر إنشاء الموعد وحجزه محطوطة جوة الـ for loop!
    #    فلو العيادة لسه مفيهاش أي مواعيد، اللوب مش هيشتغل أصلاً ومش هيحجز أي موعد!
    # 3. كارثة حجب الاسم (Variable Shadowing): سمت متغير اللوب appointment، وبعدها نادت
    #    appointment = appointment(...) فحاولت تستدعي الأوبجكت كأنه كلاس وضيعت الكلاس!
    # 4. لو الـ time مبعوت نص string المقارنة time <= datetime.now() بتضرب TypeError.
    #
    # [بعد التعديل]:
    def book_appointment(self, patient_id: str, doctor_id: str, time):
        if patient_id not in self.patients:
            raise PatientNotFoundError(f"Patient '{patient_id}' not found")

        if doctor_id not in self.doctors:
            raise DoctorNotFoundError(f"Doctor '{doctor_id}' not found")

        # تحويل النص لـ datetime بأمان لو مبعوت string
        if isinstance(time, str):
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %I:%M %p", "%Y/%m/%d %H:%M"):
                try:
                    time = datetime.strptime(time.strip(), fmt)
                    break
                except ValueError:
                    continue
            else:
                raise InvalidAppointmentTimeError(f"Invalid date format '{time}'. Use YYYY-MM-DD HH:MM")

        if time <= datetime.now():
            raise InvalidAppointmentTimeError("Appointment time cannot be in the past")

        # فحص التكرار برة وبشكل منفصل وبدون حجب اسم Appointment
        for existing_appt in self.appointments:
            if existing_appt.doctor.person_id == doctor_id and existing_appt.time == time and existing_appt.status != "cancelled":
                raise DuplicateBookingError(f"Doctor {doctor_id} already has an appointment at this time")
            if existing_appt.patient.person_id == patient_id and existing_appt.time == time and existing_appt.status != "cancelled":
                raise DuplicateBookingError(f"Patient {patient_id} already has an appointment at this time")

        # الحجز برة اللوب بشكل سليم 100%
        target_patient = self.patients[patient_id]
        target_doctor = self.doctors[doctor_id]

        new_appt = Appointment(target_patient, target_doctor, time, status="pending")
        new_appt.fee = self.fee_calculator(target_patient)

        self.appointments.append(new_appt)
        target_patient.add_visit(new_appt)
        return new_appt

    # --------------------------------------------------------------------------
    # الجزء 6: تحديث حالة الزيارة (update_visit_status)
    # --------------------------------------------------------------------------

    # [قبل التعديل]:
    # def update_visit_status(self,appointment_index,new_status):
    #     if appointment_index <0 or appointment_index >= len(self.appointments):
    #         raise IndexError("Invalid appointment number")
    #     allowed_status ={
    #         "pending", "in_progress", "completed", "cancelled",
    #     }
    #     if new_status not in allowed_statuses:
    #         raise valueError("Invalid visit status")
    #     appointment=self.appointments[appointment_index]
    #     appointment.update_status(new_status)
    #     return appointment
    #
    # الخطأ:
    # 1. عرفت المتغير باسم allowed_status (مفرد) ولما جت تفحص فحصت في allowed_statuses (جمع)! -> NameError.
    # 2. كتبت valueError بحرف v صغير بدل ValueError -> NameError.
    #
    # [بعد التعديل]:
    def update_visit_status(self, appointment_index: int, new_status: str):
        if appointment_index < 0 or appointment_index >= len(self.appointments):
            raise IndexError(f"Invalid appointment index {appointment_index}")

        allowed_statuses = {"pending", "in_progress", "completed", "cancelled", "scheduled"}
        if new_status.lower() not in allowed_statuses:
            raise ValueError(f"Invalid visit status '{new_status}'")  # صلحنا اسم الـ ValueError والـ s

        appt = self.appointments[appointment_index]
        appt.update_status(new_status)
        return appt

    # --------------------------------------------------------------------------
    # الجزء 7: فلترة وترتيب الطابور (filter / lambda / iterator)
    # --------------------------------------------------------------------------

    # [قبل التعديل]:
    # def get_emergency_patients(self):
    #     emergency=filter(lambda patient:patient.priority_level()==1,self.patients.values())
    #     return list(emergency)
    #
    # def sort_queue_by_priority(self):
    #     waiting = []
    #     for appointment in self.appointments:
    #         if appointment.status == "pending":
    #             waiting.append(appointment)
    #     waiting.sort(key=lambda appointment: appointment.patient.priority_level())
    #     return waiting
    #
    # def get_waiting_queue_by_priority_iterator(self):
    #     waiting=self.sort_queue_by_priority()
    #     return WaitingQueueItrerator(waiting)
    #
    # التقييم:
    # استخدام ممتاز لـ filter و lambda!
    # فقط في دالة الـ iterator تم ضبط الاسم ليتوافق مع main.py: get_waiting_queue_iterator.
    #
    # [بعد التعديل]:
    def get_emergency_patients(self):
        """Return only emergency patients using filter + lambda."""
        emergency = filter(lambda p: p.priority_level() == 1, self.patients.values())
        return list(emergency)

    def sort_queue_by_priority(self):
        """Sort waiting queue using sorted() / sort() with a lambda key."""
        waiting = [appt for appt in self.appointments if appt.status == "pending"]
        waiting.sort(key=lambda appt: (appt.patient.priority_level(), appt.time))
        return waiting

    def get_waiting_queue_iterator(self):
        """Return a ready-to-use WaitingQueueIterator over sorted queue."""
        waiting = self.sort_queue_by_priority()
        return WaitingQueueIterator(waiting)

    # Alias لاسم ندى
    get_waiting_queue_by_priority_iterator = get_waiting_queue_iterator

    # --------------------------------------------------------------------------
    # الجزء 8: حساب الإيرادات والتقرير اليومي (reduce & daily_report)
    # --------------------------------------------------------------------------

    # [قبل التعديل]:
    # def calculate_total_revenue(self):
    #     completed_fees = []
    #     for appointment in self.appointments:
    #         if appointment.status == "completed":
    #             completed_fees.append(appointment.fee)
    #     total = reduce(lambda total, fee: total + fee,completed_fees,0)
    #     return total
    #
    # def daily_report(self):
    #     emergency_count=len(self.get_emergency_patients())
    #     completed=len([appointment for appointment in  self.appointments if appointment.status =="completed"])
    #     pending=len([appointment for appointment in self.appointments if  appointment.status =="pending"])
    #     cancelled =len([appointment for appointment in self.appointments if appointment.status =="cancelled"])
    #     revenue=self.calculate_total_revenue()
    #     return { ... }
    #
    # التقييم:
    # ممتازة في استخدام reduce والـ List Comprehensions!
    # تم تظبيطها فقط لطباعة التقرير في الـ Terminal بشكل شيك بالإضافة لإرجاع الـ dict.
    #
    # [بعد التعديل]:
    def calculate_total_revenue(self):
        """Calculate total revenue from completed appointments using reduce."""
        completed_fees = [appt.fee for appt in self.appointments if appt.status == "completed"]
        return reduce(lambda total, fee: total + fee, completed_fees, 0.0)

    def daily_report(self):
        """Generate a real report from actual data and print summary."""
        emergency_count = len(self.get_emergency_patients())
        completed = len([a for a in self.appointments if a.status == "completed"])
        pending = len([a for a in self.appointments if a.status == "pending"])
        cancelled = len([a for a in self.appointments if a.status == "cancelled"])
        revenue = self.calculate_total_revenue()

        report = {
            "total_patients": len(self.patients),
            "total_doctors": len(self.doctors),
            "emergency_patients": emergency_count,
            "completed_visits": completed,
            "pending_visits": pending,
            "cancelled_visits": cancelled,
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
        print(f" Emergency Cases    : {report['emergency_patients']}")
        print(f" Total Revenue      : ${report['total_revenue']:.2f}")
        print("=" * 45 + "\n")

        return report


# ==============================================================================
# الجزء 9: تجربة تشغيل كود ندى وعمر معاً (Self-Test عشان منروحش فداهية)
# ==============================================================================
if __name__ == "__main__":
    print("--- Testing Nada's corrected part with Omar's classes ---")

    manager = ClinicManager(base_fee=100.0)

    # 1. تسجيل دكتور
    doc = Doctor("doctor-101", "Mohamed Alaa", "01012345678", "Cardiology")
    manager.add_doctor(doc)
    print(f" Added: {doc.display_profile()}")

    # 2. تسجيل مريض عادي ومريض طوارئ
    p_reg = RegularPatient("patient-201", "Ahmed Ali", "01234567890", 30, "Checkup")
    p_emg = EmergencyPatient("patient-202", "Mona Hassan", "01512345678", 45, "Chest Pain")
    manager.register_patient(p_reg)
    manager.register_patient(p_emg)
    print(f" Registered: {p_reg.name} & {p_emg.name}")

    # 3. حجز مواعيد
    from datetime import timedelta
    future_time1 = datetime.now() + timedelta(days=1, hours=2)
    future_time2 = datetime.now() + timedelta(days=1, hours=3)

    appt1 = manager.book_appointment("patient-201", "doctor-101", future_time1)
    appt2 = manager.book_appointment("patient-202", "doctor-101", future_time2)
    print(f" Booked appt1 fee: ${appt1.fee:.2f} (Regular)")
    print(f" Booked appt2 fee: ${appt2.fee:.2f} (Emergency - surcharge applied)")

    # 4. تجربة الـ Iterator وترتيب الطابور
    print("\n--- Waiting Queue (Emergency First) ---")
    queue_iter = manager.get_waiting_queue_iterator()
    for item in queue_iter:
        print(f"Queue item: {item.patient.name} (Priority {item.patient.priority_level()}) at {item.time}")

    # 5. تحديث حالة وإيرادات
    manager.update_visit_status(0, "completed")
    manager.update_visit_status(1, "completed")
    print(f"\n Total Revenue (reduce): ${manager.calculate_total_revenue():.2f}")

    # 6. التقرير اليومي
    manager.daily_report()

    print(" All Nada's tests passed successfully without errors!")
