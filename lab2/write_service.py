from socket import *


class Arquivo:
    def __init__(self):
        self.nome = "dicionario.txt"
    
    def escrever(self, data):
        arquivo = open(self.nome, "a")
        arquivo.write(data.decode('utf-8') + "\n")
        arquivo.close()
        print("Mensagem escrita com sucesso!")
        return "Mensagem escrita com sucesso!"


class Server:
    '''Como não podemos ter mais de uma escrita no arquivo ao mesmo tempo, o servidor de escrita
    é implementado de maneira mais simples, sem o uso de threads ou de aceitar diversas conexões.
        Entrada: socket da conexao e endereco do cliente
        Saida: '''
    def __init__(self):
        self.HOST = 'localhost' # '' possibilita acessar qualquer endereco alcancavel da maquina local
        self.PORT = 6007 # porta onde chegarao as mensagens para essa aplicacao
        self.arquivo = Arquivo()

    def run(self):
        # cria um socket para comunicacao
        sock = socket()

        # vincula a interface e porta para comunicacao
        sock.bind((self.HOST, self.PORT))

        # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
        sock.listen(1)

        while True:
            # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
            (conn, addr) = sock.accept() 
        
            # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
            data = conn.recv(1024) 

            msg = self.arquivo.escrever(data)

            # envia mensagem de resposta
            conn.send(bytearray(msg, 'utf-8')) 

            # fecha o socket da conexao
            conn.close()



# Cria servidor
server = Server()
server.run()