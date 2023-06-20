from datetime import datetime
import pytz


class Client_Logger:
    def __init__(self, socketio):
        self.socketio = socketio

    def add_log(self, message, level="INFO"):
        timezone = pytz.timezone('Europe/Berlin')
        timestamp = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        log_data = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.socketio.emit('log_message', log_data)