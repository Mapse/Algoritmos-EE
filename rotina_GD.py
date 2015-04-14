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


 # calculo da reatancia x11,x22,x33 (listanos está na funcao tensaogerador), nao concluido
imp = 0
cont = 0
for ger in listanos:
    aux = ger.nome
    while cont<100:

        for trechos in sub_1_al_1.trechos.values():

            if trechos.n2.nome == aux:
                aux = trechos.n1.nome
                imp += trechos.comprimento * trechos.condutor.xp
                sub_1_al_1.trechos.values().remove(trechos)

            cont += 1
imp = imp/100