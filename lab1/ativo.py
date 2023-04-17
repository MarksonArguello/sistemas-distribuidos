from socket import *

class Client:
    def __init__(self):
        self.HOST = 'localhost' # maquina onde esta o par passivo
        self.PORT = 5006 # porta que o par passivo esta escutando

    def run(self):
        # cria socket
        sock = socket()

        # conecta-se com o par passivo
        sock.connect((self.HOST, self.PORT))

        while True:
            # recebe mensagem do usuario
            data = input()

            # verifica se eh a mensagem de fim
            if data.lower() == 'fim': 
                break

             # envia mensagem para o par conectado 
            sock.send(bytearray(data, 'utf-8'))

            # espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
            data = sock.recv(1024)

            # imprime a mensagem recebida
            print(data.decode('utf-8'))

        # encerra a conexao
        sock.close()

# Cria cliente
client = Client()
client.run()