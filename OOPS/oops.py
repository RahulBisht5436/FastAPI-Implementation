class baseClass:
    def __init__(self,name,cls,rollnumber):
        self.name=name
        #private instance variable
        self.__cls=cls
        self.rollnumber=rollnumber
        
    def getDetails(self):
        print(f"User : {self.name} is in class {self.__cls} , with rollnumber : {self.rollnumber} ")
        
student1 = baseClass("Rahul Bisht" , "12B" , "1900950100064")
student1._baseClass__cls # will through error
print(student1._baseClass__cls)