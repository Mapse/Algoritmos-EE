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


def tensaogerador(alimentador, gerador):  # Função que percorre o sistema e identifica quais geradores ficaram com tensao fora dos limites

    count = 1
    diftensao = list()
    listanos = list()
    for nos in alimentador.nos_de_carga.values():  #percorre nos do sistema
        if isinstance(nos, gerador):
            if nos.modelofluxo == 'PV':  # trata apenas geradores modelados como PV

                deltav = float(nos.tensao.mod) - nos.tensaogerador  #calcula a diferença entre a tensão calculada com o fluxo de carga e a tensao do gerador
                diftensao.append(deltav)   # guarda as diferenças de tensões dos geradores não convergidos na lista
                listanos.append(nos)  # guarda o objeto gerador
                count += 1  # incremento que define a quantidade geradores não convergidos
                print diftensao
    return listanos


def xii(alimentador, no_, nodecarga):
    trechos = alimentador.trechos.values()  # variável que guarda os techos do alimentador
    caminho = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_)[1]  # variável que guarda o caminho do nó até o nó raiz
    caminho = list(caminho)  # faz uma lista do array caminho
    caminho_2 = list(caminho)  # faz uma lista em outra variável auxiliar
    tr = []  # lista que servirá para guarda os trechos
    reat = 0

    for no in caminho:  # for que percorre o caminho
        for trecho in trechos:  # for que percorre os trechos

            if trecho.n1.nome == no:  # se o n1 do trecho for igual ao nó atual

                if type(trecho.n2) == nodecarga:  # se o tipo for gerador verifica se o n2 ta no caminho e se o n2 nao é o próprio nó
                    if trecho.n2.nome in caminho_2 and trecho.n2.nome != no:
                        reat += (trecho.comprimento * trecho.condutor.xp)
                        tr.append(trecho)
                else:
                    no_1 = alimentador.nos_de_carga[no]

                    try:
                        no_2 = alimentador.nos_de_carga[caminho_2[1]]
                    except IndexError:
                        continue

                    set_1 = set(no_1.chaves)
                    set_2 = set(no_2.chaves)

                    if set_1.intersection(set_2) != set():
                        chave = set_1.intersection(set_2).pop()
                    else:
                        continue

                    if chave != trecho.n2.nome:
                        continue

                    for trech in trechos:
                        if trech.n1.nome == chave:
                            tr.append(trech)
                            reat += (trech.comprimento * trech.condutor.xp)
                        elif trech.n2.nome == chave:
                            reat += (trech.comprimento * trech.condutor.xp)
                            tr.append(trech)

            elif trecho.n2.nome == no:
                if type(trecho.n1) == nodecarga:
                    if trecho.n1.nome in caminho and trecho.n1.nome != no:
                        tr.append(trecho)
                        reat += (trecho.comprimento * trecho.condutor.xp)
                else:
                    no_1 = alimentador.nos_de_carga[no]

                    try:
                        no_2 = alimentador.nos_de_carga[caminho_2[1]]
                    except IndexError:
                        continue

                    no_2 = alimentador.nos_de_carga[caminho_2[1]]
                    set_1 = set(no_1.chaves)
                    set_2 = set(no_2.chaves)

                    if set_1.intersection(set_2) != set():
                        chave = set_1.intersection(set_2).pop()
                    else:
                        continue

                    if chave != trecho.n1.nome:
                        continue

                    for trech in trechos:
                        if trech.n1.nome == chave:
                            tr.append(trech)
                            reat += (trech.comprimento * trech.condutor.xp)
                        elif trech.n2.nome == chave:
                            tr.append(trech)
                            reat += (trech.comprimento * trech.condutor.xp)
        caminho_2.remove(no)

    return tr, reat / 1e3
