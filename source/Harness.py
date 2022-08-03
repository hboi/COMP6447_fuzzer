import signal
import subprocess
from queue import PriorityQueue
from strategies.JSONMutator import JSONMutator
from strategies.CSVMutator import CSVMutator
from strategies.PlaintextMutator import PlaintextMutator

from magic import from_file

# Singleton class
class Harness():
    _instance = None
    _target = None
    _mutations = None
    _strategy = None
    _successful_payload = None
    
    
    def __init__(self):
        raise RuntimeError('Call get_instance() instead')

    @classmethod
    def create_instance(cls, target):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            cls._target = target
            cls._mutations = PriorityQueue()
        
    @classmethod
    def get_instance(cls):
        return cls._instance
    
    # Does not modify original queue
    def execute_mutations(cls):
        good_mutations = PriorityQueue()
        
        # Create a copy of the queue so we dont modify the original
        queue_copy = PriorityQueue()
        for i in cls._mutations.queue:
            queue_copy.put(i)

        # run the queue
        while not queue_copy.empty():
            # get the highest priority payload
            priority, payload = queue_copy.get()
            # run the payload

            # Multithreading
            cls.try_payload(payload)
            
            # Todo determine if this mutation was good, if so add it to good mutation
            # good_mutations.put((0,payload))
            
        return good_mutations
    
    # Entry point
    def fuzz(cls, default_payload):
        round = 1

        # Add the default payload to the mutation queue
        cls._mutations.put((0,default_payload))
        
        while True:
                
            print(f"Fuzzing mutation set {round}")                
            # Run the fuzzer on current mutations
            next_mutations = cls.execute_mutations()
            
            # Check if crash
            if not cls._successful_payload is None:
                break
            
            # Generate new mutations
            while not cls._mutations.empty():
                priority, payload = cls._mutations.get()
                mutated_payloads = cls._strategy.mutate_once(payload)

                for mutated_payload in mutated_payloads:
                    next_mutations.put((priority + 1, mutated_payload))
                
            # Replace queue with new mutations
            cls._mutations = next_mutations
            round += 1

        if cls._successful_payload != None:
            print("Finished fuzzing, writing payload to bad.txt")
            print(f"The length of the payload is {len(cls._successful_payload)} bytes")
            with open("bad.txt", "w") as f:
                f.write(cls._successful_payload)
        
    
    def try_payload(cls, payload):
        process, out, err = cls.send_data(payload)
        
        if process.returncode == -(signal.SIGABRT) or process.returncode != -(signal.SIGSEGV):
            return 0
    
        cls._successful_payload = payload
        return process.returncode

    def send_data(cls, payload_data):
        try:
            process = subprocess.Popen([f'{cls._target}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            process = subprocess.Popen([f'./{cls._target}'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            out, err = process.communicate(payload_data.encode()) 
        except subprocess.TimeoutExpired:
            process.terminate()

        return (process, out, err) 

    def set_fuzzer_strategy(cls, default_input):
        file_type = from_file(default_input)
        if "CSV" in file_type:
            print("Selecting CSV Fuzzer")
            cls._strategy = CSVMutator
            return
        elif "JPEG" in file_type:
            print("Selecting JPEG Fuzzer")
        elif "JSON" in file_type:
            print("Selecting JSON Fuzzer")
            cls._strategy = JSONMutator
            return
        elif "ASCII text" == file_type:
            print("Selecting plaintext Fuzzer")
            cls._strategy = PlaintextMutator
            return
        elif "HTML document, ASCII text" == file_type:
            print("Selecting XML Fuzzer")
        
        print("Unknown file type, using all fuzzers")
        cls._strategy = CSVMutator
        
