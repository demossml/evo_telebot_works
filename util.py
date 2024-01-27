import time

from attr import dataclass


@dataclass
class TimeWorkFunction:
    def measure_execution_time(cls, func):
        start_time = time.time()
        print(
            f"Start функции: {time.strftime('%H:%M:%S', time.localtime(start_time))} "
        )
        # Call the function
        func()

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Время выполнения функции: {execution_time:.2f} секунд")

        return cls(start_time, end_time, execution_time)
