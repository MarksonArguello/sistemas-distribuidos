#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multiplexacao do processamento (atende mais de um cliente com select)
import socket
import select
import sys
import threading

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
        self.sock.sendall(bytearray(data, 'utf-8'))

    def receber(self):
        return self.sock.recv(1024).decode('utf-8')


class Monitor:
    '''
    Monitor para impedir que mais de um cliente faça conexao com o servidor de deletar e inserir ao mesmo tempo
    Diversas conexoes ao servidor de consultar podem ser feitas ao mesmo tempo
    '''
    def __init__(self):
        self.leitores = 0
        self.escritores = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(lock=self.lock)

    def entraLeitor (self):
        self.condition.acquire()
        while self.escritores > 0:
            self.condition.wait()
        
        self.leitores += 1
        self.condition.release()


    def saiLeitor (self):
        self.condition.acquire()
        self.leitores -= 1
        self.condition.notify()
        self.condition.release()
        

    def entraEscritor (self):
        self.condition.acquire()
        while self.escritores > 0 or self.leitores > 0:
            self.condition.wait()
        
        self.escritores += 1
        self.condition.release()
    
    def saiEscritor (self):
        self.condition.acquire()
        self.escritores -= 1
        self.condition.notify_all()
        self.condition.release()




class Server:
    def __init__(self):
        # define a localizacao do servidor
        self.HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
        self.PORT = 5006 # porta de acesso
        self.proxy = Proxy() # instancia o proxy
        self.lock_dicionarios = threading.Lock() #lock para acesso do dicionario 'conexoes'
        
        #armazena as conexoes ativas
        self.conexoes = {}
        self.sock = self.iniciaServidor()
    
    def enviar(self, data):
        self.sock.sendall(bytearray(data, 'utf-8'))

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

       
        self.lock_dicionarios.acquire()
        # inclui o socket principal na lista de entradas de interesse
        entradas.append(clisock)

        # registra a nova conexao
        self.conexoes[clisock] = endr
        self.lock_dicionarios.release()

        cliente = threading.Thread(target=self.atendeRequisicoes, args=(clisock,))
        cliente.start()

        return clisock, endr

    def encerraConexaoComCliente(self, clisock):
        print(str(self.conexoes[clisock]) + '-> encerrou')
        self.lock_dicionarios.acquire()
        del self.conexoes[clisock] #retira o cliente da lista de conexoes ativas
        entradas.remove(clisock) #retira o socket do cliente das entradas do select
        self.lock_dicionarios.release()
        clisock.close() # encerra a conexao com o cliente

    def enviarParaCliente(self, clisock, data):
        '''Envia dados para o cliente
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        # envia mensagem de resposta
        clisock.sendall(bytearray(data, 'utf-8'))
    
    def receberDoCliente(self, clisock):
        '''Recebe dados do cliente
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        #recebe dados do cliente
        data = clisock.recv(1024)

        if not data: # dados vazios: cliente encerrou
            return
        
        return data.decode('utf-8')


    def atendeRequisicoes(self, clisock):
        '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida: '''

        while True:
            #recebe dados do cliente
            data = self.receberDoCliente(clisock)           

            if not data: # dados vazios: cliente encerrou
                self.encerraConexaoComCliente(clisock)
                return

            print(str(self.conexoes[clisock]) + ': ' + data)

            response = self.proxy.redirecionar(data) # redireciona a requisicao para o proxy

            self.enviarParaCliente(clisock, response) # ecoa os dados para o cliente

        
    def deletar(self):
        print('Qual chave deseja deletar?')
        chave = input()
        data = f"DELETE {chave}"
        msg =self.proxy.redirecionar(data)
        print(msg)

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
        self.monitor = Monitor()

    '''
    Redireciona a requisicao para o servidor correto

    Entrada: a requisicao em string
    Saida: a resposta do servidor em string
    '''
    def redirecionar(self, data):

        cliente = None
        response = None

        metodo, chave_valor = data.split(' ', 1)

        if metodo == 'DELETE':
            self.monitor.entraEscritor()

            client = Client(self.DELETE_PORT)
            client.enviar(chave_valor)
            response = client.receber()

            self.monitor.saiEscritor()

        elif metodo == 'GET':
            self.monitor.entraLeitor()

            client = Client(self.READ_PORT)
            client.enviar(chave_valor)
            response = client.receber()

            self.monitor.saiLeitor()

        elif metodo == 'POST':
            self.monitor.entraEscritor()

            client = Client(self.WRITE_PORT)
            client.enviar(chave_valor)
            response = client.receber()

            self.monitor.saiEscritor()

        else:
            return 'Metodo nao suportado'

        
        return response

def main():
    '''Inicializa e implementa o loop principal (infinito) do servidor'''
    server = Server()
    print("Pronto para receber conexoes...")
    while True:
        #espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        #print(str(leitura))
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
                    administrador = threading.Thread(target=server.deletar)
                    administrador.start()
                elif cmd == 'hist': #outro exemplo de comando para o servidor
                    print(str(conexoes.values()))

                
main()