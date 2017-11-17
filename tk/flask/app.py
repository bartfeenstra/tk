from flask import Flask


class App(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__('tk', *args, **kwargs)
        self._register_routes()

    def _register_routes(self):
        @self.route('/submit', methods=['POST'])
        def submit():
            return 'SUBMITTED'

        @self.route('/retrieve/<id>')
        def retrieve(id):
            return id
