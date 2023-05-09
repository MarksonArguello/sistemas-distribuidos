from socket import *


class Arquivo:
    def __init__(self):
        self.nome = "dicionario.txt"
    
    def deletar(self, data):

        chave = data

        with open(self.nome, 'r+') as fp:
            # read an store all lines into list
            lines = fp.readlines()
            # move file pointer to the beginning of a file
            fp.seek(0)
            # truncate the file
            fp.truncate()

            for line in lines:
                if line.split("::")[0].lower() != chave.lower():
                    fp.write(line)


        print("{" + chave + "} deletado com sucesso!")
        return "Deletado com sucesso!"


class Server:

    def __init__(self):
        self.HOST = 'localhost' # '' possibilita acessar qualquer endereco alcancavel da maquina local
        self.PORT = 6009 # porta onde chegarao as mensagens para essa aplicacao
        self.arquivo = Arquivo()

    def run(self):
        print("Pronto para receber conexoes...")
        
        # cria um socket para comunicacao
        sock = socket()

        # vincula a interface e porta para comunicacao
        sock.bind((self.HOST, self.PORT))

        # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
        sock.listen(1)

        while True:
            # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
            (conn, addr) = sock.accept() 

            print ('Conectado com: ', addr)
        
            # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
            data = conn.recv(1024) 

            msg = self.arquivo.deletar(data.decode('utf-8'))

            # envia mensagem de resposta
            conn.sendall(bytearray(msg, 'utf-8')) 

            # fecha o socket da conexao
            conn.close()

            print ('Desconectou com: ', addr)



# Cria servidor
server = Server()
server.run()