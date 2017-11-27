import uuid
from queue import Queue
from threading import Thread


class Process:

    PROGRESS = 'PROGRESS'
    ERROR_INTERNAL = 'AN_INTERNAL_ERROR_OCCURRED_AND_WE_ARE_SORRY_FOR_THE_INCONVENIENCE'
    ERROR_UPSTREAM = 'AN_UPSTREAM_ERROR_OCCURRED_AND_THEIR_SERVER_SAID_THEY_ARE_SORRY'

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
            if 400 <= response.status_code < 500:
                result = self.ERROR_INTERNAL
            elif 500 <= response.status_code < 600:
                result = self.ERROR_UPSTREAM
            else:
                result = response.text
            queue.put((process_id, result))
        return _handler

    def retrieve(self, process_id):
        if process_id not in self._processes:
            return None
        process = self._processes[process_id]
        del self._processes[process_id]
        return process
