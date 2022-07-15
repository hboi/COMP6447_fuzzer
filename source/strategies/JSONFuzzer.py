from .Fuzzer import Fuzzer
import json
class JSONFuzzer(Fuzzer):
    def __init__(self, binary_path, binary_input_path):
        super().__init__(binary_path, binary_input_path)
        print("Running JSON Fuzzer")
        print(f"binary_path: {self.binary_path}")
        print(f"binary_input_path: {self.binary_input_path}")
        pass

    def fuzz(self):
        # Open the input JSON file for reading
        f = open(self.binary_input_path, "r")
        # Create a dictionary from the input JSON file's contents
        input_file_dict = json.load(f)
        # Iterate through the dictionary, seeing if changing 
        for value in input_file_dict.values():
              print(value)

        return "blah"

    def get_coverage():
        return 0.0
    
    def get_type_of_crash():
        return "e.g. buffer overflow"

