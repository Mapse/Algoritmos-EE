# coding=utf-8
from terminaltables import AsciiTable
import numpy as np
from scipy import linalg
from random import randint
from rnp import Arvore, Aresta
from util import Fasor, Base


class Setor(Arvore):
    Prioridade_Baixa, Prioridade_Media, Prioridade_Alta = range(3)

    def __init__(self, nome, vizinhos, nos_de_carga, prioridade=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe' \
                                      'Setor deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Setor deve ser do tipo list'
        assert isinstance(nos_de_carga, list), 'O parâmetro nos_de_carga da classe' \
                                               'Setor deve ser do tipo list'
        #assert isinstance(prioridade, int), 'O parâmetro Prioridade da classe' \
        #                                    'Setor deve ser do tipo int'
        self.nome = nome
        self.prioridade = prioridade
        self.vizinhos = vizinhos

        self.rnp_associadas = {i: None for i in self.vizinhos}

        self.nos_de_carga = dict()
        for no in nos_de_carga:
            no.setor = self.nome
            self.nos_de_carga[no.nome] = no

        self.no_de_ligacao = None

        arvore_de_setor = self._gera_arvore_do_setor()
        super(Setor, self).__init__(arvore_de_setor, str)

    def _gera_arvore_do_setor(self):
        arvore_do_setor = dict()
        # for percorre os nós de carga do setor
        for i, j in self.nos_de_carga.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            vizinhos = list()
            # for percorre os vizinhos do nó de carga
            for k in j.vizinhos:
                # condição só considera vizinho o nó de carga que está
                # no mesmo setor que o nó de carga analisado
                if k in self.nos_de_carga.keys():
                    vizinhos.append(k)
            arvore_do_setor[i] = vizinhos

        return arvore_do_setor

    def calcular_potencia(self):

        potencia_fase_a = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        potencia_fase_b = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        potencia_fase_c = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        for no in self.nos_de_carga.values():
            potencia_fase_a = potencia_fase_a + no.potencia_fase_a
            potencia_fase_b = potencia_fase_b + no.potencia_fase_b
            potencia_fase_c = potencia_fase_c + no.potencia_fase_c

        return potencia_fase_a, potencia_fase_b, potencia_fase_c

    def __str__(self):
        return 'Setor: ' + self.nome


class NoDeCarga(object):
    def __init__(self,
                 nome,
                 vizinhos,
                 potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 potencia_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 potencia_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 tensao_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tensao_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tensao_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 chaves=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe NoDeCarga' \
                                      ' deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Barra deve ser do tipo string'

        self.nome = nome
        self.vizinhos = vizinhos
        self.potencia_fase_a = potencia_fase_a
        self.potencia_fase_b = potencia_fase_b
        self.potencia_fase_c = potencia_fase_c
        self.potencia_eq_fase_a = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.potencia_eq_fase_b = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.potencia_eq_fase_c = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.tensao_fase_a = tensao_fase_a
        self.tensao_fase_b = tensao_fase_b
        self.tensao_fase_c = tensao_fase_c
        if chaves is not None:
            assert isinstance(chaves, list), 'O parâmetro chaves da classe NoDeCarga' \
                                             ' deve ser do tipo list'
            self.chaves = chaves
        else:
            self.chaves = list()

        self.setor = None

    def __str__(self):
        return 'No de Carga: ' + self.nome


class Gerador(object):
    def __init__(self,
                 nome,
                 vizinhos,
                 tipogerador,
                 maquina,
                 modelofluxo,
                 qmin,
                 qmax,
                 tensaogerador,
                 dvtol,
                 potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 potencia_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 potencia_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 tensao_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tensao_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tensao_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 chaves=None):

        self.nome = nome
        self.vizinhos = vizinhos
        self.potencia_fase_a = potencia_fase_a
        self.potencia_fase_b = potencia_fase_b
        self.potencia_fase_c = potencia_fase_c
        self.dvtol = dvtol
        self.potencia_eq_fase_a = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.potencia_eq_fase_b = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.potencia_eq_fase_c = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.tensao_fase_a = tensao_fase_a
        self.tensao_fase_b = tensao_fase_b
        self.tensao_fase_c = tensao_fase_c
        self.tipogerador = tipogerador
        self.maquina = maquina
        self.modelofluxo = modelofluxo
        self.qmin = qmin
        self.qmax = qmax
        self.tensaogerador = tensaogerador

        assert isinstance(tipogerador, str), 'O parâmetro tipogerador deve' \
                                             'ser do tipo str'
        assert isinstance(maquina, str), 'O parâmetro maquina deve' \
                                         'ser do tipo str'
        assert isinstance(modelofluxo, str), 'O parâmetro modelofluxo deve' \
                                             'ser do tipo str'
        if chaves is not None:
            assert isinstance(chaves, list), 'O parâmetro chaves da classe NoDeCarga' \
                                             ' deve ser do tipo list'
            self.chaves = chaves
        else:
            self.chaves = list()

        self.setor = None

    def __repr__(self):
        return 'Gerador: {nome}'.format(nome=self.nome)


class Subestacao(object):
    def __init__(self, nome, alimentadores, transformadores, impedancia_positiva=0, impedancia_zero=0):
        assert isinstance(nome, str), 'O parâmetro nome da classe Subestacao ' \
                                      'deve ser do tipo str'
        assert isinstance(alimentadores, list), 'O parâmetro alimentadores da classe ' \
                                                'deve ser do tipo list'

        assert isinstance(transformadores, list), 'O parâmetro alimentadores da classe ' \
                                                  'deve ser do tipo list'
        self.nome = nome

        self.alimentadores = dict()
        for alimentador in alimentadores:
            self.alimentadores[alimentador.nome] = alimentador

        self.transformadores = dict()
        for transformador in transformadores:
            self.transformadores[transformador.nome] = transformador

        for transformador in transformadores:
            self.base_sub = Base(transformador.tensao_secundario.mod, transformador.potencia.mod)
            break

        for alimentador in alimentadores:  # varre os alimentadores para criar as tensões de base e calcula as impedâncias equivalentes
            for trecho in alimentador.trechos.values():
                trecho.base = self.base_sub  # DÚVIDA AQUI
                trecho.impedancia_equivalente_positiva = trecho.impedancia_positiva/trecho.base.impedancia
                trecho.impedancia_equivalente_zero = trecho.impedancia_zero / trecho.base.impedancia

        self.impedancia_positiva = impedancia_positiva # precisa definir da subestação
        self.impedancia_zero = impedancia_zero
        self.impedancia_equivalente_positiva = impedancia_positiva
        self.impedancia_equivalente_zero = impedancia_zero

    ############################
    # CALCULOS DE CURTO-CIRCUITO
    ############################

    def calculacurto(self, tipo):
        """Função que calcula o valor da corrente de curto circuito"""

        #inicialmente calcula a impedancia equivalente para cada trecho
        self.calculaimpedanciaeq()

        if tipo == 'trifasico':
            self.curto_trifasico = [['Trecho 3fasico', 'Curto pu', 'Curto A']]

            # para cada trecho alimentado pela subestação calcula o curto
            for alimentador_atual, r in self.alimentadores.iteritems():
                for i in self.alimentadores[alimentador_atual].trechos.values():
                    curto = i.calcula_curto_trifasico()
                    self.curto_trifasico.append([i.nome, str(curto.pu), str(curto.mod)])
            table = AsciiTable(self.curto_trifasico)
            print table.table

        elif tipo == 'monofasico':
            self.curto_monofasico = [['Trecho 1fasico', 'Curto pu', 'Curto A']]

            # para cada trecho alimentado pela subestação calcula o curto
            for alimentador_atual, r in self.alimentadores.iteritems():
                for i in self.alimentadores[alimentador_atual].trechos.values():
                    curto = i.calcula_curto_monofasico()
                    self.curto_monofasico.append([i.nome, str(curto.pu), str(curto.mod)])
            table = AsciiTable(self.curto_monofasico)
            print table.table

        elif tipo == 'bifasico':
            self.curto_bifasico = [['Trecho 2fasico', 'Curto pu', 'Curto A']]

            # para cada trecho alimentado pela subestação calcula o curto
            for alimentador_atual, r in self.alimentadores.iteritems():
                for i in self.alimentadores[alimentador_atual].trechos.values():
                    curto = i.calcula_curto_bifasico()
                    self.curto_bifasico.append([i.nome, str(curto.pu), str(curto.mod)])
            table = AsciiTable(self.curto_bifasico)
            print table.table

        elif tipo == 'monofasico_minimo':
            self.curto_monofasico_minimo = [['Trecho 1fasico min', 'Curto pu', 'Curto A']]

            # para cada trecho alimentado pela subestação calcula o curto
            for alimentador_atual, r in self.alimentadores.iteritems():
                for i in self.alimentadores[alimentador_atual].trechos.values():
                    curto = i.calcula_curto_monofasico_minimo()
                    self.curto_monofasico_minimo.append([i.nome,str(curto.pu),str(curto.mod)])
            table = AsciiTable(self.curto_monofasico_minimo)
            print table.table

    def calculaimpedanciaeq(self):
        """Função que calcula a impedancia equivalente da subestação até o final do cada trecho"""

        # for coloca os valores de impedância em pu
        for alimentador in self.alimentadores.values():
            for trecho in alimentador.trechos.values():
                trecho.base = self.base_sub
                trecho.impedancia_equivalente_positiva = trecho.impedancia_positiva/ trecho.base.impedancia
                trecho.impedancia_equivalente_zero = trecho.impedancia_zero / trecho.base.impedancia

        # guarda os trechos em que já foram calculados a impedância equivalente
        trechosvisitados = []

        # procura o nó inicial(raiz) do alimentador
        for alimentador_atual, r in self.alimentadores.iteritems():
            for i in self.alimentadores[alimentador_atual].trechos.values(): # por que nao i in self.r.trechos.values():??
                for j in self.alimentadores[alimentador_atual].setores[r.arvore_nos_de_carga.raiz].nos_de_carga.keys(): #DUVIDA AQUI
                    # nó a partir do qual será procurado trechos conectados a ele
                    prox_no = self.alimentadores[alimentador_atual].setores[r.arvore_nos_de_carga.raiz].nos_de_carga[j]
                    # último trecho que foi calculado a impedância equivalente
                    trechoatual = self  # DÚVIDA AQUI
                    break
                break
            break
            # ALIMENTADOR ATUAL?
        self._calculaimpedanciaeq(trechoatual, prox_no, alimentador_atual, trechosvisitados)
#SE TRECHOS VISITADOS AINDA É VAZIO COMO FUNCIONARÁ O IF?

    def _calculaimpedanciaeq(self, trecho_anterior, no_atual, alimentador_atual, trechosvisitados):

        # procura trechos conectados ao no_atual (prox_no da execução anterior)
        for i in self.alimentadores[alimentador_atual].trechos.values():
            if (i not in trechosvisitados and i.n1 == no_atual) or (i not in trechosvisitados and i.n2  == no_atual):

                # verifica se a ligação é feita por meio de chave, verificando-se o estado da chave
                if type(no_atual) == Chave:
                    if no_atual.estado == 0:
                        continue
                    else:
                        pass
                else:
                    pass

                # calcula impedância equivalente do trecho
                i.impedancia_equivalente_positiva = i.impedancia_equivalente_positiva + trecho_anterior.impedancia_equivalente_positiva
                i.impedancia_equivalente_zero = i.impedancia_equivalente_zero + trecho_anterior.impedancia_equivalente_zero
                trechosvisitados.append(i)
                trecho_atual = i

                # procura o prox_no para calcular a sua impedancia equivalente
                if no_atual == i.n1:
                    prox_no = i.n2
                else:
                    prox_no = i.n1

                self._calculaimpedanciaeq(trecho_atual, prox_no, alimentador_atual,trechosvisitados)
            else:
                pass
        return

    def calculacurtogerador(self, alimentador, gerador, ponto_de_curto):
        """Função que calcula o valor do curto circuito com a contribuição de
        um gerador"""

        # for coloca os valores de impedância em pu
        for al in self.alimentadores.values():
            for trecho in al.trechos.values():
                trecho.base = self.base_sub
                trecho.base = self.base_sub
                trecho.impedancia_equivalente_positiva = trecho.impedancia_positiva/ trecho.base.impedancia
                trecho.impedancia_equivalente_zero = trecho.impedancia_zero / trecho.base.impedancia
        # guarda o caminho subestaçã-gerador e subestação-ponto_de_curto
        c1 = self.alimentadores[alimentador].arvore_nos_de_carga.caminho_no_para_no(self.alimentadores[alimentador].raiz,ponto_de_curto,0)
        c2 = self.alimentadores[alimentador].arvore_nos_de_carga.caminho_no_para_no(self.alimentadores[alimentador].raiz,gerador,0)

        # procura o nó de maior profundidade (ponto de encontro) que ainda é comum aos dois caminhos
        for i in range(len(c1[0])):
            for j in range(len(c2[0])):
                if c1[1][i] == c2[1][j]:
                    ponto_de_encontro = c1[1][i]
                    profundidadec1 = i
                    profundidadec2 = j
        print 'ponto de encontro', ponto_de_encontro

        impedanciasub_positiva = 0
        impedanciasub_zero = 0
        inicial = self.alimentadores[alimentador].raiz
        trechoscomuns = []

        # calcula a impedancia do caminho entre subestação e o ponto de encontro
        for i in range(profundidadec1):
            z1 = self._busca_trecho(self.alimentadores[alimentador], inicial, c1[1][i+1])
            if type(z1) == list:
                for j in z1:
                    trechoscomuns.append(j)
                    impedanciasub_positiva = impedanciasub_positiva + j.impedancia_equivalente_positiva
                    impedanciasub_zero = impedanciasub_zero + j.impedancia_equivalente_zero
            else:
                    trechoscomuns.append(z1)
                    impedanciasub_positiva = impedanciasub_positiva + z1.impedancia_equivalente_positiva
                    impedanciasub_zero = impedanciasub_zero + z1.impedancia_equivalente_zero

            inicial = c1[1][i + 1]
        '''print 'fim da impedancia sub-encontro'
        for k in trechoscomuns:
            print k.nome, '- zp', k.impedancia_equivalente_positiva
        print 'impedancia_positiva',impedanciasub_positiva
        for k in trechoscomuns:
            print k.nome, '- z0', k.impedancia_equivalente_zero
        print 'impedancia_zero',impedanciasub_zero
        print '\n \n' '''

        impedanciacomum_positiva = 0
        impedanciacomum_zero = 0
        inicial = c1[1][profundidadec1]
        trechoscurto = []

        # calcula a impedancia do caminho o ponto de encontro e o ponto de curto
        for i in range(profundidadec1 + 1, len(c1[0])):
            z2 = self._busca_trecho(self.alimentadores[alimentador], inicial, c1[1][i])
            if type(z2) == list:
                for j in z2:
                    trechoscurto.append(j)
                    impedanciacomum_positiva = impedanciacomum_positiva + j.impedancia_equivalente_positiva
                    impedanciacomum_zero = impedanciacomum_zero + j.impedancia_equivalente_zero
            else:
                trechoscurto.append(z2)
                impedanciacomum_positiva = impedanciacomum_positiva + z2.impedancia_equivalente_positiva
                impedanciacomum_zero = impedanciacomum_zero + z2.impedancia_equivalente_zero

            inicial = c1[1][i]
        '''print 'fim da impedancia encontro-curto'
        for k in trechoscurto:
            print k.nome, '- zp', k.impedancia_equivalente_positiva
        print 'impedancia_positiva',impedanciacomum_positiva
        for k in trechoscurto:
            print k.nome, '- z0', k.impedancia_equivalente_zero
        print 'impedancia_zero',impedanciacomum_zero
        print '\n \n' '''

        impedanciagerador_positiva = 0
        impedanciagerador_zero = 0
        inicial = c2[1][profundidadec1]
        trechosgerador = []

        # calcula a impedancia do caminho o ponto de encontro e o gerador
        for i in range(profundidadec1 + 1, len(c2[0])):
            z3 = self._busca_trecho(self.alimentadores[alimentador], inicial, c2[1][i])
            if type(z3) == list:
                for j in z3:
                    trechosgerador.append(j)
                    impedanciagerador_positiva = impedanciagerador_positiva + j.impedancia_equivalente_positiva
                    impedanciagerador_zero = impedanciagerador_zero + j.impedancia_equivalente_zero
            else:
                trechosgerador.append(z3)
                impedanciagerador_positiva = impedanciagerador_positiva + z3.impedancia_equivalente_positiva
                impedanciagerador_zero = impedanciagerador_zero + z3.impedancia_equivalente_zero

            inicial = c2[1][i]
        '''print 'fim da impedancia gerador-encontro'
        for k in trechosgerador:
            print k.nome, '- zp', k.impedancia_equivalente_positiva
        print 'impedancia_positiva',impedanciagerador_positiva
        for k in trechosgerador:
            print k.nome, '- z0', k.impedancia_equivalente_zero
        print 'impedancia_zero',impedanciagerador_zero'''

        # calcula a impedância da associação serie ou paralelo
        if (impedanciagerador_positiva or impedanciagerador_zero) != 0 and (impedanciasub_positiva or impedanciasub_zero) != 0:
            zparalelo_positiva = impedanciasub_positiva * impedanciagerador_positiva/(impedanciagerador_positiva+impedanciasub_positiva)
            zparalelo_zero = impedanciasub_zero * impedanciagerador_zero / (impedanciasub_zero+impedanciagerador_zero)

        elif (impedanciagerador_positiva and impedanciagerador_zero) == 0 and (impedanciasub_positiva or impedanciasub_zero) != 0:
            zparalelo_positiva = impedanciasub_positiva
            zparalelo_zero = impedanciasub_zero

        elif (impedanciagerador_positiva or impedanciagerador_zero) != 0 and (impedanciasub_positiva and impedanciasub_zero) == 0:
            zparalelo_positiva = impedanciagerador_positiva
            zparalelo_zero = impedanciagerador_zero
        else:
            zparalelo_positiva = 0
            zparalelo_zero = 0

        ztotal_positiva = zparalelo_positiva + impedanciacomum_positiva
        ztotal_zero = zparalelo_zero + impedanciacomum_zero

        # calcula o valor da corrente de curto no caminho ponto_de_encontro-curto
        curto1 = (3.0) * self.base_sub.corrente / (2 * ztotal_positiva + ztotal_zero)
        correntecc1 = Fasor(real=curto1.real, imag=curto1.imag, tipo=Fasor.Corrente)
        correntecc1.base = self.base_sub
        print 'curto monofasico em ponto comum-ponto de curto - ', correntecc1.mod
        curto1g = np.abs(impedanciasub_positiva / (impedanciagerador_positiva + impedanciasub_positiva)) * 2 * correntecc1.mod/3+\
        np.abs(impedanciasub_zero / (impedanciagerador_zero + impedanciasub_zero)) * correntecc1.mod/3
        print 'curto monofasico em gerador-ponto comum - ', curto1g
        curto1s = np.abs(impedanciagerador_positiva / (impedanciagerador_positiva + impedanciasub_positiva)) * 2 * correntecc1.mod/3+\
        np.abs(impedanciagerador_zero / (impedanciagerador_zero + impedanciasub_zero))*correntecc1.mod/3
        print 'curto monofasico em subestação-ponto comum - ', curto1s

        curto2 = (3 ** 0.5) * self.base_sub.corrente / (2 * ztotal_positiva)
        correntecc2 = Fasor(real=curto2.real, imag=curto2.imag, tipo=Fasor.Corrente)
        correntecc2.base = self.base_sub
        print 'curto bifasico em ponto comum-ponto de curto - ', correntecc2.mod

        curto3 = 1.0 * self.base_sub.corrente / (ztotal_positiva)
        correntecc3 = Fasor(real=curto3.real, imag=curto3.imag, tipo=Fasor.Corrente)
        correntecc3.base = self.base_sub
        print 'curto trifasico em ponto comum-ponto de curto - ', correntecc3.mod
        curto3g = curto3 * impedanciasub_zero / (impedanciasub_zero + impedanciagerador_zero)
        correntecc3g = Fasor(real=curto3g.real, imag=curto3g.imag, tipo=Fasor.Corrente)
        correntecc3g.base = self.base_sub
        print 'curto trifasico em gerador-ponto comum - ', correntecc3g.mod
        curto3s = curto3 * impedanciagerador_zero / (impedanciasub_zero + impedanciagerador_zero)
        correntecc3s = Fasor(real=curto3s.real, imag=curto3s.imag, tipo=Fasor.Corrente)
        correntecc3s.base = self.base_sub
        print 'curto trifasico em subestação-ponto comum - ', correntecc3s.mod

    ###########################
    # CALCULO DE FLUXO DE CARGA
    ###########################

    def _busca_trecho(self, alimentador, n1, n2):
        """Função que busca trechos em um alimendador entre os nós/chaves
          n1 e n2"""
        # for pecorre os nos de carga do alimentador
        for no in alimentador.nos_de_carga.keys():

            # cria conjuntos das chaves ligadas ao no
            chaves_n1 = set(alimentador.nos_de_carga[n1].chaves)
            chaves_n2 = set(alimentador.nos_de_carga[n2].chaves)

            # verifica se existem chaves comuns aos nos
            chaves_intersec = chaves_n1.intersection(chaves_n2)

            if chaves_intersec != set():
                # verifica quais trechos estão ligados a chave
                # comum as nós.
                chave = chaves_intersec.pop()
                trechos_ch = []
                # identificação dos trechos requeridos
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == chave:
                        if trecho.n2.nome == n1 or trecho.n2.nome == n2:
                            trechos_ch.append(trecho)
                    elif trecho.n2.nome == chave:
                        if trecho.n1.nome == n1 or trecho.n1.nome == n2:
                            trechos_ch.append(trecho)
                # caso o comprimento da lista seja dois, ou seja, há chave
                # entre dois ós de carga, a função retorna os trechos.
                if len(trechos_ch) == 2:
                    return trechos_ch
            else:
                # se não existirem chaves comuns, verifica qual trecho
                # tem os nos n1 e n2 como extremidade
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == n1:
                        if trecho.n2.nome == n2:
                            return trecho
                    elif trecho.n1.nome == n2:
                        if trecho.n2.nome == n1:
                            return trecho

    def _atribuir_tensao_a_subestacao(self, tensao):
        """ Função que atribui tensão à subestação
         e a define para todos os nós de carga"""
        self.tensao = tensao
        for alimentador in self.alimentadores.values():
            for no in alimentador.nos_de_carga.values():
                no.tensao_fase_a = Fasor(real=tensao.real,
                                         imag=tensao.imag,
                                         tipo=Fasor.Tensao)
                no.tensao_fase_b = Fasor(real=tensao.real,
                                         imag=tensao.imag,
                                         tipo=Fasor.Tensao)
                no.tensao_fase_c = Fasor(real=tensao.real,
                                         imag=tensao.imag,
                                         tipo=Fasor.Tensao)

    def _varrer_alimentador(self, alimentador):
        """ Função que varre os alimentadores pelo
        método varredura direta/inversa"""

        # guarda os nós de carga na variável nos_alimentador
        nos_alimentador = alimentador.nos_de_carga.values()

        # guarda a rnp dos nós de carga na variável rnp_alimentador
        rnp_alimentador = alimentador.arvore_nos_de_carga.rnp

        # guarda a árvore de cada nós de carga
        arvore_nos_de_carga = alimentador.arvore_nos_de_carga.arvore

        # variáveis para o auxílio na determinação do nó mais profundo
        prof_max = 0

        # for percorre a rnp dos nós de carga tomando valores
        # em pares (profundidade, nó).
        for no_prof in rnp_alimentador.transpose():
            # pega os nomes dos nós de carga.
            nos_alimentador_nomes = [no.nome for no in nos_alimentador]

            # verifica se a profundidade do nó é maior do que a
            # profundidade máxima e se ele está na lista de nós do alimentador.
            if (int(no_prof[0]) > prof_max) \
               and (no_prof[1] in nos_alimentador_nomes):
                prof_max = int(no_prof[0])

        # prof recebe a profundidae máxima determinada
        prof = prof_max

        # seção do cálculo das potências partindo dos
        # nós com maiores profundidades até o nó raíz
        while prof >= 0:
            # guarda os nós com maiores profundidades.
            nos = [alimentador.nos_de_carga[no_prof[1]]
                   for no_prof in rnp_alimentador.transpose() if
                   int(no_prof[0]) == prof]

            # decrementodo da profundidade.
            prof -= 1

            # for que percorre os nós com a profundidade
            # armazenada na variável prof
            for no in nos:
                # zera as potências para que na próxima
                # iteração não ocorra acúmulo.
                no.potencia_eq_fase_a.real = 0.0
                no.potencia_eq_fase_b.real = 0.0
                no.potencia_eq_fase_c.real = 0.0

                no.potencia_eq_fase_a.imag = 0.0
                no.potencia_eq_fase_b.imag = 0.0
                no.potencia_eq_fase_c.imag = 0.0

                # armazena a árvore do nó de carga
                # armazenado na variável nó
                vizinhos = arvore_nos_de_carga[no.nome]

                # guarda os pares (profundidade, nó)
                no_prof = [no_prof for no_prof in rnp_alimentador.transpose()
                           if no_prof[1] == no.nome]
                vizinhos_jusante = list()

                # for que percorre a árvore de cada nó de carga
                for vizinho in vizinhos:
                    # verifica quem é vizinho do nó desejado.
                    vizinho_prof = [viz_prof for viz_prof in
                                    rnp_alimentador.transpose()
                                    if viz_prof[1] == vizinho]

                    # verifica se a profundidade do vizinho é maior
                    if int(vizinho_prof[0][0]) > int(no_prof[0][0]):
                        # armazena os vizinhos a jusante.
                        vizinhos_jusante.append(
                            alimentador.nos_de_carga[vizinho_prof[0][1]])

                # verifica se não há vizinho a jusante,
                # se não houverem o nó de carga analisado
                # é o último do ramo.
                if vizinhos_jusante == []:
                    no.potencia_eq_fase_a.real += no.potencia_fase_a.real
                    no.potencia_eq_fase_b.real += no.potencia_fase_b.real
                    no.potencia_eq_fase_c.real += no.potencia_fase_c.real

                    no.potencia_eq_fase_a.imag += no.potencia_fase_a.imag
                    no.potencia_eq_fase_b.imag += no.potencia_fase_b.imag
                    no.potencia_eq_fase_c.imag += no.potencia_fase_c.imag
                else:
                    # soma a potencia da carga associada ao nó atual
                    no.potencia_eq_fase_a.real += no.potencia_fase_a.real
                    no.potencia_eq_fase_b.real += no.potencia_fase_b.real
                    no.potencia_eq_fase_c.real += no.potencia_fase_c.real

                    no.potencia_eq_fase_a.imag += no.potencia_fase_a.imag
                    no.potencia_eq_fase_b.imag += no.potencia_fase_b.imag
                    no.potencia_eq_fase_c.imag += no.potencia_fase_c.imag

                    # acrescenta à potência do nó atual
                    # as potências dos nós a jusante
                    for no_jus in vizinhos_jusante:
                        no.potencia_eq_fase_a.real += no_jus.potencia_eq_fase_a.real
                        no.potencia_eq_fase_b.real += no_jus.potencia_eq_fase_b.real
                        no.potencia_eq_fase_c.real += no_jus.potencia_eq_fase_c.real

                        no.potencia_eq_fase_a.imag += no_jus.potencia_eq_fase_a.imag
                        no.potencia_eq_fase_b.imag += no_jus.potencia_eq_fase_b.imag
                        no.potencia_eq_fase_c.imag += no_jus.potencia_eq_fase_c.imag

                        # chama a função busca_trecho para definir
                        # quais trechos estão entre o nó atual e o nó a jusante
                        trecho = self._busca_trecho(alimentador,
                                                    no.nome,
                                                    no_jus.nome)
                        # se o trecho não for uma instancia da classe
                        # Trecho(quando há chave entre nós de cargas)
                        # a impedância é calculada
                        if not isinstance(trecho, Trecho):

                            r1, x1 = trecho[0].calcula_impedancia()
                            r2, x2 = trecho[1].calcula_impedancia()
                            r, x = r1 + r2, x1 + x2
                        # se o trecho atual for uma instancia da classe trecho
                        else:
                            r, x = trecho.calcula_impedancia()
                            # calculo das potências dos nós de carga a jusante.
                        no.potencia_eq_fase_a.real += r * (no_jus.potencia_eq_fase_a.mod ** 2) / \
                            no_jus.tensao_fase_a.mod ** 2
                        no.potencia_eq_fase_b.real += r * (no_jus.potencia_eq_fase_b.mod ** 2) / \
                            no_jus.tensao_fase_b.mod ** 2
                        no.potencia_eq_fase_c.real += r * (no_jus.potencia_eq_fase_c.mod ** 2) / \
                            no_jus.tensao_fase_c.mod ** 2

                        no.potencia_eq_fase_a.imag += x * (no_jus.potencia_eq_fase_a.mod ** 2) / \
                            no_jus.tensao_fase_a.mod ** 2
                        no.potencia_eq_fase_b.imag += x * (no_jus.potencia_eq_fase_b.mod ** 2) / \
                            no_jus.tensao_fase_b.mod ** 2
                        no.potencia_eq_fase_c.imag += x * (no_jus.potencia_eq_fase_c.mod ** 2) / \
                            no_jus.tensao_fase_c.mod ** 2

        prof = 0
        # seção do cálculo de atualização das tensões
        while prof <= prof_max:
            # salva os nós de carga a montante
            nos = [alimentador.nos_de_carga[col_no_prof[1]]
                   for col_no_prof in rnp_alimentador.transpose()
                   if int(col_no_prof[0]) == prof + 1]
            # percorre os nós para guardar a árvore do nó requerido
            for no in nos:
                vizinhos = arvore_nos_de_carga[no.nome]
                # guarda os pares (profundidade,nó)
                no_prof = [col_no_prof
                           for col_no_prof in rnp_alimentador.transpose()
                           if col_no_prof[1] == no.nome]
                vizinhos_montante = list()
                # verifica quem é vizinho do nó desejado.
                for vizinho in vizinhos:
                    vizinho_prof = [viz_prof
                                    for viz_prof in rnp_alimentador.transpose()
                                    if viz_prof[1] == vizinho]
                    if int(vizinho_prof[0][0]) < int(no_prof[0][0]):
                        # armazena os vizinhos a montante.
                        vizinhos_montante.append(
                            alimentador.nos_de_carga[vizinho_prof[0][1]])
                # armazena o primeiro vizinho a montante
                no_mon = vizinhos_montante[0]
                trecho = self._busca_trecho(alimentador, no.nome, no_mon.nome)
                # se existir chave, soma a resistência dos dois trechos
                if not isinstance(trecho, Trecho):

                    r1, x1 = trecho[0].calcula_impedancia()
                    r2, x2 = trecho[1].calcula_impedancia()
                    r, x = r1 + r2, x1 + x2
                # caso não exista, a resistência é a do próprio trecho
                else:
                    r, x = trecho.calcula_impedancia()

                v_mon_fase_a = no_mon.tensao_fase_a.mod
                v_mon_fase_b = no_mon.tensao_fase_b.mod
                v_mon_fase_c = no_mon.tensao_fase_c.mod

                pa = no.potencia_eq_fase_a.real
                pb = no.potencia_eq_fase_b.real
                pc = no.potencia_eq_fase_c.real

                qa = no.potencia_eq_fase_a.imag
                qb = no.potencia_eq_fase_b.imag
                qc = no.potencia_eq_fase_c.imag

                # parcela de perdas
                pa += r * (no.potencia_eq_fase_a.mod ** 2) / no.tensao_fase_a.mod ** 2
                pb += r * (no.potencia_eq_fase_b.mod ** 2) / no.tensao_fase_b.mod ** 2
                pc += r * (no.potencia_eq_fase_c.mod ** 2) / no.tensao_fase_c.mod ** 2

                qa += x * (no.potencia_eq_fase_a.mod ** 2) / no.tensao_fase_a.mod ** 2
                qb += x * (no.potencia_eq_fase_b.mod ** 2) / no.tensao_fase_b.mod ** 2
                qc += x * (no.potencia_eq_fase_c.mod ** 2) / no.tensao_fase_c.mod ** 2

                v_jus_fase_a = v_mon_fase_a ** 2 - 2 * (r * pa + x * qa) + \
                    (r ** 2 + x ** 2) * (pa ** 2 + qa ** 2) / v_mon_fase_a ** 2
                v_jus_fase_b = v_mon_fase_b ** 2 - 2 * (r * pb + x * qb) + \
                    (r ** 2 + x ** 2) * (pb ** 2 + qb ** 2) / v_mon_fase_b ** 2
                v_jus_fase_c = v_mon_fase_c ** 2 - 2 * (r * pc + x * qc) + \
                    (r ** 2 + x ** 2) * (pc ** 2 + qc ** 2) / v_mon_fase_c ** 2

                v_jus_fase_a = np.sqrt(v_jus_fase_a)
                v_jus_fase_b = np.sqrt(v_jus_fase_b)
                v_jus_fase_c = np.sqrt(v_jus_fase_c)

                k1a = (pa * x - qa * r) / v_mon_fase_a
                k1b = (pb * x - qb * r) / v_mon_fase_b
                k1c = (pc * x - qc * r) / v_mon_fase_c

                k2a = v_mon_fase_a - (pa * r - qa * x) / v_mon_fase_a
                k2b = v_mon_fase_b - (pb * r - qb * x) / v_mon_fase_b
                k2c = v_mon_fase_c - (pc * r - qc * x) / v_mon_fase_c

                ang_a = no_mon.tensao_fase_a.ang * np.pi / 180.0 - np.arctan(k1a / k2a)
                ang_b = no_mon.tensao_fase_b.ang * np.pi / 180.0 - np.arctan(k1b / k2b)
                ang_c = no_mon.tensao_fase_c.ang * np.pi / 180.0 - np.arctan(k1c / k2c)

                no.tensao_fase_a.mod = v_jus_fase_a
                no.tensao_fase_b.mod = v_jus_fase_b
                no.tensao_fase_c.mod = v_jus_fase_c

                no.tensao_fase_a.ang = ang_a * 180.0 / np.pi
                no.tensao_fase_b.ang = ang_b * 180.0 / np.pi
                no.tensao_fase_c.ang = ang_c * 180.0 / np.pi

                # print 'Tensao do no {nome}: {tens}'.format(nome=no.nome, tens=no.tensao.mod/1e3)

                # calcula o fluxo de corrente passante no trecho
                corrente_fase_a = no.tensao_fase_a.real - no_mon.tensao_fase_a.real
                corrente_fase_b = no.tensao_fase_b.real - no_mon.tensao_fase_b.real
                corrente_fase_c = no.tensao_fase_c.real - no_mon.tensao_fase_c.real

                corrente_fase_a += (no.tensao_fase_a.imag - no_mon.tensao_fase_a.imag) * 1.0j
                corrente_fase_b += (no.tensao_fase_b.imag - no_mon.tensao_fase_b.imag) * 1.0j
                corrente_fase_c += (no.tensao_fase_c.imag - no_mon.tensao_fase_c.imag) * 1.0j

                corrente_fase_a /= (r + x * 1.0j)
                corrente_fase_b /= (r + x * 1.0j)
                corrente_fase_c /= (r + x * 1.0j)
                # se houver chaves, ou seja, há dois trechos a mesma corrente
                # é atribuida
                if not isinstance(trecho, Trecho):
                    trecho[0].fluxo_fase_a = Fasor(real=corrente_fase_a.real,
                                                   imag=corrente_fase_a.imag,
                                                   tipo=Fasor.Corrente)
                    trecho[0].fluxo_fase_b = Fasor(real=corrente_fase_b.real,
                                                   imag=corrente_fase_b.imag,
                                                   tipo=Fasor.Corrente)
                    trecho[0].fluxo_fase_c = Fasor(real=corrente_fase_c.real,
                                                   imag=corrente_fase_c.imag,
                                                   tipo=Fasor.Corrente)

                    trecho[1].fluxo_fase_a = Fasor(real=corrente_fase_a.real,
                                                   imag=corrente_fase_a.imag,
                                                   tipo=Fasor.Corrente)
                    trecho[1].fluxo_fase_b = Fasor(real=corrente_fase_b.real,
                                                   imag=corrente_fase_b.imag,
                                                   tipo=Fasor.Corrente)
                    trecho[1].fluxo_fase_c = Fasor(real=corrente_fase_c.real,
                                                   imag=corrente_fase_c.imag,
                                                   tipo=Fasor.Corrente)

                else:
                    trecho.fluxo_fase_a = Fasor(real=corrente_fase_a.real,
                                                imag=corrente_fase_a.imag,
                                                tipo=Fasor.Corrente)
                    trecho.fluxo_fase_b = Fasor(real=corrente_fase_b.real,
                                                imag=corrente_fase_b.imag,
                                                tipo=Fasor.Corrente)
                    trecho.fluxo_fase_c = Fasor(real=corrente_fase_c.real,
                                                imag=corrente_fase_c.imag,
                                                tipo=Fasor.Corrente)
            prof += 1

    def atribuir_potencia(self, alimentador):
        """ Funcao que atribui potencia negativa em geradores para o calculo do
        fluxo de potencia  """
        # percorre os nos/geradores do sistema
        for nos in alimentador.nos_de_carga.values():
            # se a classe gerador for instanciada, atribui-se a potência
            # negativa ao nó da iteração.
            if isinstance(nos, Gerador):
                nos.potencia_fase_a.real = (-1) * nos.potencia_fase_a.real
                nos.potencia_fase_b.real = (-1) * nos.potencia_fase_b.real
                nos.potencia_fase_c.real = (-1) * nos.potencia_fase_c.real

                nos.potencia_fase_a.imag = (-1) * nos.potencia_fase_a.imag
                nos.potencia_fase_b.imag = (-1) * nos.potencia_fase_b.imag
                nos.potencia_fase_c.imag = (-1) * nos.potencia_fase_c.imag

    def tensaogerador(self, alimentador):
        """ Funcao que retorna uma lista com os geradores que nao convergiram,
        a quantidade de geradores e a matriz
            com as diferenças de tennsoes de cada gerador """

        count_fase_a = 0
        count_fase_b = 0
        count_fase_c = 0

        diftensao_fase_a = list()
        diftensao_fase_b = list()
        diftensao_fase_c = list()

        listager_fase_a = list()
        listager_fase_b = list()
        listager_fase_c = list()
        # percorre nos do sistema
        for nos in alimentador.nos_de_carga.values():
            # identifica os geradores do sistema
            if isinstance(nos, Gerador):
                # trata apenas geradores modelados como PV
                if nos.modelofluxo == 'PV':
                    # calcula a diferença entre a tensão calculada com o fluxo
                    # de carga e a tensao do gerador
                    deltav_fase_a = np.array([[nos.tensaogerador - float(nos.tensao_fase_a.mod)]])
                    deltav_fase_b = np.array([[nos.tensaogerador - float(nos.tensao_fase_b.mod)]])
                    deltav_fase_c = np.array([[nos.tensaogerador - float(nos.tensao_fase_c.mod)]])
                    # se a diferença de tensao for maior do que a tolerancia o
                    # gerador será guardado
                    if abs(deltav_fase_a) > nos.dvtol:
                        # guarda as diferenças de tensões dos geradores não
                        # convergidos na lista
                        diftensao_fase_a.append(deltav_fase_a)
                        # guarda o objeto gerador
                        listager_fase_a.append(nos)
                        # incremento que define a quantidade geradores não
                        # convergidos
                        count_fase_a += 1

                    if abs(deltav_fase_b) > nos.dvtol:
                        # guarda as diferenças de tensões dos geradores não
                        # convergidos na lista
                        diftensao_fase_b.append(deltav_fase_b)
                        # guarda o objeto gerador
                        listager_fase_b.append(nos)
                        # incremento que define a quantidade geradores não
                        # convergidos
                        count_fase_b += 1

                    if abs(deltav_fase_c) > nos.dvtol:
                        # guarda as diferenças de tensões dos geradores não
                        # convergidos na lista
                        diftensao_fase_c.append(deltav_fase_c)
                        # guarda o objeto gerador
                        listager_fase_c.append(nos)
                        # incremento que define a quantidade geradores não
                        # convergidos
                        count_fase_c += 1
        # cria um array para auxiliar na formação da matriz
        # das diferenças de tensões
        aux_fase_a = np.array([[]])
        aux_fase_b = np.array([[]])
        aux_fase_c = np.array([[]])
        # caso diftensao seja diferente de vazio, ou seja, existe gerador que não convergiu
        # forma-se a matriz das diferenças de tensões
        if diftensao_fase_a != []:
            # concatena a primeira diferença de tensão com o array auxiliar
            dif_fase_a = np.concatenate((diftensao_fase_a[0], aux_fase_a), axis=1)
            # remove o primeiro elemento deixando apenas o array vazio
            diftensao_fase_a.pop(0)
            # adiciona todos os elementos à matriz de diferença de tensões, incluindo o elemento removido
            for i in diftensao_fase_a:  # for que percorre a lista de array para realizar o restante da concatenação
                dif_fase_a = np.concatenate((dif_fase_a, i))
            diftensao_fase_a = dif_fase_a

        if diftensao_fase_b != []:
            # concatena a primeira diferença de tensão com o array auxiliar
            dif_fase_b = np.concatenate((diftensao_fase_b[0], aux_fase_b), axis=1)
            # remove o primeiro elemento deixando apenas o array vazio
            diftensao_fase_b.pop(0)
            # adiciona todos os elementos à matriz de diferença de tensões, incluindo o elemento removido
            for i in diftensao_fase_b:  # for que percorre a lista de array para realizar o restante da concatenação
                dif_fase_b = np.concatenate((dif_fase_b, i))
            diftensao_fase_b = dif_fase_b

        if diftensao_fase_c != []:
            # concatena a primeira diferença de tensão com o array auxiliar
            dif_fase_c = np.concatenate((diftensao_fase_c[0], aux_fase_c), axis=1)
            # remove o primeiro elemento deixando apenas o array vazio
            diftensao_fase_c.pop(0)
            # adiciona todos os elementos à matriz de diferença de tensões, incluindo o elemento removido
            for i in diftensao_fase_c:  # for que percorre a lista de array para realizar o restante da concatenação
                dif_fase_c = np.concatenate((dif_fase_c, i))
            diftensao_fase_c = dif_fase_c
        # retorna a lista com os geradores a quantidade de geradores e a matriz coluna da diferença de tensões
        return listager_fase_a, count_fase_a, diftensao_fase_a, listager_fase_b, count_fase_b, diftensao_fase_b, listager_fase_c, count_fase_c, diftensao_fase_c

    def matrix_reatancia(self, alimentador):
        """funcao que retorna a matriz X para o calculo da matriz de diferença
        de potência reativa """
        # chama a função tensaogerador retornando os geradores não convergidos,
        # bem como o número de geradores
        listageradores_fase_a, numgeradores_fase_a, dVgeradores_fase_a = self.tensaogerador(alimentador)[0], self.tensaogerador(alimentador)[1], self.tensaogerador(alimentador)[2]
        listageradores2_fase_a = self.tensaogerador(alimentador)[0]
        listageradores3_fase_a = self.tensaogerador(alimentador)[0]

        listageradores_fase_b, numgeradores_fase_b, dVgeradores_fase_b = self.tensaogerador(alimentador)[3], self.tensaogerador(alimentador)[4], self.tensaogerador(alimentador)[5]
        listageradores2_fase_b = self.tensaogerador(alimentador)[3]
        listageradores3_fase_b = self.tensaogerador(alimentador)[3]

        listageradores_fase_c, numgeradores_fase_c, dVgeradores_fase_c = self.tensaogerador(alimentador)[6], self.tensaogerador(alimentador)[7], self.tensaogerador(alimentador)[8]
        listageradores2_fase_c = self.tensaogerador(alimentador)[6]
        listageradores3_fase_c = self.tensaogerador(alimentador)[6]
        # declara uma matriz de zero com a dimensão (n x n), onde n é a
        # quantidade de geradores
        xa = np.zeros((numgeradores_fase_a, numgeradores_fase_a))
        xb = np.zeros((numgeradores_fase_b, numgeradores_fase_b))
        xc = np.zeros((numgeradores_fase_c, numgeradores_fase_c))

        aux_fase_a = []
        rem_fase_a = []
        # for para calcular os elementos xij/xji em ordem
        for i in listageradores2_fase_a:
            for j in listageradores3_fase_a:
                # caso i seja igual a j não faz nada, pois são elementos
                # da diagonal principal
                if i.nome == j.nome:
                    pass
                else:
                    # se o elemento já estiver computado não faz nada
                    if j.nome in rem_fase_a:
                        pass
                    else:
                        # guarda em aux o reatancia xij
                        aux_fase_a.append(self.xij(alimentador, i.nome, j.nome))
                        # guarda o nome do elemento visitado para não
                        # utilizá-lo na próxima iteração
                        rem_fase_a.append(i.nome)
        aux_fase_b = []
        rem_fase_b = []
        # for para calcular os elementos xij/xji em ordem
        for i in listageradores2_fase_b:
            for j in listageradores3_fase_b:
                # caso i seja igual a j não faz nada, pois são elementos
                # da diagonal principal
                if i.nome == j.nome:
                    pass
                else:
                    # se o elemento já estiver computado não faz nada
                    if j.nome in rem_fase_b:
                        pass
                    else:
                        # guarda em aux o reatancia xij
                        aux_fase_b.append(self.xij(alimentador, i.nome, j.nome))
                        # guarda o nome do elemento visitado para não
                        # utilizá-lo na próxima iteração
                        rem_fase_b.append(i.nome)
        aux_fase_c = []
        rem_fase_c = []
        # for para calcular os elementos xij/xji em ordem
        for i in listageradores2_fase_c:
            for j in listageradores3_fase_c:
                # caso i seja igual a j não faz nada, pois são elementos
                # da diagonal principal
                if i.nome == j.nome:
                    pass
                else:
                    # se o elemento já estiver computado não faz nada
                    if j.nome in rem_fase_c:
                        pass
                    else:
                        # guarda em aux o reatancia xij
                        aux_fase_c.append(self.xij(alimentador, i.nome, j.nome))
                        # guarda o nome do elemento visitado para não
                        # utilizá-lo na próxima iteração
                        rem_fase_c.append(i.nome)

        # for onde a matriz xa será preenchida
        for i in range(np.shape(xa)[0]):
            for j in range(np.shape(xa)[1]):
                # se é um elemento da diagonal principal
                if i == j:
                    # percorre a primeira lista auxiliar
                    for no in listageradores_fase_a:
                        # atribui a xii atual a reatância
                        xa[i, j] = self.xii(alimentador, no.nome)
                        # remove o nó atual para não utilizado
                        # novamente
                        listageradores_fase_a.remove(no)
                        # quebra o for para não calcular x22, x33..
                        # e substituir no lugar de x11
                        break
                # se é um elemento em que o número da coluna é maior
                # do que a linha
                elif j > i:
                    # faz for na lista com as reatâncias xij obtidas
                    # em ordem
                    for reat in aux_fase_a:
                        # se xij for 0, ou seja, não foi calulado
                        if xa[i, j] == 0:
                            # atribiu-se o valor de reat a xij e xji
                            xa[i, j] = reat
                            xa[j, i] = reat
                            # remove o elemento para não utilizar
                            # novamente
                            aux_fase_a.remove(reat)
                            # quebra o for para não substituir
                            # os valores de outros xij
                            break
                        # se xij for diferente de zero não faz nada
                        else:
                            pass
        # for onde a matriz xb será preenchida
        for i in range(np.shape(xb)[0]):
            for j in range(np.shape(xb)[1]):
                # se é um elemento da diagonal principal
                if i == j:
                    # percorre a primeira lista auxiliar
                    for no in listageradores_fase_b:
                        # atribui a xii atual a reatância
                        xb[i, j] = self.xii(alimentador, no.nome)
                        # remove o nó atual para não utilizado
                        # novamente
                        listageradores_fase_b.remove(no)
                        # quebra o for para não calcular x22, x33..
                        # e substituir no lugar de x11
                        break
                # se é um elemento em que o número da coluna é maior
                # do que a linha
                elif j > i:
                    # faz for na lista com as reatâncias xij obtidas
                    # em ordem
                    for reat in aux_fase_b:
                        # se xij for 0, ou seja, não foi calulado
                        if xb[i, j] == 0:
                            # atribiu-se o valor de reat a xij e xji
                            xb[i, j] = reat
                            xb[j, i] = reat
                            # remove o elemento para não utilizar
                            # novamente
                            aux_fase_b.remove(reat)
                            # quebra o for para não substituir
                            # os valores de outros xij
                            break
                        # se xij for diferente de zero não faz nada
                        else:
                            pass
        # for onde a matriz xc será preenchida
        for i in range(np.shape(xc)[0]):
            for j in range(np.shape(xc)[1]):
                # se é um elemento da diagonal principal
                if i == j:
                    # percorre a primeira lista auxiliar
                    for no in listageradores_fase_c:
                        # atribui a xii atual a reatância
                        xc[i, j] = self.xii(alimentador, no.nome)
                        # remove o nó atual para não utilizado
                        # novamente
                        listageradores_fase_c.remove(no)
                        # quebra o for para não calcular x22, x33..
                        # e substituir no lugar de x11
                        break
                # se é um elemento em que o número da coluna é maior
                # do que a linha
                elif j > i:
                    # faz for na lista com as reatâncias xij obtidas
                    # em ordem
                    for reat in aux_fase_c:
                        # se xij for 0, ou seja, não foi calulado
                        if xc[i, j] == 0:
                            # atribiu-se o valor de reat a xij e xji
                            xc[i, j] = reat
                            xc[j, i] = reat
                            # remove o elemento para não utilizar
                            # novamente
                            aux_fase_c.remove(reat)
                            # quebra o for para não substituir
                            # os valores de outros xij
                            break
                        # se xij for diferente de zero não faz nada
                        else:
                            pass
        return xa, xb, xc

    def reativo(self, alimentador):
        """ função que calcula a matriz de diferença de potência reativa dos
        geradores não convergidos, regula a potência injetada/absorvida e
        verifica se o limite de potência reativa inferior ou superior não
        foi alcançada"""

        # calcula a matriz de diferença de potência dos geradores
        # não convergidos
        dq_fase_a = np.dot(linalg.inv(self.matrix_reatancia(alimentador)[0]), self.tensaogerador(alimentador)[2])
        dq_fase_b = np.dot(linalg.inv(self.matrix_reatancia(alimentador)[1]), self.tensaogerador(alimentador)[5])
        dq_fase_c = np.dot(linalg.inv(self.matrix_reatancia(alimentador)[2]), self.tensaogerador(alimentador)[8])
        # percorre a lista com geradores para verificar o seu patamar de tensão
        for dv_fase_a, pot_fase_a, ger_fase_a in zip(self.tensaogerador(alimentador)[2], dq_fase_a, self.tensaogerador(alimentador)[0]):
            # se a diferença de tensão for maior do que zero o gerador
            # aumenta a produção de reativo
            if dv_fase_a > 0:
                ger_fase_a.potencia_fase_a.imag = ger_fase_a.potencia_fase_a.imag - 3 * pot_fase_a[0]
            # se a diferença de tensão for menor do que zero o gerador
            # reduz a produção de reativo
            elif dv_fase_a < 0:
                ger_fase_a.potencia_fase_a.imag = ger_fase_a.potencia_fase_a.imag + 3 * pot_fase_a[0]
            # se a potência do gerador ultrapassou o seu limite superior
            # atribui-se o limite superior a potência reativa do gerador
            if abs(ger_fase_a.potencia_fase_a.imag) > abs(ger_fase_a.qmax):
                ger_fase_a.potencia_fase_a.imag = -ger_fase_a.qmax
            # se a potência do gerador ultrapassou o seu limite inferior
            # atribui-se o limite inferior a potência reativa do gerador
            elif abs(ger_fase_a.potencia_fase_a.imag) < abs(ger_fase_a.qmin):
                ger_fase_a.potencia_fase_a.imag = -ger_fase_a.qmin

        for dv_fase_b, pot_fase_b, ger_fase_b in zip(self.tensaogerador(alimentador)[5], dq_fase_b, self.tensaogerador(alimentador)[3]):
            # se a diferença de tensão for maior do que zero o gerador
            # aumenta a produção de reativo
            if dv_fase_b > 0:
                ger_fase_b.potencia_fase_b.imag = ger_fase_b.potencia_fase_b.imag - 3 * pot_fase_b[0]
            # se a diferença de tensão for menor do que zero o gerador
            # reduz a produção de reativo
            elif dv_fase_b < 0:
                ger_fase_b.potencia_fase_b.imag = ger_fase_b.potencia_fase_b.imag + 3 * pot_fase_b[0]
            # se a potência do gerador ultrapassou o seu limite superior
            # atribui-se o limite superior a potência reativa do gerador
            if abs(ger_fase_b.potencia_fase_b.imag) > abs(ger_fase_b.qmax):
                ger_fase_b.potencia_fase_b.imag = -ger_fase_b.qmax
            # se a potência do gerador ultrapassou o seu limite inferior
            # atribui-se o limite inferior a potência reativa do gerador
            elif abs(ger_fase_b.potencia_fase_b.imag) < abs(ger_fase_b.qmin):
                ger_fase_b.potencia_fase_b.imag = -ger_fase_b.qmin

        for dv_fase_c, pot_fase_c, ger_fase_c in zip(self.tensaogerador(alimentador)[8], dq_fase_c, self.tensaogerador(alimentador)[6]):
            # se a diferença de tensão for maior do que zero o gerador
            # aumenta a produção de reativo
            if dv_fase_c > 0:
                ger_fase_c.potencia_fase_c.imag = ger_fase_c.potencia_fase_c.imag - 3 * pot_fase_c[0]
            # se a diferença de tensão for menor do que zero o gerador
            # reduz a produção de reativo
            elif dv_fase_c < 0:
                ger_fase_c.potencia_fase_c.imag = ger_fase_c.potencia_fase_b.imag + 3 * pot_fase_c[0]
            # se a potência do gerador ultrapassou o seu limite superior
            # atribui-se o limite superior a potência reativa do gerador
            if abs(ger_fase_c.potencia_fase_c.imag) > abs(ger_fase_c.qmax):
                ger_fase_c.potencia_fase_c.imag = -ger_fase_c.qmax
            # se a potência do gerador ultrapassou o seu limite inferior
            # atribui-se o limite inferior a potência reativa do gerador
            elif abs(ger_fase_c.potencia_fase_c.imag) < abs(ger_fase_c.qmin):
                ger_fase_c.potencia_fase_c.imag = -ger_fase_c.qmin

    def xii(self, alimentador, no_):
        """ função que calcula a reatância de um gerador até o nó raiz """
        # variável que guarda os techos do alimentador
        trechos = alimentador.trechos.values()
        # variável que guarda o caminho do nó até o nó raiz
        caminho = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_)[1]
        # faz uma lista do array caminho
        caminho = list(caminho)
        # faz uma lista em outra variável auxiliar
        caminho_2 = list(caminho)
        # lista que servirá para guardar os trechos
        tr = []
        reat = 0
        # for que percorre o caminho
        for no in caminho:
            # for que percorre os trechos
            for trecho in trechos:
                # se o n1 do trecho for igual ao nó atual
                if trecho.n1.nome == no:
                    # se não for uma chave
                    if type(trecho.n2) == NoDeCarga or type(trecho.n2) == Gerador:
                        # se o n2 ta no caminho e o n2 não for o próprio no
                        if trecho.n2.nome in caminho_2 and trecho.n2.nome != no:
                            # adiciona a reatancia do trecho
                            reat += (trecho.comprimento * trecho.condutor.xp)
                            # guarda o trecho
                            tr.append(trecho)
                    # se for uma chave
                    else:
                        # guarda o nó ontem existe a chave
                        no_1 = alimentador.nos_de_carga[no]
                        try:
                            # tenta pegar o próximo nó da iteração
                            no_2 = alimentador.nos_de_carga[caminho_2[1]]
                            # como se está removendo os nós o indice irá variar
                            # para tanto, se houver erro de indice ele continua
                        except IndexError:
                            continue
                        # cria um conjunto com as chaves do nó atual
                        set_1 = set(no_1.chaves)
                        # cria um conjunto com as chaves do nó da próxima
                        # interação
                        set_2 = set(no_2.chaves)
                        # se a interseção das chaves dos nós for
                        # diferente de vazio ele guarda a chave
                        if set_1.intersection(set_2) != set():
                            chave = set_1.intersection(set_2).pop()
                        else:
                            # se a interseção for vazia ele vai para a próxima
                            # iteração
                            continue
                        # caso a chave seja diferente do n2 vai para a próxima
                        # iteração
                        if chave != trecho.n2.nome:
                            continue
                        # percorre os trechos
                        for trech in trechos:
                            # se o n1 for a chave
                            if trech.n1.nome == chave:
                                # guarda o trecho
                                tr.append(trech)
                                # adiciona a reatancia do trecho
                                reat += (trech.comprimento * trech.condutor.xp)
                            # se o n2 for a chave
                            elif trech.n2.nome == chave:
                                # adiciona a reatancia do trecho
                                reat += (trech.comprimento * trech.condutor.xp)
                                # guarda o trecho
                                tr.append(trech)
                # realiza as mesmas lógicas quando o nó é n1
                elif trecho.n2.nome == no:
                    if type(trecho.n1) == NoDeCarga or type(trecho.n1) == Gerador:
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

        return reat

    def xij(self, alimentador, no_1, no_2):
        """ função que calcula a reatância de um caminho compartilhado
        por dois geradores da rede """
        # guarda o caminho dos geradores até o nó raiz
        caminho_1 = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_1)
        caminho_2 = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_2)
        # variáveis auxiliares
        max_prof = 0
        no_max = None
        # faz for na lista de nos e na lista de profundidade
        for i, ix in zip(caminho_1[1, :], caminho_1[0, :]):
            for j, jx in zip(caminho_2[1, :], caminho_2[0, :]):
                # caso se encontro o nó de interseção das duas listas
                if i == j:
                    # se a profundidade for maior do que a máxima
                    if int(ix) > max_prof:
                        # atribui a max_prof a profundidade atual
                        max_prof = int(ix)
                        # atribui ao no_max o no de menor profundidade
                        no_max = i

        return self.xii(alimentador, no_max)

    def calcular_fluxo_pq(self, alimentador):
        max_iteracaoes = 50
        criterio_converg = 0.001
        converg = 1e6
        iter = 0

        print '============================'
        print 'Varredura no alimentador {al}'.format(al=alimentador.nome)

        # dicionário que guarda o nome dos nós e atribui o critério de convergência
        converg_nos_fase_a = dict()
        converg_nos_fase_b = dict()
        converg_nos_fase_c = dict()
        for no in alimentador.nos_de_carga.values():
            converg_nos_fase_a[no.nome] = 1e6
            converg_nos_fase_b[no.nome] = 1e6
            converg_nos_fase_c[no.nome] = 1e6
        # testa se o máximo de iterações foi alcançada e a convergência
        while iter <= max_iteracaoes and converg > criterio_converg:
            iter += 1
            #print '-------------------------'
            #print 'Iteração: {iter}'.format(iter=iter)
            # dicionário que guarda as o nome dos nós na chave a suas tensões nos valores
            tensao_nos_fase_a = dict()
            tensao_nos_fase_b = dict()
            tensao_nos_fase_c = dict()
            for no in alimentador.nos_de_carga.values():
                tensao_nos_fase_a[no.nome] = Fasor(real=no.tensao_fase_a.real,
                                                   imag=no.tensao_fase_a.imag,
                                                   tipo=Fasor.Tensao)
                tensao_nos_fase_b[no.nome] = Fasor(real=no.tensao_fase_b.real,
                                                   imag=no.tensao_fase_b.imag,
                                                   tipo=Fasor.Tensao)
                tensao_nos_fase_c[no.nome] = Fasor(real=no.tensao_fase_c.real,
                                                   imag=no.tensao_fase_c.imag,
                                                   tipo=Fasor.Tensao)
            # varre o alimentador calculado as potências e as tensões
            self._varrer_alimentador(alimentador)
            # faz a diferença entre os valores de tensões passados e valores de
            # tensões atuais para verificar a convergência
            for no in alimentador.nos_de_carga.values():
                converg_nos_fase_a[no.nome] = abs(tensao_nos_fase_a[no.nome].mod - no.tensao_fase_a.mod)
                converg_nos_fase_b[no.nome] = abs(tensao_nos_fase_b[no.nome].mod - no.tensao_fase_b.mod)
                converg_nos_fase_c[no.nome] = abs(tensao_nos_fase_c[no.nome].mod - no.tensao_fase_c.mod)
            # toma o valor máximo de diferença de tensão para todos os nós da rede
            converg_fase_a = max(converg_nos_fase_a.values())
            converg_fase_b = max(converg_nos_fase_b.values())
            converg_fase_c = max(converg_nos_fase_c.values())

            converg = max(converg_fase_a, converg_fase_b, converg_fase_c)
            # print 'Max. diferença de tensões: {conv}'.format(conv=converg)
        # se convergiu retorna verdadeiro, se não convergiu retorna falso
        if converg < criterio_converg:
            return True
        else:
            return False

    def calcular_fluxo_de_carga(self):
        # atribui a tensão da subestação e a todos os nós da rede
        f1 = Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao)
        self._atribuir_tensao_a_subestacao(f1)
        # for  que percorre os alimentadores da subestação dada
        for alimentador in self.alimentadores.values():
            # atribui potência negativa para os geradores da rede
            self.atribuir_potencia(alimentador)
            # chama o método para a realização do backward/forward sweep
            converg = self.calcular_fluxo_pq(alimentador)
            # se o fluxo de carga convergiu se realiza a análise dos geradores
            if converg:
                max_iteracoes = 100
                iter = 0

                while True:
                    # armazena lista com os geradores, a quantidade deles e a
                    # matriz  com a diferença de tensão em cada um
                    listager_fase_a, count_fase_a, diftensao_fase_a = self.tensaogerador(alimentador)[0], self.tensaogerador(alimentador)[1], self.tensaogerador(alimentador)[2]
                    listager_fase_b, count_fase_b, diftensao_fase_b = self.tensaogerador(alimentador)[3], self.tensaogerador(alimentador)[4], self.tensaogerador(alimentador)[5]
                    listager_fase_c, count_fase_c, diftensao_fase_c = self.tensaogerador(alimentador)[6], self.tensaogerador(alimentador)[7], self.tensaogerador(alimentador)[8]
                    iter += 1
                    if iter >= max_iteracoes or listager_fase_a == [] and listager_fase_b == [] and listager_fase_c ==[]:
                        if iter >= max_iteracoes:
                            print 'Numero maximo de iteracoes atingidas'
                        elif listager_fase_a == [] and listager_fase_b == [] and listager_fase_c == []:
                            print 'Convergencia atingida'
                        break
                    else:
                        # calculo do reativo para os geradores
                        self.reativo(alimentador)
                        converg = self.calcular_fluxo_pq(alimentador)
                        if not converg:
                            break



