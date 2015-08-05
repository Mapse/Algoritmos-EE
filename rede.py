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

        potencia = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        for no in self.nos_de_carga.values():
            potencia = potencia + no.potencia

        return potencia

    def __str__(self):
        return 'Setor: ' + self.nome


class NoDeCarga(object):
    def __init__(self,
                 nome,
                 vizinhos,
                 potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 tensao=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 chaves=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe NoDeCarga' \
                                      ' deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Barra deve ser do tipo string'

        self.nome = nome
        self.vizinhos = vizinhos
        self.potencia = potencia
        self.potencia_eq = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.tensao = tensao
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
                 potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 tensao=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 chaves=None):

        self.nome = nome
        self.vizinhos = vizinhos
        self.potencia = potencia
        self.dvtol = dvtol
        self.potencia_eq = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.tensao = tensao
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

        #calcula a impedancia do caminho entre subestação e o ponto de encontro
        for i in range(profundidadec1):
            z1 = self._busca_trecho(self.alimentadores[alimentador],inicial,c1[1][i+1])
            if type(z1) == list:
                for j in z1:
                    trechoscomuns.append(j)
                    impedanciasub_positiva = impedanciasub_positiva + j.impedancia_equivalente_positiva
                    impedanciasub_zero = impedanciasub_zero + j.impedancia_equivalente_zero
            else:
                    trechoscomuns.append(z1)
                    impedanciasub_positiva = impedanciasub_positiva + z1.impedancia_equivalente_positiva
                    impedanciasub_zero = impedanciasub_zero + z1.impedancia_equivalente_zero

            inicial = c1[1][i+1]
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

        #calcula a impedancia do caminho o ponto de encontro e o ponto de curto
        for i in range(profundidadec1+1,len(c1[0])):
            z2 = self._busca_trecho(self.alimentadores[alimentador],inicial,c1[1][i])
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

        #calcula a impedancia do caminho o ponto de encontro e o gerador
        for i in range(profundidadec1+1,len(c2[0])):
            z3 = self._busca_trecho(self.alimentadores[alimentador],inicial,c2[1][i])
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

        #calcula a impedância da associação serie ou paralelo
        if (impedanciagerador_positiva or impedanciagerador_zero) != 0 and (impedanciasub_positiva or impedanciasub_zero) != 0:
            zparalelo_positiva = impedanciasub_positiva*impedanciagerador_positiva/(impedanciagerador_positiva+impedanciasub_positiva)
            zparalelo_zero = impedanciasub_zero*impedanciagerador_zero/(impedanciasub_zero+impedanciagerador_zero)

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

        #calcula o valor da corrente de curto no caminho ponto_de_encontro-curto
        curto1 = (3.0) * self.base_sub.corrente / (2 * ztotal_positiva + ztotal_zero)
        correntecc1 = Fasor(real=curto1.real, imag=curto1.imag, tipo=Fasor.Corrente)
        correntecc1.base = self.base_sub
        print 'curto monofasico em ponto comum-ponto de curto - ', correntecc1.mod
        curto1g = np.abs(impedanciasub_positiva / (impedanciagerador_positiva + impedanciasub_positiva))*2*correntecc1.mod/3+\
        np.abs(impedanciasub_zero / (impedanciagerador_zero + impedanciasub_zero)) * correntecc1.mod/3
        print 'curto monofasico em gerador-ponto comum - ', curto1g
        curto1s = np.abs(impedanciagerador_positiva / (impedanciagerador_positiva + impedanciasub_positiva))*2*correntecc1.mod/3+\
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
                no.tensao = Fasor(real=tensao.real,
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
                no.potencia_eq.real = 0.0
                no.potencia_eq.imag = 0.0

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
                    no.potencia_eq.real += no.potencia.real
                    no.potencia_eq.imag += no.potencia.imag
                else:
                    # soma a potencia da carga associada ao nó atual
                    no.potencia_eq.real += no.potencia.real
                    no.potencia_eq.imag += no.potencia.imag

                    # acrescenta à potência do nó atual
                    # as potências dos nós a jusante
                    for no_jus in vizinhos_jusante:
                        no.potencia_eq.real += no_jus.potencia_eq.real
                        no.potencia_eq.imag += no_jus.potencia_eq.imag

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
                        no.potencia_eq.real += r * (no_jus.potencia_eq.mod ** 2) / \
                            no_jus.tensao.mod ** 2
                        no.potencia_eq.imag += x * (no_jus.potencia_eq.mod ** 2) / \
                            no_jus.tensao.mod ** 2

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

                v_mon = no_mon.tensao.mod

                p = no.potencia_eq.real
                q = no.potencia_eq.imag

                # parcela de perdas
                p += r * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2
                q += x * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2

                v_jus = v_mon ** 2 - 2 * (r * p + x * q) + \
                    (r ** 2 + x ** 2) * (p ** 2 + q ** 2) / v_mon ** 2
                v_jus = np.sqrt(v_jus)

                k1 = (p * x - q * r) / v_mon
                k2 = v_mon - (p * r - q * x) / v_mon

                ang = no_mon.tensao.ang * np.pi / 180.0 - np.arctan(k1 / k2)

                no.tensao.mod = v_jus
                no.tensao.ang = ang * 180.0 / np.pi

                # print 'Tensao do no {nome}: {tens}'.format(nome=no.nome, tens=no.tensao.mod/1e3)

                # calcula o fluxo de corrente passante no trecho
                corrente = no.tensao.real - no_mon.tensao.real
                corrente += (no.tensao.imag - no_mon.tensao.imag) * 1.0j
                corrente /= (r + x * 1.0j)
                # se houver chaves, ou seja, há dois trechos a mesma corrente
                # é atribuida
                if not isinstance(trecho, Trecho):
                    trecho[0].fluxo = Fasor(real=corrente.real,
                                            imag=corrente.imag,
                                            tipo=Fasor.Corrente)
                    trecho[1].fluxo = Fasor(real=corrente.real,
                                            imag=corrente.imag,
                                            tipo=Fasor.Corrente)
                else:
                    trecho.fluxo = Fasor(real=corrente.real,
                                         imag=corrente.imag,
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
                nos.potencia.real = (-1) * nos.potencia.real
                nos.potencia.imag = (-1) * nos.potencia.imag

    def tensaogerador(self, alimentador):
        """ Funcao que retorna uma lista com os geradores que nao convergiram,
        a quantidade de geradores e a matriz
            com as diferenças de tennsoes de cada gerador """

        count = 0
        diftensao = list()
        listager = list()
        # percorre nos do sistema
        for nos in alimentador.nos_de_carga.values():
            # identifica os geradores do sistema
            if isinstance(nos, Gerador):
                # trata apenas geradores modelados como PV
                if nos.modelofluxo == 'PV':
                    # calcula a diferença entre a tensão calculada com o fluxo
                    # de carga e a tensao do gerador
                    deltav = np.array([[nos.tensaogerador - float(nos.tensao.mod)]])
                    # se a diferença de tensao for maior do que a tolerancia o gerador será guardado
                    if abs(deltav) > nos.dvtol:
                        # guarda as diferenças de tensões dos geradores não convergidos na lista
                        diftensao.append(deltav)
                        # guarda o objeto gerador
                        listager.append(nos)
                        # incremento que define a quantidade geradores não convergidos
                        count += 1
        # cria um array para auxiliar na formação da matriz das diferenças de tensões
        aux = np.array([[]])
        # caso diftensao seja diferente de vazio, ou seja, existe gerador que não convergiu
        # forma-se a matriz das diferenças de tensões
        if diftensao != []:
            # concatena a primeira diferença de tensão com o array auxiliar
            dif = np.concatenate((diftensao[0], aux), axis=1)
            # remove o primeiro elemento deixando apenas o array vazio
            diftensao.pop(0)
            # adiciona todos os elementos à matriz de diferença de tensões, incluindo o elemento removido
            for i in diftensao:  # for que percorre a lista de array para realizar o restante da concatenação
                dif = np.concatenate((dif, i))
            diftensao = dif

        print diftensao
        return listager, count, diftensao  # retorna a lista com os geradores a quantidade de geradores e a matriz coluna da diferença de tensões

    def matrix_reatancia(self, alimentador):
        """funcao... """
        listageradores, numgeradores, dVgeradores = self.tensaogerador(alimentador)
        listageradores2 = self.tensaogerador(alimentador)[0]
        listageradores3 = self.tensaogerador(alimentador)[0]
        x = np.zeros((numgeradores, numgeradores))
        aux = []
        rem = []
        for i in listageradores2:
            for j in listageradores3:
                if i.nome == j.nome:
                    pass
                else:
                    if j.nome in rem:
                        pass
                    else:
                        aux.append(self.xij(alimentador, i.nome, j.nome))
                        rem.append(i.nome)
        for i in range(np.shape(x)[0]):
            for j in range(np.shape(x)[1]):
                if i == j:
                    for no in listageradores:
                        x[i, j] = self.xii(alimentador, no.nome)
                        listageradores.remove(no)
                        break
                elif j > i:
                    for reat in aux:
                        if x[i, j] == 0:
                            x[i, j] = reat
                            x[j, i] = reat
                            aux.remove(reat)
                            break
                        else:
                            pass
        return x

    def reativo(self, alimentador):
        dq = np.dot(linalg.inv(self.matrix_reatancia(alimentador)), self.tensaogerador(alimentador)[2])
        for dv, pot, ger in zip(self.tensaogerador(alimentador)[2], dq, self.tensaogerador(alimentador)[0]):
            if dv > 0:
                ger.potencia.imag = ger.potencia.imag - 50 * pot[0]
            elif dv < 0:
                ger.potencia.imag = ger.potencia.imag + 50 * pot[0]

            if abs(ger.potencia.imag) > abs(ger.qmax):
                ger.potencia.imag = -ger.qmax
            elif abs(ger.potencia.imag) < abs(ger.qmin):
                ger.potencia.imag = -ger.qmin

    def xii(self, alimentador, no_):

        trechos = alimentador.trechos.values()  # variável que guarda os techos do alimentador
        caminho = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_)[1]  # variável que guarda o caminho do nó até o nó raiz
        caminho = list(caminho)  # faz uma lista do array caminho
        caminho_2 = list(caminho)  # faz uma lista em outra variável auxiliar
        tr = []  # lista que servirá para guardar os trechos
        reat = 0
        # for para a obtenção das variáveis nodecarga e gerador

        for no in caminho:  # for que percorre o caminho
            for trecho in trechos:  # for que percorre os trechos

                if trecho.n1.nome == no:  # se o n1 do trecho for igual ao nó atual

                    if type(trecho.n2) == NoDeCarga or type(trecho.n2) == Gerador:  # se o tipo for gerador verifica se o n2 ta no caminho e se o n2 nao é o próprio nó
                        if trecho.n2.nome in caminho_2 and trecho.n2.nome != no:
                            reat += (trecho.comprimento * trecho.condutor.xp)
                            tr.append(trecho)
                    else:
                        no_1 = alimentador.nos_de_carga[no]

                        try:
                            no_2 = alimentador.nos_de_carga[caminho_2[1]]  # pega o próximo nó da iteração
                        except IndexError:  # como se está removendo os nós o indice irá variar
                            continue        # para tanto, se houver erro de indice ele continua

                        set_1 = set(no_1.chaves)  # cria um conjunto com as chaves do nó atual
                        set_2 = set(no_2.chaves)  # cria um conjunto com as chaves do nó da próxima interação
                                                  # quando for s1 ele assume o que????
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

        caminho_1 = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_1)
        caminho_2 = alimentador.arvore_nos_de_carga.caminho_no_para_raiz(no_2)

        max_prof = 0
        no_max = None

        for i, ix in zip(caminho_1[1, :], caminho_1[0, :]):
            for j, jx in zip(caminho_2[1, :], caminho_2[0, :]):
                if i == j:
                    if int(ix) > max_prof:
                        max_prof = int(ix)
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
        converg_nos = dict()
        for no in alimentador.nos_de_carga.values():
            converg_nos[no.nome] = 1e6
        # testa se o máximo de iterações foi alcançada e a convergência
        while iter <= max_iteracaoes and converg > criterio_converg:
            iter += 1
            #print '-------------------------'
            #print 'Iteração: {iter}'.format(iter=iter)
            # dicionário que guarda as o nome dos nós na chave a suas tensões nos valores
            tensao_nos = dict()
            for no in alimentador.nos_de_carga.values():
                tensao_nos[no.nome] = Fasor(real=no.tensao.real,
                                            imag=no.tensao.imag,
                                            tipo=Fasor.Tensao)
            # varre o alimentador calculado as potências e as tensões
            self._varrer_alimentador(alimentador)
            # faz a diferença entre os valores de tensões passados e valores de
            # tensões atuais para verificar a convergência
            for no in alimentador.nos_de_carga.values():
                converg_nos[no.nome] = abs(tensao_nos[no.nome].mod -
                                           no.tensao.mod)
            # toma o valor máximo de diferença de tensão para todos os nós da rede
            converg = max(converg_nos.values())
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
                max_iteracoes = 10000
                iter = 0

                while True:
                    # armazena lista com os geradores, a quantidade deles e a
                    # matriz  com a diferença de tensão em cada um
                    listager, count, diftensao = self.tensaogerador(alimentador)
                    iter += 1
                    if iter >= max_iteracoes or listager == []:
                        if iter >= max_iteracoes:
                            print 'Numero maximo de iteracoes atingidas'
                        elif listager == []:
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
                 fluxo=None,
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

        if fluxo is None:
            self.fluxo = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)
        else:
            self.fluxo = fluxo

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
                   potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['1'])
    a1 = NoDeCarga(nome='A1',
                   vizinhos=['A2'],
                   potencia=Fasor(real=460.0e3, imag=250.0e3, tipo=Fasor.Potencia))
    a2 = NoDeCarga(nome='A2',
                   vizinhos=['S1', 'A1', 'A3', 'C1'],
                   potencia=Fasor(real=350.0e3, imag=220.0e3, tipo=Fasor.Potencia),
                   chaves=['1', '3'])
    a3 = NoDeCarga(nome='A3',
                   vizinhos=['A2', 'B1'],
                   potencia=Fasor(real=500.0e3, imag=280.0e3, tipo=Fasor.Potencia),
                   chaves=['2'])
    b1 = Gerador(nome='B1',
                 vizinhos=['B2', 'A3'],
                 dvtol=1,
                 potencia=Fasor(real=110e3, imag=80e3, tipo=Fasor.Potencia),
                 chaves=['2'],
                 tensao=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tipogerador='AEROGERADOR',
                 maquina='DFIG',
                 modelofluxo='PV',
                 qmin=30e3,
                 qmax=650e3,
                 tensaogerador=13800)
    b2 = NoDeCarga(nome='B2',
                   vizinhos=['B1', 'B3', 'E2'],
                   potencia=Fasor(real=450.0e3, imag=230.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    b3 = NoDeCarga(nome='B3',
                   vizinhos=['B2', 'C3'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['5'])
    c1 = Gerador(nome='C1',
                 vizinhos=['C2', 'C3', 'A2'],
                 dvtol=1,
                 potencia=Fasor(real=90e3, imag=55e3, tipo=Fasor.Potencia),
                 chaves=['3'],
                 tensao=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 tipogerador='FOTOVOLTAICO',
                 maquina='',
                 modelofluxo='PV',
                 qmin=20e3,
                 qmax=650e3,
                 tensaogerador=13800)
    c2 = NoDeCarga(nome='C2',
                   vizinhos=['C1'],
                   potencia=Fasor(real=650.0e3, imag=330.0e3, tipo=Fasor.Potencia))
    c3 = NoDeCarga(nome='C3',
                   vizinhos=['C1', 'E3', 'B3'],
                   potencia=Fasor(real=300.0e3, imag=180.0e3, tipo=Fasor.Potencia),
                   chaves=['5', '8'])

    # Nos de carga do alimentador S2_AL1
    s2 = NoDeCarga(nome='S2',
                   vizinhos=['D1'],
                   potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['6'])
    d1 = NoDeCarga(nome='D1',
                   vizinhos=['S2', 'D2', 'D3', 'E1'],
                   potencia=Fasor(real=200.0e3, imag=160.0e3, tipo=Fasor.Potencia),
                   chaves=['6', '7'])
    d2 = NoDeCarga(nome='D2',
                   vizinhos=['D1'],
                   potencia=Fasor(real=90.0e3, imag=40.0e3, tipo=Fasor.Potencia))
    d3 = NoDeCarga(nome='D3',
                   vizinhos=['D1'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia))
    e1 = NoDeCarga(nome='E1',
                   vizinhos=['E3', 'E2', 'D1'],
                   potencia=Fasor(real=100.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   chaves=['7'])
    e2 = NoDeCarga(nome='E2',
                   vizinhos=['E1', 'B2'],
                   potencia=Fasor(real=110.0e3, imag=70.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    e3 = NoDeCarga(nome='E3',
                   vizinhos=['E1', 'C3'],
                   potencia=Fasor(real=150.0e3, imag=80.0e3, tipo=Fasor.Potencia),
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
