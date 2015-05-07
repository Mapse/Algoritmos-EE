# coding=utf-8


# calculo de capacidade

def calcular_capacidade(alimentador):
    for trecho in alimentador.trechos.values():
        if int(trecho.fluxo.mod) > trecho.capacidade:
            print 'O trecho  %s está com sobrecorrente!' % trecho.nome

def atribuir_potencia(alimentador, gerador):
    """ Funcao que atribui potencia negativa em geradores para o calculo do fluxo de potencia  """
    for nos in alimentador.nos_de_carga.values():  # percorre os nos/geradores do sistema
        if isinstance(nos, gerador):  # se a classe gerador for instanciada, atribui-se a potência negativa ao nó da iteração.
            nos.potencia.real = (-1) * nos.potencia.real
            nos.potencia.imag = (-1) * nos.potencia.imag

def tensaogerador(alimentador,gerador): # Função que percorre o sistema e identifica quais geradores ficaram com tensao fora dos limites

    count = 1
    diftensao = list()
    listanos = list()
    for nos in alimentador.nos_de_carga.values(): #percorre nos do sistema
        if isinstance(nos, gerador):
            if nos.modelofluxo == 'PV': # trata apenas geradores modelados como PV

                deltaV = float(nos.tensao.mod) - nos.tensaogerador #calcula a diferença entre a tensão calculada com o fluxo de carga e a tensao do gerador
                diftensao.append(deltaV) # guarda as diferenças de tensões dos geradores não convergidos na lista
                listanos.append(nos) # guarda o objeto gerador
                count += 1 # incremento que define a quantidade geradores não convergidos
                print diftensao
    return listanos



#Cálculo da diagonal principal
# Farei uma função para o cálculo

reat = 0  # define a variavel como 0 para depois atribuir as reatancias de cada trecho
trechos = sub_1_al_1.trechos.values()  # armazena os trechos do sistema
caminho = sub_1_al_1.arvore_nos_de_carga.caminho_no_para_raiz('B1')[1]  # armazena o caminho nó para raiz (usando B1 como exemplo)
for no in caminho:
    for trecho in trechos:  # faz for nos trechos do alimentador.
        if str(no) == trecho.n1.nome:  # se o nó atual do caminho for igual ao n1 do trecho faz:

            if trecho.n1.nome not in caminho:  # se o nome do n1 do trecho não está no caminho
                if trecho.n2.nome in caminho:  # verifica se o n2 está e portanto soma a reatância
                    reat += trecho.comprimento * trecho.condutor.xp
                    print trecho  # dá o print do trecho para verificação
            elif trecho.n2.nome not in caminho:  # ou se o nome do n2 do trecho não está no caminho
                if trecho.n1.nome in caminho:  # verifica se o nome do n1 está no caminho
                    aux = 0  # variável auxiliar
                    if isinstance(trecho.n2, Chave):  # (PROBLEMA) se o n2 do trecho instancia a classe Chave
                        aux = trecho.n2  # a variável recebe o n2
                        if aux.vizinhojus not in caminho:  # se o vizinhojus não estiver no caminho
                            reat += 0  # não soma a reatância
                        else:  # se o vizinhomon estiver no caminho:
                                reat += trecho.comprimento * trecho.condutor.xp #soma a reatancia
                                print trecho
                    elif trecho.n2.nome not in caminho:  # por outro lado, se o n2 do trecho não está no caminho
                        reat += 0  # atribui zero para a reatância
                    else:  # pelo contrário, soma a reatancia
                        reat += trecho.comprimento * trecho.condutor.xp
                        print trecho
            else:  # se os dois nós considerados, n1 e n2 estiverem no caminho, soma a reatancia.
                reat += trecho.comprimento * trecho.condutor.xp
                print trecho
                trechos.remove(trecho)  # precisa-se remover o trecho, pois ao considerar o próximo nó da árvore
# o mesmo trecho será visitado e a reatância seria adicionada novamente.
        elif str(no) == trecho.n2.nome:  # ou se o nó atual do caminho é igual ao n2 do trecho e realiza
                                        # praticamente a mesma coisa de anteriormente
            if trecho.n1.nome not in caminho:
                if trecho.n2.nome in caminho:
                    reat += trecho.comprimento * trecho.condutor.xp
                    print trecho
            elif trecho.n2.nome not in caminho:
                if trecho.n1.nome in caminho:
                    if isinstance(trecho.n2, Chave):
                        reat += 0
                    elif trecho.n2.nome not in caminho:
                        reat += 0
                    else:
                        reat += trecho.comprimento * trecho.condutor.xp
                        print trecho
            else:
                reat += trecho.comprimento * trecho.condutor.xp
                print trecho
                trechos.remove(trecho)
print reat


    def xij(alimentador):