class Trecho(Aresta):
    def __init__(self,
                 nome,
                 n1,
                 n2,
                 fluxo_fase_a=None,
                 fluxo_fase_b=None,
                 fluxo_fase_c=None,
                 condutor=None,
                 comprimento=None,
                 resistenciacontato=100):
        assert isinstance(nome, str), 'O parâmetro nome da classe Trecho ' \
                                      'deve ser do tipo str'
        assert isinstance(n1, NoDeCarga) or isinstance(n1, Chave) or isinstance(n1, Gerador), 'O parâmetro n1 da classe Trecho ' \
                                                                                              'deve ser do tipo No de carga ' \
                                                                                              'ou do tipo Chave'
        assert isinstance(n2, NoDeCarga) or isinstance(n2, Chave) or isinstance(n2, Gerador), 'O parâmetro n2 da classe Trecho ' \
                                                                                              'deve ser do tipo No de carga ' \
                                                                                              'ou do tipo Chave'
        super(Trecho, self).__init__(nome)
        self.n1 = n1
        self.n2 = n2
        self.no_montante = None
        self.no_jusante = None
        self.condutor = condutor
        self.comprimento = comprimento
        self.impedancia_positiva = (self.condutor.rp + self.condutor.xp * 1j) * self.comprimento
        self.impedancia_zero = (self.condutor.rz + self.condutor.xz * 1j) * self.comprimento
        self.resistencia_contato = resistenciacontato

        if fluxo_fase_a is None:
            self.fluxo_fase_a = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)
        else:
            self.fluxo_fase_a = fluxo_fase_a

        if fluxo_fase_a is None:
            self.fluxo_fase_b = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)
        else:
            self.fluxo_fase_b = fluxo_fase_b

        if fluxo_fase_a is None:
            self.fluxo_fase_c = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)
        else:
            self.fluxo_fase_c = fluxo_fase_c

    def calcula_impedancia(self):
        return (self.comprimento * self.condutor.rp,
                self.comprimento * self.condutor.xp)

    def calcula_curto_monofasico(self):
        curto1 = (3.0) * self.base.corrente / (2 * self.impedancia_equivalente_positiva + self.impedancia_equivalente_zero)
        correntecc = Fasor(real=curto1.real, imag=curto1.imag, tipo=Fasor.Corrente)
        correntecc.base = self.base
        return correntecc

    def calcula_curto_bifasico(self):
        curto2 = (3 ** 0.5) * self.base.corrente / (2 * self.impedancia_equivalente_positiva)
        correntecc = Fasor(real=curto2.real, imag=curto2.imag, tipo=Fasor.Corrente)
        correntecc.base = self.base
        return correntecc

    def calcula_curto_trifasico(self):
        curto3 = 1.0 * self.base.corrente / (self.impedancia_equivalente_positiva)
        correntecc = Fasor(real=curto3.real, imag=curto3.imag, tipo=Fasor.Corrente)
        correntecc.base = self.base
        return correntecc

    def calcula_curto_monofasico_minimo(self):
        curto1m = 3.0 * self.base.corrente / (2 * self.impedancia_equivalente_positiva + self.impedancia_equivalente_zero+3*self.resistencia_contato/self.base.impedancia)
        correntecc = Fasor(real=curto1m.real, imag=curto1m.imag, tipo=Fasor.Corrente)
        correntecc.base = self.base
        return correntecc

    def __repr__(self):
        return 'Trecho: %s' % self.nome


