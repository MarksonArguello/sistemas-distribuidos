from socket import *


class Arquivo:
    def __init__(self):
        self.nome = "dicionario.txt"
    
    # Retorna todos os valores para a chave recebida
    def ler(self, data):
        chave = data

        valores = []
        with open(self.nome, 'r') as f:
            for linha in f:
                if linha.split("::")[0].lower() == chave.lower():
                    valores.append(linha.split("::")[1].strip("\n "))

        # Ordena os valores
        valores.sort()

        if len(valores) > 0:
            print(f"Chave {chave} encontrada")
            return ",".join(valores)

        print (f"Chave {chave} não encontrada")
        return "Chave não encontrada"

        


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
        print("Pronto para receber conexoes...")
        
        # cria um socket para comunicacao
        sock = socket()

        # vincula a interface e porta para comunicacao
        sock.bind((self.HOST, self.PORT))

        # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
        sock.listen(5)

        while True:
            # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
            (conn, addr) = sock.accept()

            print ('Conectado com: ', addr)
        
            # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
            data = conn.recv(1024)

            msg = self.arquivo.ler(data.decode('utf-8'))

            # envia mensagem de resposta
            conn.sendall(bytearray(msg, 'utf-8')) 

            # fecha o socket da conexao
            conn.close()

            print ('Desconectou com: ', addr)




# Cria servidor
server = Server()
server.run()