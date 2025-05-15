import socket
import json
import threading

class Client:
    def __init__(self, host='172.28.173.86', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.connected = False

    def connect(self, username):
        try:
            self.socket.connect((self.host, self.port))
            self.username = username
            self.connected = True
            
            # Enviar registro
            register_message = {
                'type': 'register',
                'username': username
            }
            self.socket.send(json.dumps(register_message).encode('utf-8'))
            
            # Thread para receber mensagens
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    self.connected = False
                    break
                
                message = json.loads(data)
                self.handle_message(message)
            except:
                self.connected = False
                break

    def handle_message(self, message):
        if 'type' in message and message['type'] == 'message':
            print(f"\n[Mensagem de {message['sender']}]: {message['content']}\n> ", end='')
        elif 'status' in message:
            if message['status'] == 'success' and 'result' in message:
                print(f"\n[Resultado]: {message['result']}\n> ", end='')
            elif message['status'] == 'error':
                print(f"\n[Erro]: {message['message']}\n> ", end='')

    def send_message(self, recipient, content):
        if not self.connected:
            print("Não conectado ao servidor")
            return False
        
        message = {
            'type': 'message',
            'sender': self.username,
            'recipient': recipient,
            'content': content
        }
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            return True
        except:
            self.connected = False
            return False

    def send_calculation(self, num1, num2, operation):
        if not self.connected:
            print("Não conectado ao servidor")
            return False
        
        message = {
            'type': 'calculation',
            'num1': num1,
            'num2': num2,
            'operation': operation
        }
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            return True
        except:
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False
        self.socket.close()

def main():
    print("=== Cliente de Chat e Cálculo Remoto ===")
    username = input("Digite seu nome de usuário: ")
    
    client = Client()
    if not client.connect(username):
        print("Falha ao conectar ao servidor")
        return
    
    print("\nConectado ao servidor. Comandos disponíveis:")
    print("  /msg <destinatário> <mensagem> - Enviar mensagem")
    print("  /calc <operação> <num1> <num2> - Realizar cálculo (add, subtract, multiply, divide)")
    print("  /quit - Sair")
    
    try:
        while client.connected:
            command = input("> ").strip()
            
            if command.startswith("/msg "):
                parts = command[5:].split(maxsplit=1)
                if len(parts) == 2:
                    recipient, content = parts
                    client.send_message(recipient, content)
                else:
                    print("Uso: /msg <destinatário> <mensagem>")
            
            elif command.startswith("/calc "):
                parts = command[6:].split()
                if len(parts) == 3:
                    operation, num1, num2 = parts
                    try:
                        num1 = float(num1)
                        num2 = float(num2)
                        client.send_calculation(num1, num2, operation)
                    except ValueError:
                        print("Números inválidos")
                else:
                    print("Uso: /calc <operação> <num1> <num2>")
            
            elif command == "/quit":
                client.disconnect()
                print("Desconectado")
                break
            
            else:
                print("Comando inválido")
    except KeyboardInterrupt:
        client.disconnect()
        print("\nDesconectado")

if __name__ == "__main__":
    main()