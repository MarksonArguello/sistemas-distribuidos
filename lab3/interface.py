import rpyc

class Interface:
    def __init__(self):
        self.connection = rpyc.connect("localhost", port=18861)
        self.dicionario_service = self.connection.root

    def imprime_menu(self):
        print()
        print("Escolha uma opção:")
        print("1 - Inserir definicao")
        print("2 - Consultar palavra")
        print("3 - Sair")

        cmd = input()
        print()

        return cmd
    
    def inserir_definicao(self):
        print("Digite a chave: ")
        chave = input()
        print("Digite o valor: ")
        valor = input()

        return (chave, valor)

    def consultar_palavra(self):
        print("Digite a chave: ")
        valores = input()

        return valores

    def run(self):
        while True:
            # Impressao do menu
            opcao = self.imprime_menu()
            msg = ""

            if opcao == '1':
                # recebe o valor e a chave
                data = self.inserir_definicao()

                msg = self.dicionario_service.inserir(data)

            elif opcao == '2':
                # recebe a chave
                data = self.consultar_palavra()
                # envia mensagem para o par conectado 
                msg = self.dicionario_service.consultar(data)

            elif opcao == '3':
                # Termina execucao do cliente
                print("Saindo...")
                self.connection.close()
                break

            else:
                print("Opção inválida")
                continue
            print()
            print(msg)

# Cria cliente
aplicacao_cliente = Interface()
aplicacao_cliente.run()