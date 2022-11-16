import socket
import dungeons_server
import time
import threading

__all__ = ['Interface']

class Interface:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect(('localhost', 28135))
        except socket.error as e:
            if e.errno == 10061: raise ConnectionRefusedError('Could not find any instance of PyDungeons running!')
            else: raise Exception('Unrecognized Server Unavailable Exception - ' + str(e))
        self._res = None
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(*self):
        self = self[0]
        while self._running:
            data = b''
            try:
                data = self._sock.recv(1024)
            except socket.error:
                print('Server closed!')
                self._running = False
                return
            self._res = data.decode('utf-8')
            time.sleep(0.1)

    def _send(self, msg):
        try:
            self._sock.sendall(msg.encode('utf-8'))
        except socket.error as e:
            if e.errno == 10054:
                raise ConnectionResetError('Disconnected from server!')
            else:
                raise Exception('Unrecognized Server Reset Exception - ' + e)

    @property
    def _result(self):
        try:
            return int(float(self._res))
        except:
            return self._res

    '''@result.setter
    def result(self, x):
        self._res = x'''

    def post(self, what):
        self._send('POST ' + what)

    def add_enemy(self, enemy, x, y):
        self._send('ADDENEMY ' + enemy + ' ' + str(x) + ' ' + str(y))

    def get_player_hp(self):
        self._send('GETHEALTH')
        time.sleep(0.1)
        return self._result

    def set_player_hp(self, hp):
        self._send('SETHEALTH ' + str(hp))

    def get_player_pos(self):
        self._send('GETPOS')
        time.sleep(0.1)
        x = self._result
        time.sleep(0.1)
        return (x, self._result)

    def set_player_pos(self, x, y):
        self._send('SETPOS ' + str(x) + ' ' + str(y))