class Alimentador(Arvore):
    def __init__(self, nome, setores, trechos, chaves):
        assert isinstance(nome, str), 'O parâmetro nome da classe Alimentador' \
                                      'deve ser do tipo string'
        assert isinstance(setores, list), 'O parâmetro setores da classe' \
                                          'Alimentador deve ser do tipo list'
        assert isinstance(chaves, list), 'O parâmetro chaves da classe' \
                                         'Alimentador deve ser do tipo list'
        self.nome = nome

        self.setores = dict()
        for setor in setores:
            self.setores[setor.nome] = setor

        self.chaves = dict()
        for chave in chaves:
            self.chaves[chave.nome] = chave

        self.nos_de_carga = dict()
        for setor in setores:
            for no in setor.nos_de_carga.values():
                self.nos_de_carga[no.nome] = no

        self.trechos = dict()
        for trecho in trechos:
            self.trechos[trecho.nome] = trecho

        for setor in self.setores.values():
            print 'Setor: ', setor.nome
            setores_vizinhos = list()
            for chave in self.chaves.values():
                if chave.n1 is setor:
                    setores_vizinhos.append(chave.n2)
                elif chave.n2 is setor:
                    setores_vizinhos.append(chave.n1)

            for setor_vizinho in setores_vizinhos:
                print 'Setor Vizinho: ', setor_vizinho.nome
                nos_de_ligacao = list()
                for i in setor.nos_de_carga.values():
                    for j in setor_vizinho.nos_de_carga.values():
                        if i.nome in j.vizinhos:
                            nos_de_ligacao.append((j, i))

                for no in nos_de_ligacao:
                    setor.ordenar(no[1].nome)
                    setor.rnp_associadas[setor_vizinho.nome] = (no[0],
                                                                setor.rnp)
                    print 'RNP: ', setor.rnp

        _arvore_da_rede = self._gera_arvore_da_rede()

        super(Alimentador, self).__init__(_arvore_da_rede, str)

    def ordenar(self, raiz):
        super(Alimentador, self).ordenar(raiz)

        for setor in self.setores.values():
            caminho = self.caminho_no_para_raiz(setor.nome)
            if setor.nome != raiz:
                setor_jusante = caminho[1, 1]
                setor.rnp = setor.rnp_associadas[setor_jusante][1]

    def _gera_arvore_da_rede(self):

        arvore_da_rede = {i: list() for i in self.setores.keys()}

        for chave in self.chaves.values():
            if chave.n1.nome in self.setores.keys() and chave.estado == 1:
                arvore_da_rede[chave.n1.nome].append(chave.n2.nome)
            if chave.n2.nome in self.setores.keys() and chave.estado == 1:
                arvore_da_rede[chave.n2.nome].append(chave.n1.nome)

        return arvore_da_rede

    def gerar_arvore_nos_de_carga(self):

        # define os nós de carga do setor raiz da subestação como os primeiros
        # nós de carga a povoarem a arvore nós de carga e a rnp nós de carga
        setor_raiz = self.setores[self.rnp[1][0]]
        self.arvore_nos_de_carga = Arvore(arvore=setor_raiz._gera_arvore_do_setor(),
                                          dtype=str)
        self.arvore_nos_de_carga.ordenar(raiz=setor_raiz.rnp[1][0])

        # define as listas visitados e pilha, necessárias ao
        # processo recursivo de visita
        # dos setores da subestação
        visitados = []
        pilha = []

        # inicia o processo iterativo de visita dos setores
        # em busca de seus respectivos nós de carga
        self._gerar_arvore_nos_de_carga(setor_raiz, visitados, pilha)

    def _gerar_arvore_nos_de_carga(self, setor, visitados, pilha):

        # atualiza as listas de recursão
        visitados.append(setor.nome)
        pilha.append(setor.nome)

        # for percorre os setores vizinhos ao setor atual
        # que ainda não tenham sido visitados
        vizinhos = setor.vizinhos
        for i in vizinhos:

            # esta condição testa se existe uma ligação
            # entre os setores de uma mesma subestação, mas
            # que possuem uma chave normalmente aberta entre eles.
            # caso isto seja constatado o laço for é interrompido.
            if i not in visitados and i in self.setores.keys():
                for c in self.chaves.values():
                    if c.n1.nome == setor.nome and c.n2.nome == i:
                        if c.estado == 1:
                            break
                        else:
                            pass
                    elif c.n2.nome == setor.nome and c.n1.nome == i:
                        if c.estado == 1:
                            break
                        else:
                            pass
                else:
                    continue
                prox = i
                setor_vizinho = self.setores[i]
                no_insersao, rnp_insersao = setor_vizinho.rnp_associadas[setor.nome]
                arvore_insersao = setor_vizinho._gera_arvore_do_setor()

                setor_vizinho.no_de_ligacao = no_insersao

                setor_vizinho.rnp = rnp_insersao

                self.arvore_nos_de_carga.inserir_ramo(no_insersao.nome,
                                                      (rnp_insersao,
                                                       arvore_insersao),
                                                      no_raiz=rnp_insersao[1, 0]
                                                      )
                break
            else:
                continue
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._gerar_arvore_nos_de_carga(self.setores[anter],
                                                       visitados, pilha)
            else:
                return
        return self._gerar_arvore_nos_de_carga(self.setores[prox],
                                               visitados,
                                               pilha)

    def atualizar_arvore_da_rede(self):
        _arvore_da_rede = self._gera_arvore_da_rede()
        self.arvore = _arvore_da_rede

    def gerar_trechos_da_rede(self):

        self.trechos = dict()

        j = 0
        for i in range(1, np.size(self.arvore_nos_de_carga.rnp, axis=1)):
            prof_1 = int(self.arvore_nos_de_carga.rnp[0, i])
            prof_2 = int(self.arvore_nos_de_carga.rnp[0, j])

            while abs(prof_1 - prof_2) is not 1:
                if abs(prof_1 - prof_2) == 0:
                    j -= 1
                elif abs(prof_1 - prof_2) == 2:
                    j = i - 1
                prof_2 = int(self.arvore_nos_de_carga.rnp[0, j])
            else:
                n_1 = str(self.arvore_nos_de_carga.rnp[1, j])
                n_2 = str(self.arvore_nos_de_carga.rnp[1, i])
                setor_1 = None
                setor_2 = None
                print 'Trecho: ' + n_1 + '-' + n_2

                # verifica quais os nós de carga existentes nas extremidades do trecho
                # e se existe uma chave no trecho

                for setor in self.setores.values():
                    if n_1 in setor.nos_de_carga.keys():
                        setor_1 = setor
                    if n_2 in setor.nos_de_carga.keys():
                        setor_2 = setor

                    if setor_1 is not None and setor_2 is not None:
                        break
                else:
                    if setor_1 is None:
                        n = n_1
                    else:
                        n = n_2
                    for setor in self.setores.values():
                        if n in setor.nos_de_carga.keys() and np.size(setor.rnp, axis=1) == 1:
                            if setor_1 is None:
                                setor_1 = setor
                            else:
                                setor_2 = setor
                            break

                if setor_1 != setor_2:
                    for chave in self.chaves.values():
                        if chave.n1 in (setor_1, setor_2) and chave.n2 in (setor_1, setor_2):
                            self.trechos[n_1 + n_2] = Trecho(nome=n_1 + n_2,
                                                             n1=self.nos_de_carga[n_1],
                                                             n2=self.nos_de_carga[n_2],
                                                             chave=chave)
                else:
                    self.trechos[n_1 + n_2] = Trecho(nome=n_1 + n_2,
                                                     n1=self.nos_de_carga[n_1],
                                                     n2=self.nos_de_carga[n_2])

    def calcular_potencia(self):
        potencia = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        for no in self.nos_de_carga.values():
            potencia = potencia + no.potencia

        return potencia

    def podar(self, no, alterar_rnp=False):
        poda = super(Alimentador, self).podar(no, alterar_rnp)
        rnp_setores = poda[0]
        arvore_setores = poda[1]

        if alterar_rnp:
            # for povoa dicionario com setores podados
            setores = dict()
            for i in rnp_setores[1, :]:
                setor = self.setores.pop(i)
                setores[setor.nome] = setor

            # for povoa dicionario com nos de carga podados
            nos_de_carga = dict()
            for setor in setores.values():
                for j in setor.nos_de_carga.values():
                    if j.nome in self.nos_de_carga.keys():
                        no_de_carga = self.nos_de_carga.pop(j.nome)
                        nos_de_carga[no_de_carga.nome] = no_de_carga

            # for atualiza a lista de nós de carga da subestação
            # excluindo os nós de carga podados
            for setor in self.setores.values():
                for no_de_carga in setor.nos_de_carga.values():
                    self.nos_de_carga[no_de_carga.nome] = no_de_carga
                    if no_de_carga.nome in nos_de_carga.keys():
                        nos_de_carga.pop(no_de_carga.nome)

            # poda o ramo na arvore da subetação
            poda = self.arvore_nos_de_carga.podar(setores[no].rnp[1, 0], alterar_rnp=alterar_rnp)
            rnp_nos_de_carga = poda[0]
            arvore_nos_de_carga = poda[1]

            # for povoa dicionario de chaves que estao nos trechos podados
            # e retira do dicionario de chaves da arvore que esta sofrendo a poda
            # as chaves que não fazem fronteira com os trechos remanescentes
            chaves = dict()
            for chave in self.chaves.values():
                if chave.n1.nome in setores.keys():
                    if not chave.n2.nome in self.setores.keys():
                        chaves[chave.nome] = self.chaves.pop(chave.nome)
                    else:
                        chave.estado = 0
                        chaves[chave.nome] = chave
                elif chave.n2.nome in setores.keys():
                    if not chave.n1.nome in self.setores.keys():
                        chaves[chave.nome] = self.chaves.pop(chave.nome)
                    else:
                        chave.estado = 0
                        chaves[chave.nome] = chave

            # for poda os trechos dos setores podados e povoa o dicionario trechos
            # para que possa ser repassado juntamente com os outros dados da poda
            trechos = dict()
            for no in rnp_nos_de_carga[1, :]:
                for trecho in self.trechos.values():
                    if trecho.n1.nome == no or trecho.n2.nome == no:
                        trechos[trecho.nome] = self.trechos.pop(trecho.nome)

            return (setores, arvore_setores, rnp_setores,
                    nos_de_carga, arvore_nos_de_carga, rnp_nos_de_carga,
                    chaves, trechos)
        else:
            return rnp_setores

    def inserir_ramo(self, no, poda, no_raiz=None):

        (setores, arvore_setores, rnp_setores,
         nos_de_carga, arvore_nos_de_carga, rnp_nos_de_carga,
         chaves, trechos) = poda

        if no_raiz is None:
            setor_inserir = setores[rnp_setores[1, 0]]
        else:
            setor_inserir = setores[no_raiz]

        setor_insersao = self.setores[no]

        # for identifica se existe alguma chave que permita a inserção do ramo na arvore
        # da subestação que ira receber a inserção.
        chaves_de_lig = dict()
        # for percorre os nos de carga do setor de insersão
        for i in self.setores[setor_insersao.nome].nos_de_carga.values():
            # for percorre as chaves associadas ao no de carga
            for j in i.chaves:
                # for percorre os nos de carga do setor raiz do ramo a ser inserido
                for w in setores[setor_inserir.nome].nos_de_carga.values():
                    # se a chave pertence aos nos de carga i e w então é uma chave de ligação
                    if j in w.chaves:
                        chaves_de_lig[j] = (i, w)

        if not chaves_de_lig:
            print 'A insersao não foi possível pois nenhuma chave de fronteira foi encontrada!'
            return

        i = randint(0, len(chaves_de_lig) - 1)
        n1, n2 = chaves_de_lig[chaves_de_lig.keys()[i]]

        self.chaves[chaves_de_lig.keys()[i]].estado = 1

        if setor_inserir.nome == setores[rnp_setores[1, 0]].nome:
            super(Alimentador, self).inserir_ramo(no, (rnp_setores, arvore_setores))
        else:
            super(Alimentador, self).inserir_ramo(no, (rnp_setores, arvore_setores), no_raiz)

        # atualiza setores do alimentador
        self.setores.update(setores)

        # atualiza os nos de carga do alimentador
        self.nos_de_carga.update(nos_de_carga)

        # atualiza as chaves do alimentador
        self.chaves.update(chaves)

        # atualiza os trechos do alimentador
        self.trechos.update(trechos)

        # atualiza a arvore de setores do alimentador
        self.atualizar_arvore_da_rede()

        # atualiza a arvore de nos de carga do alimentador
        self.gerar_arvore_nos_de_carga()


