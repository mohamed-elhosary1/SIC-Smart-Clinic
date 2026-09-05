import re
class Clinic_Error(Exception):
    pass
class Invalidappointment_time_Error(Clinic_Error):
    pass
class DuplicatingBoking_Error(Clinic_Error):
    pass
class PateintNotFound_Error(Clinic_Error):
    pass
class DocumentNotFound_Error(Clinic_Error):
    pass
def validate_patient_id(patient_id):
    pattern="patient-[0-9]+"
    if re.fullmatch(pattern,patient_id):
        return True
    return False
def validate_doctor_id(doctor_id):
    pattern="doctor-[0-9]+"
    if re.fullmatch(pattern,doctor_id):
        return True
    return False
def validate_phone_(phone):
    return bool(re.fullmatch("01[0-9]{9}",phone))
class person:
    def __init__(self,person_id,name,phone_):
        self.person_id = person_id
        self.name = name
        self.phone_ = phone_
    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone_}"
    def __str__(self):
        return f"{self.person_id} {self.name} {self.phone_}"
class patient(person):
    def __init__(self,patient_id,name,phone,age,case_type):
        if not validate_patient_id(patient_id):
            raise PateintNotFound_Error("patient_id")
        super().__init__(patient_id,name,phone)
        self.age = age
        self.case_type = case_type
        self.history = []
    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone_} {self.age} {self.case_type}"
    def priority_level(self):
        return "normal"
    def add_visit(self,visit):
        self.history.append(visit)
class emergency_patient(patient):
    def priority_level(self):
        return 1
    def display_profile(self):
        list=super().display_profile()
        return f"{list} high priority"
class Regular_Patients(patient):
    def priority_level(self):
        return 2
    def display_profile(self):
        list= super().display_profile()
        return f"{list} regular priority"
class doctor(person):
    def __init__(self,doctor_id,name,phone_,speciality,availability=True or False):
        self.doctor_id = doctor_id
        self.person_id = doctor_id
        self.name = name
        self.phone_ = phone_
        self.speciality = speciality
        self.availability = availability
    def display_profile(self):
        return f"{self.doctor_id} {self.name} {self.phone_} {self.speciality}"
    def toggle_availability(self):
        self.availability = not self.availability
class appointment:
    booked_date = {}
    def __init__(self,patient,doctor,date,fee,status="scheduled"):
        if doctor.person_id not in appointment.booked_date:
            appointment.booked_date[doctor.person_id] = []
        if date in appointment.booked_date[doctor.person_id]:
            raise DuplicatingBoking_Error("appointment already booked")
        appointment.booked_date[doctor.person_id].append(date)
        self.patient=patient
        self.doctor=doctor
        self.date=date
        self.fee=fee
        self.status=status

    def update_status(self,new_status):
        self.status=new_status
    def __str__(self) :
        return f"{self.patient.person_id} {self.doctor.person_id} {self.date} {self.status}"
if __name__=="__main__":
    patient_1=emergency_patient("patient-243","ali mohamed","01272829111","25","chestpain")
    doctor_1=doctor("doctor-100","mohamed alaa","01205341252","cardilogist")
    appointment_1=appointment(patient_1,doctor_1,"tuesday: 8:00 Am",300)
    print(patient_1.display_profile())
    print(doctor_1.display_profile())
    print(appointment_1)
class Clinic_Error(Exception):
    pass
class Invalidappointment_time_Error(Clinic_Error):
    pass
class DuplicatingBoking_Error(Clinic_Error):
    pass
class PateintNotFound_Error(Clinic_Error):
    pass
class DocumentNotFound_Error(Clinic_Error):
    pass
def validate_patient_id(patient_id):
    pattern="patient-[0-9]+"
    if re.fullmatch(pattern,patient_id):
        return True
    return False
def validate_doctor_id(doctor_id):
    pattern="doctor-[0-9]+"
    if re.fullmatch(pattern,doctor_id):
        return True
    return False
def validate_phone_(phone):
    return bool(re.fullmatch("01[0-9]{9}",phone))
class person:
    def __init__(self,person_id,name,phone_):
        self.person_id = person_id
        self.name = name
        self.phone_ = phone_
    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone_}"
    def __str__(self):
        return f"{self.person_id} {self.name} {self.phone_}"
class patient(person):
    def __init__(self,patient_id,name,phone,age,case_type):
        if not validate_patient_id(patient_id):
            raise PateintNotFound_Error("patient_id")
        super().__init__(patient_id,name,phone)
        self.age = age
        self.case_type = case_type
        self.history = []
    def display_profile(self):
        return f"{self.person_id} {self.name} {self.phone_} {self.age} {self.case_type}"
    def priority_level(self):
        return "normal"
    def add_visit(self,visit):
        self.history.append(visit)
class emergency_patient(patient):
    def priority_level(self):
        return 1
    def display_profile(self):
        list=super().display_profile()
        return f"{list} high priority"
class Regular_Patients(patient):
    def priority_level(self):
        return 2
    def display_profile(self):
        list= super().display_profile()
        return f"{list} regular priority"
class doctor(person):
    def __init__(self,doctor_id,name,phone_,speciality,availability=True):
        self.doctor_id = doctor_id
        self.person_id = doctor_id
        self.name = name
        self.phone_ = phone_
        self.speciality = speciality
        self.availability = availability
    def display_profile(self):
        return f"{self.doctor_id} {self.name} {self.phone_} {self.speciality}"
    def toggle_availability(self):
        self.availability = not self.availability
class appointment:
    booked_date = {}
    def __init__(self,patient,doctor,date,fee,status="scheduled"):
        if doctor.person_id not in appointment.booked_date:
            appointment.booked_date[doctor.person_id] = []
        if date in appointment.booked_date[doctor.person_id]:
            raise DuplicatingBoking_Error("appointment already booked")
        appointment.booked_date[doctor.person_id].append(date)
        self.patient=patient
        self.doctor=doctor
        self.date=date
        self.fee=fee
        self.status=status

    def update_status(self,new_status):
        self.status=new_status
    def __str__(self) :
        return f"{self.patient.person_id} {self.doctor.person_id} {self.date} {self.status}"
if __name__=="__main__":
    patient_1=emergency_patient("patient-243","ali mohamed","01272829111","25","chestpain")
    doctor_1=doctor("doctor-100","mohamed alaa","01205341252","cardilogist")
    appointment_1=appointment(patient_1,doctor_1,"tuesday: 8:00 Am",300)
    print(patient_1.display_profile())
    print(doctor_1.display_profile())
    print(appointment_1)
