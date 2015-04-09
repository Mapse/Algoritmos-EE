# coding=utf-8


# calculo de capacidade

def calcular_capacidade(alimentador):
	for trecho in alimentador.trechos.values():
		if int(trecho.fluxo.mod) > trecho.capacidade:
			print 'O trecho  %s está com sobrecorrente!' % trecho.nome

def atribuir_potencia(alimentador,a):
    for nos in alimentador.nos_de_carga.values():
        if isinstance(nos, a):
        	if nos.modelofluxo == 'PV':
				nos.potencia.real = (-1) * nos.potencia.real
				nos.potencia.imag = (-1) * nos.potencia.imag

def tensaogerador(alimentador):
	cont = 0
	diftensao = list()
	listanos = list()
	for nos in alimentador.nos_de_carga.values():
		if nos.tipo == 'PV':
			
			deltaV = float(nos.tensao.mod) - nos.tensaogerador
			diftensao.append(deltaV)
			listanos.append(nos)
			cont += 1
			print diftensao
	return listanos,#diftensao, cont

#sdef calculareatancia(alimentador):
	#nosdegeracao = tensaogerador(alimentador)
	#for nos in nosdegeracao:

    	#return nosdegeracao