class Chave(Aresta):
    def __init__(self, nome, estado=1):
        assert estado == 1 or estado == 0, 'O parâmetro estado deve ser um inteiro de valor 1 ou 0'
        super(Chave, self).__init__(nome)
        self.estado = estado

    def __str__(self):
        if self.n1 is not None and self.n2 is not None:
            return 'Chave: %s - n1: %s, n2: %s' % (self.nome, self.n1.nome, self.n2.nome)
        else:
            return 'Chave: %s' % self.nome


class Transformador(object):
    def __init__(self, nome, tensao_primario, tensao_secundario, potencia, impedancia):
        assert isinstance(nome, str), 'O parâmetro nome deve ser do tipo str'
        assert isinstance(tensao_secundario, Fasor), 'O parâmetro tensao_secundario deve ser do tipo Fasor'
        assert isinstance(tensao_primario, Fasor), 'O parâmetro tensao_primario deve ser do tipo Fasor'
        assert isinstance(potencia, Fasor), 'O parâmetro potencia deve ser do tipo Fasor'
        assert isinstance(impedancia, Fasor), 'O parâmetro impedancia deve ser do tipo Fasor'

        self.nome = nome
        self.tensao_primario = tensao_primario
        self.tensao_secundario = tensao_secundario
        self.potencia = potencia
        self.impedancia = impedancia


