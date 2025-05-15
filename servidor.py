import socket
import json
import threading
from queue import Queue

class Server:
    def __init__(self, host='172.28.173.86', port=5000):
        self.host = host
        self.port = port
        self.clients = {}
        self.message_queue = Queue()
        self.setup_server()

    def setup_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.port}")

        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

        process_thread = threading.Thread(target=self.process_messages)
        process_thread.daemon = True
        process_thread.start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.socket.accept()
            print(f"Conexão estabelecida com {client_address}")

            thread = threading.Thread(
                target=self.receive_messages,
                args=(client_socket,)
            )
            thread.daemon = True
            thread.start()

    def receive_messages(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.message_queue.put((client_socket, message))
            except:
                break

        for username, socket in list(self.clients.items()):
            if socket == client_socket:
                del self.clients[username]
                print(f"{username} desconectado")
                break

    def process_messages(self):
        while True:
            client_socket, message = self.message_queue.get()
            
            if message['type'] == 'register':
                self.handle_register(client_socket, message)
            elif message['type'] == 'message':
                self.handle_message(message)
            elif message['type'] == 'calculation':
                self.handle_calculation(client_socket, message)

    def handle_register(self, client_socket, message):
        username = message['username']
        self.clients[username] = client_socket
        print(f"Usuário registrado: {username}")
        response = {'status': 'success', 'message': 'Registro bem-sucedido'}
        client_socket.send(json.dumps(response).encode('utf-8'))

    def handle_message(self, message):
        sender = message['sender']
        recipient = message['recipient']
        content = message['content']
        
        if recipient in self.clients:
            recipient_socket = self.clients[recipient]
            response = {
                'type': 'message',
                'sender': sender,
                'content': content
            }
            recipient_socket.send(json.dumps(response).encode('utf-8'))
        else:
            if sender in self.clients:
                sender_socket = self.clients[sender]
                response = {
                    'status': 'error',
                    'message': f'Destinatário {recipient} não encontrado'
                }
                sender_socket.send(json.dumps(response).encode('utf-8'))

    def handle_calculation(self, client_socket, message):
        try:
            num1 = float(message['num1'])
            num2 = float(message['num2'])
            operation = message['operation']
            
            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                if num2 == 0:
                    raise ZeroDivisionError("Divisão por zero")
                result = num1 / num2
            else:
                raise ValueError("Operação inválida")
            
            response = {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
        
        client_socket.send(json.dumps(response).encode('utf-8'))

if __name__ == "__main__":
    server = Server()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor encerrado")