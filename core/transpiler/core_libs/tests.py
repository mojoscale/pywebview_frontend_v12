
__include_modules__ = {"espressif8266":"ESP8266TEST,ESP8266TEST2", 
"espressif32":"ESP32TEST,ESP32TEST2"}
__dependencies__ = {"espressif8266":"ESP8266TEST,ESP8266TEST2", 
"espressif32":"ESP32TEST,ESP32TEST2"}

testvar:int = 1 
testvar_2: str = "asdds"
testvar_3: list = [1, 2, 3, 4]
testvar_4 = 10



class TestClass:
	def __init__(self, arg1: int, arg2: str):
		self.arg1 = arg1 
		self.arg2 = arg2

		self.__use_as_is__ = True
		self.__translation__= None 


	def method1(self, some_arg:str):

		__use__as_is__ = True 
		__translation__ = None

		return 


	def method2(self, some_arg:str, some_other_arg:int):

		__use__as_is__ = True 
		__translation__ = None

		return 


def test_function(a:int, c:str) -> str:
	__use__as_is__ = False
	__translation__ = "some_Other_Test({0}).some_other_func({1}).run()"

	return "abc"


def return_list_func() -> list[str]:

	__use__as_is__ = True 

	return ["a"]




