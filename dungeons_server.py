import threading, socket, signal, sys, time, re, string
import dungeon_enemies
import logger

class PDPYServer:
    _last_result = None
    def __init__(self, port, game):
        logger.info(f'Binding to port {port}...', 'PDPYServer')
        self.listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen.bind(('localhost', port))
        logger.info(f'Listening on port {port}...', 'PDPYServer')
        self.listen.listen(1)
        self.sockets = []
        self.game = game
        self.running = True
        #signal.signal(signal.SIGINT, self.signal_handle)
        #signal.signal(signal.SIGTERM, self.signal_handle)

    def run(self):
        while self.running:
            try:
                (sock, address) = self.listen.accept()
            except socket.error:
                #print('Limit reached! Server quitting...')
                return
            self.sockets.append(sock)
            logger.info(f'Found a client (address={address})', 'PDPYServer')
            cthread = ClientListener(self, sock, address)
            cthread.start()
            time.sleep(0.1)

    def recieve(self, data, listener):
        logger.info(f'Recieved data {data}', 'PDPYServer')
        if re.match('^POST ', data):
            data = data[5:]
            self.game.message(data)
        elif re.match('^ADDENEMY ', data):
            data = data[9:]
            d = data.split(' ')
            enem, x, y = d[:-2], d[-2], d[-1]
            l = []
            for i in enem:
                l.append(string.capwords(i))
            enem = ''.join(l)
            try:
                enemy = getattr(dungeon_enemies, enem)
                self.game.enemies.append(enemy(int(x), int(y)))
            except Exception as e:
                print('Error - ' + str(e))
        elif re.match('^GETHEALTH', data):
            #PDPYServer._last_result = self.game.player
            listener.socket.sendall(str(self.game.player.hp).encode('utf-8'))
        elif re.match('^SETHEALTH ', data):
            data = data[10:]
            self.game.player.hp = int(float(data))
        elif re.match('^GETPOS', data):
            listener.socket.sendall(str(self.game.player.rect.x).encode('utf-8'))
            time.sleep(0.15)
            listener.socket.sendall(str(self.game.player.rect.y).encode('utf-8'))
        elif re.match('^SETPOS ', data):
            data = data[7:]
            x, y = data.split(' ')
            x, y = (int(float(x)), int(float(y)))
            self.game.player.rect.x = x
            self.game.player.rect.y = y
        else:
            logger.error('Unrecognized: ' + data, 'PDPYServer')

    def remove(self, sock, address):
        self.sockets.remove(sock)
        logger.info(f'Address {address} quitting', 'PDPYServer')

    def signal_handle(self, signal, frame):
        self.listen.close()
        logger.info(f'Closing server', 'PDPYServer')
        sys.exit(1)

    def stop(self):
        self.running = False
        self.listen.close()
        logger.info(f'Closing server', 'PDPYServer')

class ClientListener(threading.Thread):
    def __init__(self, server, sock, address):
        super().__init__(daemon=True)
        self.server = server
        self.address = address
        self.socket = sock
        self.listening = True

    def run(self):
        while self.listening:
            data = ""
            try:
                data = self.socket.recv(1024)
            except socket.error:
                continue
            self.handle_msg(data)
            time.sleep(0.1)

    def quit(self):
        self.listening = False
        self.socket.close()
        self.server.remove(self.socket, self.address)

    def handle_msg(self, data):
        data = data.decode('utf-8')
        self.server.recieve(data, self)

if __name__ == '__main__':
    server = PDPYServer(28135, None)
    server.run()
