#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multiplexacao do processamento (atende mais de um cliente com select)
import socket
import select
import sys

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]

class Client:
    def __init__(self, port):
        self.HOST = 'localhost' # maquina onde esta o par passivo
        self.PORT = port
        self.sock = self.conecatar()

    def conecatar(self):
        # cria socket
        sock = socket.socket()
        # conecta-se com o par passivo
        sock.connect((self.HOST, self.PORT))

        return sock
    
    def desconectar(self):
        self.sock.close()

    def enviar(self, data):
        self.sock.send(bytearray(data, 'utf-8'))

    def receber(self):
        return self.sock.recv(1024).decode('utf-8')


class Server:
    def __init__(self):
        # define a localizacao do servidor
        self.HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
        self.PORT = 5006 # porta de acesso
        self.proxy = Proxy() # instancia o proxy
        
        #armazena as conexoes ativas
        self.conexoes = {}
        self.sock = self.iniciaServidor()
    
    def enviar(self, data):
        self.sock.send(bytearray(data, 'utf-8'))

    def receber(self):
        data = self.sock.recv(1024)
        if data:
            return data.decode('utf-8')
        return None


    def iniciaServidor(self):
        '''Cria um socket de servidor e o coloca em modo de espera por conexoes
        Saida: o socket criado'''
        # cria o socket 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

        # vincula a localizacao do servidor
        sock.bind((self.HOST, self.PORT))

        # coloca-se em modo de espera por conexoes
        sock.listen(5) 

        # configura o socket para o modo nao-bloqueante
        sock.setblocking(False)
        
        # inclui o socket principal na lista de entradas de interesse
        entradas.append(sock)

        return sock

    def aceitaConexao(self):
        '''Aceita o pedido de conexao de um cliente
        Saida: o novo socket da conexao e o endereco do cliente'''

        # estabelece conexao com o proximo cliente
        clisock, endr = self.sock.accept()

        # configura o socket para o modo nao-bloqueante
        clisock.setblocking(False)

        # inclui o socket principal na lista de entradas de interesse
        entradas.append(clisock)

        # registra a nova conexao
        self.conexoes[clisock] = endr

        return clisock, endr

    def encerraConexaoComCliente(self, clisock):
        print(str(self.conexoes[clisock]) + '-> encerrou')
        del self.conexoes[clisock] #retira o cliente da lista de conexoes ativas
        entradas.remove(clisock) #retira o socket do cliente das entradas do select
        clisock.close() # encerra a conexao com o cliente

    def enviarParaCliente(self, clisock, data):
        '''Envia dados para o cliente
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        # envia mensagem de resposta
        clisock.send(bytearray(data, 'utf-8'))
    
    def receberDoCliente(self, clisock):
        '''Recebe dados do cliente
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        #recebe dados do cliente
        data = clisock.recv(1024)

        if not data: # dados vazios: cliente encerrou
            return None
        
        return data.decode('utf-8')


    def atendeRequisicoes(self, clisock):
        '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        #recebe dados do cliente
        data = self.receberDoCliente(clisock)

        if not data: # dados vazios: cliente encerrou
            self.encerraConexaoComCliente(clisock)
            return

        print(str(self.conexoes[clisock]) + ': ' + data)

        response = self.proxy.redirecionar(data) # redireciona a requisicao para o proxy

        self.enviarParaCliente(clisock, response) # ecoa os dados para o cliente

    def fechaServidor(self):
        '''Fecha o socket do servidor'''
        if not self.conexoes: #somente termina quando nao houver clientes ativos
            self.sock.close()
            sys.exit()
        else: 
            print("ha conexoes ativas")


class Proxy:

    def __init__(self):
        self.READ_PORT = 6007 # Porta do servidor de leitura
        self.WRITE_PORT = 6008 # Porta do servidor de escrita
        self.DELETE_PORT = 6009 # Porta do servidor de deletar

    '''
    Redireciona a requisicao para o servidor correto

    Entrada: a requisicao em string
    Saida: a resposta do servidor em string
    '''
    def redirecionar(self, data):
        cliente = None

        method = data.split(' ')[0]
        if method == 'DELETE':
            client = Client(self.DELETE_PORT)
        elif method == 'GET':
            client = Client(self.READ_PORT)
        elif method == 'POST':
            client = Client(self.WRITE_PORT)
        else:
            return 'Metodo nao suportado'

        client.enviar(data)

        return client.receber()
        

def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
    server = Server()
    print("Pronto para receber conexoes...")
    while True:
        #espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])

        #tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == server.sock:  #pedido novo de conexao
                clisock, endr = server.aceitaConexao()
                print ('Conectado com: ', endr)

            elif pronto == sys.stdin: #entrada padrao
                cmd = input()
                if cmd == 'fim': #solicitacao de finalizacao do servidor
                    server.fechaServidor()
                elif cmd == 'deletar': #solitacao de deletar uma chave
                    print('Qual chave deseja deletar?')
                    chave = input()
                    data = f"DELETE {chave}"
                    msg = server.proxy.redirecionar(data)
                    print(msg)
                elif cmd == 'hist': #outro exemplo de comando para o servidor
                    print(str(conexoes.values()))
            else: #nova requisicao de cliente
                server.atendeRequisicoes(pronto)

main()