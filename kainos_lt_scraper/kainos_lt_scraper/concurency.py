from abc import ABC, abstractmethod
import threading
import uuid
from typing import Callable, Dict, Any

class Worker(ABC):
    """An abstract base class for workers that perform tasks concurrently."""
    lock: threading.Lock = None
    cancel_requested: bool = None
    semaphore: threading.Semaphore = threading.Semaphore(5)

    @classmethod
    def initialize_class_variables(cls) -> None:
        """
        Initialize class variables if they haven't been already.
        """
        if cls.lock is None:
            cls.lock = threading.Lock()
        if cls.cancel_requested is None:
            cls.cancel_requested = False

    @abstractmethod
    def run(self) -> None:
        """
        The main method that each worker needs to implement and will be called to perform its task.
        """
        pass

    @classmethod
    def cancel_all(cls) -> None:
        """
        Signal to all worker instances that they should cancel their operation at the next opportunity.
        """
        try:
            with cls.lock:
                cls.cancel_requested = True
        except:
            cls.cancel_requested = True

class ItemWorker(Worker):
    """A specific type of Worker that processes items."""
    next_page: Dict[uuid.UUID, int] = {}

    def __init__(self, correlation_id: uuid.UUID) -> None:
        """
        Initialize an ItemWorker with a given correlation_id.
        
        :param correlation_id: A unique identifier for this worker's tasks.
        """
        Worker.initialize_class_variables()
        self.correlation_id: uuid.UUID = correlation_id
        with Worker.lock:
            if self.correlation_id not in ItemWorker.next_page:
                ItemWorker.next_page[self.correlation_id] = 1
            self.current_page: int = ItemWorker.next_page[self.correlation_id]

    def run(self, jobs: Callable[[], None], paginator: Callable[[], Any], on_finish: Callable[[], None]) -> None:
        """
        Run the worker, processing each job in the provided list of jobs.
        
        :param jobs: A list of functions representing the tasks to be done.
        :param paginator: A function that handles pagination.
        :param on_finish: A function to call when the worker finishes its tasks.
        """
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
