from socket import *

class Server:
    def __init__(self):
        self.HOST = 'localhost' # '' possibilita acessar qualquer endereco alcancavel da maquina local
        self.PORT = 5006 # porta onde chegarao as mensagens para essa aplicacao

    def run(self):
        # cria um socket para comunicacao
        sock = socket()

        # vincula a interface e porta para comunicacao
        sock.bind((self.HOST, self.PORT))

        # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
        sock.listen(1)

        # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
        (conn, addr) = sock.accept() 

        while True:
            # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
            msg = conn.recv(1024) 

            if not msg: break

            # envia mensagem de resposta
            conn.send(msg) 

        # fecha o socket da conexao
        conn.close()



# Cria servidor
server = Server()
server.run()