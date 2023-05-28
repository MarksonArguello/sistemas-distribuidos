import rpyc
import sys
import select

from threading import Thread
from rpyc.utils.server import ThreadedServer

class Arquivo:
    def __init__(self):
        self.nome = "dicionario.txt"

    def escrever(self, dicionario):
        with open(self.nome, 'w') as arquivo:
            for chave in dicionario.keys():
                arquivo.write(chave + ':')
                arquivo.write(','.join(dicionario[chave]))
                arquivo.write('\n')

    def ler(self):
        dicionario = {}
        with open(self.nome, 'r') as arquivo:
            for linha in arquivo:
                if linha == '\n' or linha.strip() == '':
                    continue
                chave, valor = linha.strip().split(':')
                valor = valor.split(',')
                dicionario[chave] = valor

        return dicionario


class ProcessamentoService(rpyc.Service):
    def __init__(self):
        self.arquivo = Arquivo()
        self.dicionario = self.arquivo.ler()     
        self.conexoes = 0

    def on_connect(self, conn):
        print("Cliente conectado\n")
        self.conexoes += 1

    def on_disconnect(self, conn):
        print("Conexao perdida\n")
        self.conexoes -= 1

    def conxoes_ativas(self):
        return self.conexoes > 0

    def exposed_inserir(self, data):
        chave, valor = data
        print("Inserindo definicao")
        print("Chave: " + chave)
        print("Valor: " + valor)

        if chave in self.dicionario:
            self.dicionario[chave].append(valor)
        else:
            self.dicionario[chave] = [valor]

        self.dicionario[chave].sort()

        print("Definicao inserida com sucesso")
        print()

        return "Definicao inserida com sucesso"
    
    def exposed_consultar(self, chave):
        print("Consultando definicao")
        print("Chave: " + chave)

        if chave in self.dicionario:
            print("Definicao: " + str(self.dicionario[chave]))
            print()
        else:
            print("Definicao nao encontrada")
            print()
            return str([])        

        return str(self.dicionario[chave])

    def remover(self):
        print()
        print ("Qual a chave que deseja remover?")
        chave = input()
        print("Removendo definicao")
        print("Chave: " + chave)
        print()

        if chave in self.dicionario:
            del self.dicionario[chave]
            print("Definicao removida com sucesso")
        else:
            print("Definicao nao encontrada")
        
        print()


    def escrever_arquivo(self):
        print("Escrevendo no arquivo")
        self.arquivo.escrever(self.dicionario)


class Servidor:
    def __init__(self):
        #define a lista de I/O de interesse (jah inclui a entrada padrao)
        self.entradas = [sys.stdin]
        self.processamentoService = ProcessamentoService()

    def iniciaServidor(self):
        self.server = ThreadedServer(self.processamentoService, port=18861)
        self.server.start()

    def fechaServidor(self):
        print()
        if self.processamentoService.conxoes_ativas():
            print("Existem clientes conectados")
            print("Deseja realmente finalizar o servidor? (s/n)")
            resposta = input()
            print()
            if resposta != 's':
                return
                
        self.desconectar()
        

    def desconectar(self):
        self.processamentoService.escrever_arquivo()
        print("Finalizando servidor")
        self.server.close()
        sys.exit()


    def run(self):
        print("Iniciando servidor")
        print("Digite 'fim' para terminar o servidor")
        print("Digite 'deletar' para remover uma chave")
        print()

        t = Thread(target=self.iniciaServidor)
        t.start()
        print("Pronto para receber conexoes...")

        while True:
            #espera por qualquer entrada de interesse
            leitura, escrita, excecao = select.select(self.entradas, [], [])
            
            #tratar todas as entradas prontas
            for pronto in leitura:
                if pronto == sys.stdin: #entrada padrao
                    cmd = input()
                    if cmd == 'fim': #solicitacao de finalizacao do servidor
                        self.fechaServidor()
                    elif cmd == 'deletar': #solitacao de deletar uma chave
                        self.processamentoService.remover()
                    else:
                        print("Comando invalido")
                        print()

servidor = Servidor()
servidor.run()