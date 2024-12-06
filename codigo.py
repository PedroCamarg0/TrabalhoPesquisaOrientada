# Nome: Pedro Oliveira Camargo
# RA: 231026188

# Código feito usando windows 11 e pip 24.3.1, executado no ambiente virtual python na pasta

from ortools.sat.python import cp_model
import matplotlib.pyplot as plt

import time


def main():

    # Dados do problema
    clientesCentro = {
        "C1": [(2,1), (0,3), (1,6), (3,7), (5,3), (4,6)],
        "C2": [(1,8), (2,5), (4,10), (5,10), (0,10), (3,4)],
        "C3": [(2,5), (3,4), (5,8), (0,9), (1,1), (4,7)],
        "C4": [(1,5), (0,5), (2,5), (3,3), (4,8), (5,9)],
        "C5": [(2,9), (1,3), (4,5), (5,4), (0,3), (3,1)],
        "C6": [(1,3), (3,3), (5,9), (0,10), (4,4), (2,1)],
    }

    maqCentro = [0, 1, 2, 3, 4, 5]

    clientesCompacta = {
        "C1": [(1,21), (0,53), (4,95), (3,55), (2,34)],
        "C2": [(0,21), (3,52), (4,16), (2,26), (1,71)],
        "C3": [(3,39), (4,98), (1,42), (2,31), (0,12)],
        "C4": [(1,77), (0,55), (4,79), (2,66), (3,77)],
        "C5": [(0,83), (3,34), (2,64), (1,19), (4,37)],
        "C6": [(1,54), (2,43), (4,79), (0,92), (3,62)],
        "C7": [(3,69), (4,77), (1,87), (2,87), (0,93)],
        "C8": [(2,38), (0,60), (1,41), (3,24), (4,83)],
        "C9": [(3,17), (1,49), (4,25), (0,44), (2,98)],
        "C10": [(4,77), (3,79), (2,43), (1,75), (0,96)]
    }

    maqCompacta = [0, 1, 2, 3, 4]
    
    
    # Escolha da unidade a ser consultada
    invalido=True
    while invalido==True:
        opc = int(input("Que unidade deseja obter o calendário?(Centro=1, Compacta=2)\n"))
        
        match opc:
            case 1:
                cronograma, makespan = resolve(clientesCentro, maqCentro)
                invalido=False
            case 2:
                cronograma, makespan = resolve(clientesCompacta, maqCompacta)
                invalido=False
            case _:
                print("Opção inválida.")
                invalido=True
    
    plotaGrafico(cronograma, makespan)
    
    return



def resolve(clientes, aparelhos):
    
    time_inicio = time.time()
    
    # Cria o modelo
    modelo = cp_model.CpModel()
    
    # Variáveis de decisão
    tasks = {}
    inicios = {}
    finais = {}
    intervalo = {}

    for cliente, lista_task in clientes.items():
        for ordem, (aparelho, duracao) in enumerate(lista_task):
            task = (cliente, ordem)
            inicios[task] = modelo.NewIntVar(0, 1000, f"start_{cliente}_{ordem}")
            finais[task] = modelo.NewIntVar(0, 1000, f"end_{cliente}_{ordem}")
            intervalo[task] = modelo.NewIntervalVar( inicios[task], duracao, finais[task], f"interval_{cliente}_{ordem}" )
            tasks[task] = (aparelho, duracao)

    # Restrição de ordem (um cliente deve seguir sua sequência de tarefas)
    for cliente, lista_task in clientes.items():
        for ordem in range(len(lista_task) - 1):
            modelo.Add(inicios[(cliente, ordem + 1)] >= finais[(cliente, ordem)])

    # Restrição de uso de máquinas (máquina só pode ser usada por um cliente por vez)
    aparelho_intervalos = {machine: [] for machine in aparelhos}
    for (cliente, ordem), (aparelho, duracao) in tasks.items():
        aparelho_intervalos[aparelho].append(intervalo[(cliente, ordem)])

    for aparelho, intervalos in aparelho_intervalos.items():
        modelo.AddNoOverlap(intervalos)

    # Minimizar o tempo total (makespan)
    makespan = modelo.NewIntVar(0, 1000, "makespan")
    modelo.AddMaxEquality(makespan, [finais[(cliente, len(tasks_list) - 1)] for cliente, tasks_list in clientes.items()])
    modelo.Minimize(makespan)

    # Resolve o problema
    solucao = cp_model.CpSolver()
    solucao.Solve(modelo)

    # Cria o cronograma e printa seus valores
    cronograma = {}
    print(f"Makespan: {solucao.Value(makespan)} minutos")
    for cliente, lista_task in clientes.items():
        cronograma[cliente] = []
        for ordem, (aparelho, duracao) in enumerate(lista_task):
            inicio = solucao.Value(inicios[(cliente, ordem)])
            fim = solucao.Value(finais[(cliente, ordem)])
            cronograma[cliente].append((aparelho, inicio, fim))
            print(f"{cliente} - Máquina {aparelho}: {inicio} -> {fim}")    
            
    time_fim = time.time()
    time_total = time_fim - time_inicio
    
    print(f"Tempo de execução: {time_total} segundos")
    
    return cronograma, solucao.Value(makespan)
    

def plotaGrafico(cronograma, makespan):
    
    # Gerando gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    for i, cliente in enumerate(cronograma.keys()):
        for aparelho, inicio, fim in cronograma[cliente]:
            ax.barh(cliente, fim - inicio, left=inicio, color="#4169E1")

    ax.set_xlabel("Tempo (minutos)")
    ax.set_ylabel("Clientes")
    ax.set_title(f"Escalonamento de Treinos - Makespan: {makespan}")
    plt.show()
    
    return


if __name__ == "__main__":
    main()