from socket import *

class Aplicacao:
    def __init__(self):
        self.client = Client()

    def imprime_menu(self):
        print("Escolha uma opção:")
        print("1 - Inserir definicao")
        print("2 - Consultar palavra")
        print("3 - Sair")
        return input()
    
    def inserir_definicao(self):
        print("Digite a chave: ")
        chave = input()
        print("Digite o valor: ")
        valor = input()

        # Retorna a chave e o valor concatenadas no formato chave::valor
        return chave + "::" + valor

    def consultar_palavra(self):
        print("Digite a chave: ")
        palavra = input()
        return palavra
    
    def run(self):
        while True:
            # Impressao do menu
            opcao = self.imprime_menu()

            if opcao == '1':
                # recebe a definicao
                data = self.inserir_definicao()
                # envia mensagem para o par conectado 
                self.client.enviar(data)

            elif opcao == '2':
                # recebe a chave
                data = input()
                # envia mensagem para o par conectado 
                self.client.enviar(data)

            elif opcao == '3':
                # Termina o loop
                break

            else:
                print("Opção inválida")
                continue
            
            # imprime a mensagem recebida
            print(self.client.receber())

class Client:

    def __init__(self):
        self.HOST = 'localhost' # maquina onde esta o par passivo
        self.PORT = 5006 # porta que o par passivo esta escutando
        self.sock = self.conecatar()

    def conecatar(self):
        # cria socket
        sock = socket()
        # conecta-se com o par passivo
        sock.connect((self.HOST, self.PORT))

        return sock
    
    def desconectar(self):
        self.sock.close()

    def enviar(self, data):
        self.sock.send(bytearray(data, 'utf-8'))

    def receber(self):
        return self.sock.recv(1024).decode('utf-8')

# Cria cliente
aplicacao_cliente = Aplicacao()
aplicacao_cliente.run()