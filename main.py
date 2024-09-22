import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.__endereco = endereco
        self.__contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.__contas.append(conta)
        return conta

    # Getter para o endereço
    @property
    def endereco(self):
        return self.__endereco
    
    @property
    def contas(self):
        return self.__contas

    def __str__(self):
        return f"Endereco: {self.__endereco}"

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.__nome = nome
        self.__data_nascimento = data_nascimento
        self.__cpf = cpf

    # Getters para os atributos privados
    @property
    def nome(self):
        return self.__nome

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    @property
    def cpf(self):
        return self.__cpf
    
    def __str__(self):
        return (f"Nome: {self.nome}\n"
                f"Data_nascimento: {self.data_nascimento}\n"
                f"Cpf: {self.get_cpf()}\n"
                f"Endereco: {self.endereco}")

class Conta:
    def __init__(self, cliente, numero):
        self.__cliente = cliente
        self.__agencia = "0001"
        self.__numero = numero
        self.__saldo = 0
        self.__historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(cliente, numero)

    @property
    def cliente(self):
        return self.__cliente

    @property
    def agencia(self):
        return self.__agencia

    @property
    def numero(self):
        return self.__numero

    @property
    def saldo(self):
        return self.__saldo

    @property
    def historico(self):
        return self.__historico

    def depositar(self, valor):
        if valor > 0:
            self.__saldo += valor
            self.__historico.adicionar_transacao(f"Depósito de R${valor:.2f}")
            print("\n+++ Depósito realizado com sucesso +++")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

    def sacar(self, valor):
        if self.__saldo >= valor:
            self.__saldo -= valor
            self.__historico.adicionar_transacao(f"Saque de R${valor:.2f}")
            print("\n+++ Saque realizado com sucesso +++")
            return True
        else:
            print("\n@@@ Operação falhou! Saldo insuficiente. @@@")
            return False

class ContaCorrente(Conta):
    def __init__(self, cliente, numero, limite=500, limite_saques=3):
        super().__init__(cliente, numero)
        self.__limite = limite
        self.__limite_saques = limite_saques
    
    @property
    def limite(self):
        return self.__limite
    @property
    def limite_saques(self):
        return self.__limite_saques

    def sacar(self, valor):
        if self.__limite_saques > 0 and valor <= self.__limite:
            return super().sacar(valor)
        elif self.__limite_saques <= 0:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        elif valor > self.__limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        else:
            return False

    def __str__(self):
        return f"Agência: {self.agencia}, Número: {self.numero}, Saldo: {self.saldo}"


class Historico:
    def __init__(self):
        self.__transacoes = []

    @property
    def transacoes(self):
        return self.__transacoes

    def adicionar_transacao(self, transacao):
        self.__transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "transacao": transacao,
                "data": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            }
        )


class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

    @staticmethod
    def data_hora_atual():
        return datetime.now()

    @staticmethod
    def valor_decimal(valor):
        return float(valor)


    def __str__(self):
        return f"{self.data_hora} - {self.valor}"


class Saque(Transacao):
    def __init__(self, valor):
        self.__valor = self.valor_decimal(valor)
        self.__data_hora = self.data_hora_atual()

    @property
    def valor(self):
        return self.__valor

    @property
    def data_hora(self):
        return self.__data_hora

    def registrar(self, conta):
        if conta.sacar(self.__valor):
            self.__data_hora = self.data_hora_atual()
        else:
            raise ValueError("Saldo insuficiente")


class Deposito(Transacao):
    def __init__(self, valor):
        self.__valor = self.valor_decimal(valor)
        self.__data_hora = self.data_hora_atual()

    @property
    def valor(self):
        return self.__valor

    @property
    def data_hora(self):
        return self.__data_hora

    def registrar(self, conta):
        conta.depositar(self.__valor)
        self.__data_hora = self.data_hora_atual()


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [nu]\tNovo usuário
    [lc]\tListar contas
    [lu]\tListar usuários
    [q]\tSair
    
     -> """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def filtrar_conta(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = filtrar_conta(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = filtrar_conta(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


# Função exibir_extrato corrigida
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = filtrar_conta(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    if len(conta.historico.transacoes) == 0:
        print("Nenhuma transação realizada.")
    else:
        for transacao in conta.historico.transacoes:
            print(transacao.data)
            print("\t\t",transacao.transacao)
    print(f"\nSaldo atual: R${conta.saldo:.2f}")

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Cliente já existe! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input(
        "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): "
    )

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )
    clientes.append(cliente)

    print("\n+++ Cliente criado com sucesso! +++")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n+++ Conta criada com sucesso! +++")


def listar_contas(contas):
    if len(contas) == 0:
        print("\n@@@ Não há contas cadastradas! @@@")

    for conta in contas:
        print("+" * 100)
        print(textwrap.dedent(str(conta)))


def listar_usuarios(clientes):
    for cliente in clientes:
        print("+" * 100)
        print(textwrap.dedent(str(cliente)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "lu":
            listar_usuarios(clientes)
        elif opcao == "q":
            break
        else:
            print(
                "\n@@@ Operação inválida, por favor, selecione novamente a operação desejada. @@@"
            )


if __name__ == "__main__":
    main()
