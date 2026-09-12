from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator, model_validator
from typing import Optional, Annotated
from enum import Enum


class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class PatientCreation(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    age: int = Field(gt=0, lt=120)
    bloodGroup: Optional[BloodGroup] = None
    background: Annotated[
        str | None,
        Field(
            min_length=20,
            strict=True,
            title="Background of the user",
            description=" This field tells the background of patient so that root cause of problem can be identified ",
        ),
    ] = None
    email: EmailStr
    extremelyRare:bool=False
    weigth:float = 60.5
    height:float = 1.2
    
    
    @computed_field
    @property
    def calculateBMI(self) ->float: 
        bmi = round(self.weigth / (self.height**2),2)
        print("BMI calculated sussessfully")
        return bmi
    

    @model_validator(mode="after")
    @classmethod
    def validateModel(cls, model):
        if model.bloodGroup == BloodGroup.O_POSITIVE:
            model.extremelyRare = True

    @field_validator("email")
    @classmethod
    def validateEmail(cls, value):
        if "telgoo5" not in value:
            raise ValueError("Customer is not Telgoo5  employee'")


def createPatient(patient: PatientCreation):
    print(f"patient name :{patient.name} has the age of {patient.age} ")
    print(patient)
  


createPatient(
    PatientCreation(
        name="rahul bisht", age=112, bloodGroup="O+", email="Rahulbisht5436@telgoo5.com"
    )
)
