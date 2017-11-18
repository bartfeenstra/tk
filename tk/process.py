import uuid

import requests


class Process:
    def __init__(self, sourcebox_url, sourcebox_account_name, sourcebox_user_name, sourcebox_password):
        self._processes = {}
        self._sourcebox_url = sourcebox_url
        self._sourcebox_account_name = sourcebox_account_name
        self._sourcebox_user_name = sourcebox_user_name
        self._sourcebox_password = sourcebox_password

    def submit(self, document):
        process_id = str(uuid.uuid4())
        self._processes[process_id] = 'PROGRESS'
        # @todo Add async support in a follow-up.
        response = requests.post(self._sourcebox_url, data={
            'account': self._sourcebox_account_name,
            'username': self._sourcebox_user_name,
            'password': self._sourcebox_password,
        }, files={
            'uploaded_file': document,
        }, params={
            'useHttpErrorCodes': 'true',
            'useJsonErrorMsg': 'true',
        })
        self._processes[process_id] = response.text
        return process_id

    def retrieve(self, process_id):
        if process_id not in self._processes:
            return None
        return self._processes[process_id]
