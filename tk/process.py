import uuid


class Process:
    def __init__(self):
        self._processes = {}

    def submit(self):
        process_id = str(uuid.uuid4())
        self._processes[process_id] = 'PROGRESS'
        return process_id

    def retrieve(self, process_id):
        if process_id not in self._processes:
            return None
        return self._processes[process_id]
