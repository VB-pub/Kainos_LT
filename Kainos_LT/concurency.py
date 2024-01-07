from abc import ABC, abstractmethod
import threading
import uuid

class Worker(ABC):
    lock = None
    cancel_requested = None
    semaphore = threading.Semaphore(5) 

    @classmethod
    def initialize_class_variables(cls):
        if cls.lock is None:
            cls.lock = threading.Lock()
        if cls.cancel_requested is None:
            cls.cancel_requested = False

    @abstractmethod
    def run(self):
        pass
    
    @classmethod
    def cancel_all(cls):
        try:
            with cls.lock:
                cls.cancel_requested = True
        except:
            cls.cancel_requested = True

class ItemWorker(Worker):
    next_page = {} 
    
    def __init__(self, correlation_id : uuid):
        Worker.initialize_class_variables()
        self.correlation_id = correlation_id
        with Worker.lock:
            if self.correlation_id not in ItemWorker.next_page:
                ItemWorker.next_page[self.correlation_id] = 1
            self.current_page = ItemWorker.next_page[self.correlation_id]
    
    def run(self, jobs, paginator, on_finish):
        with self.semaphore:
            try:
                while not Worker.cancel_requested and ItemWorker.next_page[self.correlation_id] is not None:
                    with Worker.lock:
                        self.current_page = ItemWorker.next_page[self.correlation_id]
                        ItemWorker.next_page[self.correlation_id] += 1

                    for job in jobs:
                        job()
            
                    paginator_next = paginator()
                    if not paginator_next:
                        with Worker.lock:
                            ItemWorker.next_page[self.correlation_id] = None
            finally:
                on_finish()
