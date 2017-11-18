import uuid
from queue import Queue
from threading import Thread


class Process:
    def __init__(self, session, sourcebox_url, sourcebox_account_name, sourcebox_user_name, sourcebox_password):
        self._processes = {}
        self._process_queue = Queue()
        self._session = session
        self._sourcebox_url = sourcebox_url
        self._sourcebox_account_name = sourcebox_account_name
        self._sourcebox_user_name = sourcebox_user_name
        self._sourcebox_password = sourcebox_password

        worker = Thread(target=self._process_queue_worker,
                        args=(self._process_queue,))
        worker.setDaemon(True)
        worker.start()

    def _process_queue_worker(self, queue):
        while True:
            process_id, profile = queue.get()
            self._processes[process_id] = profile
            queue.task_done()

    def submit(self, document):
        process_id = str(uuid.uuid4())
        self._processes[process_id] = 'PROGRESS'
        self._session.post(self._sourcebox_url, data={
            'account': self._sourcebox_account_name,
            'username': self._sourcebox_user_name,
            'password': self._sourcebox_password,
        }, files={
            'uploaded_file': document,
        }, params={
            'useHttpErrorCodes': 'true',
            'useJsonErrorMsg': 'true',
        }, background_callback=self._handle_submit_response(process_id))
        return process_id

    def _handle_submit_response(self, process_id):
        queue = self._process_queue

        def _handler(session, response):
            queue.put((process_id, response.text))
        return _handler

    def retrieve(self, process_id):
        if process_id not in self._processes:
            return None
        return self._processes[process_id]