class Condutor(object):
    def __init__(self, nome, rp, xp, rz, xz, ampacidade):
        self.nome = nome
        self.rp = float(rp)
        self.xp = float(xp)
        self.rz = float(rz)
        self.xz = float(xz)
        self.ampacidade = float(ampacidade)


if __name__ == '__main__':
    # Este trecho do módulo faz parte de sua documentacao e serve como exemplo de como
    # utiliza-lo. Uma pequena rede com duas subestações é representada.

    # Na Subestação S1 existem três setores de carga: A, B, C.
    # O setor A possui três nós de carga: A1, A2, e A3
    # O setor B possui três nós de carga: B1, B2, e B3
    # O setor C possui três nós de carga: C1, C2, e C3
    # O nó de carga S1 alimenta o setor A por A2 através da chave 1
    # O nó de carga A3 alimenta o setor B por B1 através da chave 2
    # O nó de carga A2 alimenta o setor C por C1 através da chave 3

    # Na Subestação S2 existem dois setores de carga: D e E.
    # O setor D possui três nós de carga: D1, D2, e D3
    # O setor E possui três nós de carga: E1, E2, e E3
    # O nó de carga S2 alimenta o setor D por D1 através da chave 6
    # O nó de carga D1 alimenta o setor E por E1 através da chave 7

    # A chave 4 interliga os setores B e E respectivamente por B2 e E2
    # A chave 5 interliga os setores B e C respectivamente por B3 e C3
    # A chave 8 interliga os setores C e E respectivamente por C3 e E3

    # Para representar a rede são criados então os seguintes objetos:
    # _chaves : dicionario contendo objetos do tipo chave que representam
    # as chaves do sistema;
    # _seotores_1 : dicionario contendo objetos setor que representam
    # os setores da Subestação S1;
    # _seotores_2 : dicionario contendo objetos setor que representam
    # os setores da Subestação S2;
    # _nos : dicionarios contendo objetos nos_de_carga que representam
    # os nós de carga dos setores em cada um dos trechos das
    # subestações;
    # _subestacoes : dicionario contendo objetos Subestacao que herdam
    # a classe Arvore e contém todos os elementos que
    # representam um ramo da rede elétrica, como chaves, setores,
    # nós de carga e trechos;

    # chaves do alimentador de S1
    ch1 = Chave(nome='1', estado=1)
    ch2 = Chave(nome='2', estado=1)
    ch3 = Chave(nome='3', estado=1)

    # chaves de Fronteira
    ch4 = Chave(nome='4', estado=0)
    ch5 = Chave(nome='5', estado=0)
    ch8 = Chave(nome='8', estado=0)

    # chaves do alimentador de S2
    ch6 = Chave(nome='6', estado=1)
    ch7 = Chave(nome='7', estado=1)

    # Nos de carga do alimentador S1_AL1
    s1 = NoDeCarga(nome='S1',
                   vizinhos=['A2'],
                   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['1'])
    a1 = NoDeCarga(nome='A1',
                   vizinhos=['A2'],
                   potencia_fase_a=Fasor(real=460.0e3, imag=250.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=460.0e3, imag=250.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=460.0e3, imag=250.0e3, tipo=Fasor.Potencia),)
    a2 = NoDeCarga(nome='A2',
                   vizinhos=['S1', 'A1', 'A3', 'C1'],
                   potencia_fase_a=Fasor(real=350.0e3, imag=220.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=350.0e3, imag=220.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=350.0e3, imag=220.0e3, tipo=Fasor.Potencia),
                   chaves=['1', '3'])
    a3 = NoDeCarga(nome='A3',
                   vizinhos=['A2', 'B1'],
                   potencia_fase_a=Fasor(real=500.0e3, imag=280.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=500.0e3, imag=280.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=500.0e3, imag=280.0e3, tipo=Fasor.Potencia),
                   chaves=['2'])
    b1 = Gerador(nome='B1',
                 vizinhos=['B2', 'A3'],
                 dvtol=1,
                 potencia_fase_a=Fasor(real=110e3, imag=80e3, tipo=Fasor.Potencia),
                 potencia_fase_b=Fasor(real=110e3, imag=80e3, tipo=Fasor.Potencia),
                 potencia_fase_c=Fasor(real=110e3, imag=80e3, tipo=Fasor.Potencia),
                 chaves=['2'],
                 tipogerador='AEROGERADOR',
                 maquina='DFIG',
                 modelofluxo='PV',
                 qmin=30e3,
                 qmax=650e3,
                 tensaogerador=13800)
    b2 = NoDeCarga(nome='B2',
                   vizinhos=['B1', 'B3', 'E2'],
                   potencia_fase_a=Fasor(real=450.0e3, imag=230.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=450.0e3, imag=230.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=450.0e3, imag=230.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    b3 = NoDeCarga(nome='B3',
                   vizinhos=['B2', 'C3'],
                   potencia_fase_a=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['5'])
    c1 = Gerador(nome='C1',
                 vizinhos=['C2', 'C3', 'A2'],
                 dvtol=1,
                 potencia_fase_a=Fasor(real=90e3, imag=55e3, tipo=Fasor.Potencia),
                 potencia_fase_b=Fasor(real=90e3, imag=55e3, tipo=Fasor.Potencia),
                 potencia_fase_c=Fasor(real=90e3, imag=55e3, tipo=Fasor.Potencia),
                 chaves=['3'],
                 tipogerador='FOTOVOLTAICO',
                 maquina='',
                 modelofluxo='PV',
                 qmin=20e3,
                 qmax=650e3,
                 tensaogerador=13800)
    c2 = NoDeCarga(nome='C2',
                   vizinhos=['C1'],
                   potencia_fase_a=Fasor(real=650.0e3, imag=330.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=650.0e3, imag=330.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=650.0e3, imag=330.0e3, tipo=Fasor.Potencia),)
    c3 = NoDeCarga(nome='C3',
                   vizinhos=['C1', 'E3', 'B3'],
                   potencia_fase_a=Fasor(real=300.0e3, imag=180.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=300.0e3, imag=180.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=300.0e3, imag=180.0e3, tipo=Fasor.Potencia),
                   chaves=['5', '8'])

    # Nos de carga do alimentador S2_AL1
    s2 = NoDeCarga(nome='S2',
                   vizinhos=['D1'],
                   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['6'])
    d1 = NoDeCarga(nome='D1',
                   vizinhos=['S2', 'D2', 'D3', 'E1'],
                   potencia_fase_a=Fasor(real=200.0e3, imag=160.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=200.0e3, imag=160.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=200.0e3, imag=160.0e3, tipo=Fasor.Potencia),
                   chaves=['6', '7'])
    d2 = NoDeCarga(nome='D2',
                   vizinhos=['D1'],
                   potencia_fase_a=Fasor(real=90.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=90.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=90.0e3, imag=40.0e3, tipo=Fasor.Potencia),)
    d3 = NoDeCarga(nome='D3',
                   vizinhos=['D1'],
                   potencia_fase_a=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),)
    e1 = NoDeCarga(nome='E1',
                   vizinhos=['E3', 'E2', 'D1'],
                   potencia_fase_a=Fasor(real=100.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=100.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=100.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   chaves=['7'])
    e2 = NoDeCarga(nome='E2',
                   vizinhos=['E1', 'B2'],
                   potencia_fase_a=Fasor(real=110.0e3, imag=70.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=110.0e3, imag=70.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=110.0e3, imag=70.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    e3 = NoDeCarga(nome='E3',
                   vizinhos=['E1', 'C3'],
                   potencia_fase_a=Fasor(real=150.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_b=Fasor(real=150.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   potencia_fase_c=Fasor(real=150.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['8'])

    cond_1 = Condutor(nome='CAA 266R', rp=0.2391, xp=0.37895, rz=0.41693, xz=1.55591, ampacidade=301)

    # Trechos do alimentador S1_AL1
    s1_ch1 = Trecho(nome='S1CH1', n1=s1, n2=ch1, condutor=cond_1, comprimento=0.01)

    ch1_a2 = Trecho(nome='CH1A2', n1=ch1, n2=a2, condutor=cond_1, comprimento=1.0)
    a2_a1 = Trecho(nome='A2A1', n1=a2, n2=a1, condutor=cond_1, comprimento=1.0)
    a2_a3 = Trecho(nome='A2A3', n1=a2, n2=a3, condutor=cond_1, comprimento=1.0)
    a2_ch3 = Trecho(nome='A2CH3', n1=a2, n2=ch3, condutor=cond_1, comprimento=0.5)
    a3_ch2 = Trecho(nome='A3CH2', n1=a3, n2=ch2, condutor=cond_1, comprimento=0.5)

    ch3_c1 = Trecho(nome='CH3C1', n1=ch3, n2=c1, condutor=cond_1, comprimento=0.5)
    c1_c2 = Trecho(nome='C1C2', n1=c1, n2=c2, condutor=cond_1, comprimento=1.0)
    c1_c3 = Trecho(nome='C1C3', n1=c1, n2=c3, condutor=cond_1, comprimento=1.0)
    c3_ch8 = Trecho(nome='C3CH8', n1=c3, n2=ch8, condutor=cond_1, comprimento=0.5)
    c3_ch5 = Trecho(nome='C3CH5', n1=c3, n2=ch5, condutor=cond_1, comprimento=0.5)

    ch2_b1 = Trecho(nome='CH2B1', n1=ch2, n2=b1, condutor=cond_1, comprimento=0.5)
    b1_b2 = Trecho(nome='B1B2', n1=b1, n2=b2, condutor=cond_1, comprimento=1.0)
    b2_ch4 = Trecho(nome='B2CH4', n1=b2, n2=ch4, condutor=cond_1, comprimento=0.5)
    b2_b3 = Trecho(nome='B2B3', n1=b2, n2=b3, condutor=cond_1, comprimento=1.0)
    b3_ch5 = Trecho(nome='B3CH5', n1=b3, n2=ch5, condutor=cond_1, comprimento=0.5)

    # Trechos do alimentador S2_AL1
    s2_ch6 = Trecho(nome='S2CH6', n1=s2, n2=ch6, condutor=cond_1, comprimento=0.01)

    ch6_d1 = Trecho(nome='CH6D1', n1=ch6, n2=d1, condutor=cond_1, comprimento=1.0)
    d1_d2 = Trecho(nome='D1D2', n1=d1, n2=d2, condutor=cond_1, comprimento=1.0)
    d1_d3 = Trecho(nome='D1D3', n1=d1, n2=d3, condutor=cond_1, comprimento=1.0)
    d1_ch7 = Trecho(nome='D1CH7', n1=d1, n2=ch7, condutor=cond_1, comprimento=0.5)

    ch7_e1 = Trecho(nome='CH7E1', n1=ch7, n2=e1, condutor=cond_1, comprimento=0.5)
    e1_e2 = Trecho(nome='E1E2', n1=e1, n2=e2, condutor=cond_1, comprimento=1.0)
    e2_ch4 = Trecho(nome='E2CH4', n1=e2, n2=ch4, condutor=cond_1, comprimento=0.5)
    e1_e3 = Trecho(nome='E1E3', n1=e1, n2=e3, condutor=cond_1, comprimento=1.0)
    e3_ch8 = Trecho(nome='E3CH8', n1=e3, n2=ch8, condutor=cond_1, comprimento=0.5)

    # Setor S1
    st1 = Setor(nome='S1',
                vizinhos=['A'],
                nos_de_carga=[s1])

    # setor A
    stA = Setor(nome='A',
                vizinhos=['S1', 'B', 'C'],
                nos_de_carga=[a1, a2, a3])

    # Setor B
    stB = Setor(nome='B',
                vizinhos=['A', 'C', 'E'],
                nos_de_carga=[b1, b2, b3])

    # Setor C
    stC = Setor(nome='C',
                vizinhos=['A', 'B', 'E'],
                nos_de_carga=[c1, c2, c3])

    # Setor S2
    st2 = Setor(nome='S2',
                vizinhos=['D'],
                nos_de_carga=[s2])

    # Setor D
    stD = Setor(nome='D',
                vizinhos=['S2', 'E'],
                nos_de_carga=[d1, d2, d3])

    # Setor E
    stE = Setor(nome='E',
                vizinhos=['D', 'B', 'C'],
                nos_de_carga=[e1, e2, e3])

    # ligação das chaves com os respectivos setores
    ch1.n1 = st1
    ch1.n2 = stA

    ch2.n1 = stA
    ch2.n2 = stB

    ch3.n1 = stA
    ch3.n2 = stC

    ch4.n1 = stB
    ch4.n2 = stE

    ch5.n1 = stB
    ch5.n2 = stC

    ch6.n1 = st2
    ch6.n2 = stD

    ch7.n1 = stD
    ch7.n2 = stE

    ch8.n1 = stC
    ch8.n2 = stE

    # Alimentador 1 de S1
    sub_1_al_1 = Alimentador(nome='S1_AL1',
                             setores=[st1, stA, stB, stC],
                             trechos=[s1_ch1, ch1_a2, a2_a1,
                                      a2_a3, a2_ch3, ch3_c1,
                                      c1_c2, c1_c3, c3_ch5,
                                      c3_ch8, a3_ch2, ch2_b1,
                                      b1_b2, b2_ch4, b2_b3,
                                      b3_ch5],
                             chaves=[ch1, ch2, ch3, ch4, ch5, ch8])

    # Alimentador 1 de S2
    sub_2_al_1 = Alimentador(nome='S2_AL1',
                             setores=[st2, stD, stE],
                             trechos=[s2_ch6, ch6_d1, d1_d2,
                                      d1_d3, d1_ch7, ch7_e1,
                                      e1_e2, e2_ch4, e1_e3,
                                      e3_ch8],
                             chaves=[ch6, ch7, ch4, ch8])

    t1 = Transformador(nome='S1_T1',
                       tensao_primario=Fasor(mod=69e3, ang=0.0, tipo=Fasor.Tensao),
                       tensao_secundario=Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao),
                       potencia=Fasor(mod=10e6, ang=0.0, tipo=Fasor.Potencia),
                       impedancia=Fasor(real=0.5, imag=0.2, tipo=Fasor.Impedancia))

    t2 = Transformador(nome='S2_T1',
                       tensao_primario=Fasor(mod=69e3, ang=0.0, tipo=Fasor.Tensao),
                       tensao_secundario=Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao),
                       potencia=Fasor(mod=10e6, ang=0.0, tipo=Fasor.Potencia),
                       impedancia=Fasor(real=0.5, imag=0.2, tipo=Fasor.Impedancia))

    sub_1 = Subestacao(nome='S1', alimentadores=[sub_1_al_1], transformadores=[t1])

    sub_2 = Subestacao(nome='S2', alimentadores=[sub_2_al_1], transformadores=[t2])

    _subestacoes = {sub_1_al_1.nome: sub_1_al_1, sub_2_al_1.nome: sub_2_al_1}

    sub_1_al_1.ordenar(raiz='S1')
    sub_2_al_1.ordenar(raiz='S2')

    sub_1_al_1.gerar_arvore_nos_de_carga()
    sub_2_al_1.gerar_arvore_nos_de_carga()


    # Imprime a representação de todos os setores da subestção
    # na representação
    # nó profundidade
    # print sub1.rnp

    # print sub1.arvore_nos_de_carga.arvore

    # imprime as rnp dos setores de S1
    # for setor in _sub_1.setores.values():
    # print 'setor: ', setor.nome
    # print setor.rnp

    # imprime as rnp dos setores de S2
    # for setor in _sub_2.setores.values():
    # print 'setor: ', setor.nome
    # print setor.rnp

    # _subestacoes['S1'].gera_trechos_da_rede()

    # imprime os trechos da rede S1
    # for trecho in _sub_1.trechos.values():
    #    print trecho
