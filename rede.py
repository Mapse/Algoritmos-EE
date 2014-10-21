# coding=utf-8

from rnp import Arvore, Aresta


class Setor(Arvore):
    def __init__(self, nome, vizinhos, nos_de_carga):
        assert isinstance(nome, str), 'O parâmetro nome da classe' \
                                      'Setor deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Setor deve ser do tipo list'
        assert isinstance(nos_de_carga, dict), 'O parâmetro nos_de_carga da classe' \
                                               'Setor deve ser do tipo dict'
        self.nome = nome
        self.nos_de_carga = nos_de_carga
        self.vizinhos = vizinhos
        self.id = None
        self.arvore_do_setor = self._gera_arvore_do_setor()

        super(Setor, self).__init__(self.arvore_do_setor, str)

    def _gera_arvore_do_setor(self):
        arvore_do_setor = dict()
        for i, j in self.nos_de_carga.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            arvore_do_setor[i] = j.vizinhos

        return arvore_do_setor

    def __str__(self):
        return 'Setor: ' + self.nome


class NoDeCarga(object):
    def __init__(self, nome, vizinhos, potencia):
        assert isinstance(nome, str), 'O parâmetro nome da classe NoDeCarga' \
                                      ' deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Barra deve ser do tipo string'
        assert isinstance(potencia, complex), 'O parâmetro potência da classe' \
                                              'NoDeCarga deve ser do tipo string'
        self.nome = nome
        self.potencia = potencia
        self.vizinhos = vizinhos
        self.id = None

    def __str__(self):
        return 'No de Carga: ' + self.nome


class Alimentador(Arvore):
    def __init__(self):
        pass


class Subestacao(Arvore):
    def __init__(self, nome, setores, chaves):
        assert isinstance(nome, str), 'O parâmetro nome da classe Subestação' \
                                      'deve ser do tipo string'
        assert isinstance(setores, dict), 'O parâmetro setores da classe' \
                                          'Subestacao deve ser do tipo dict'
        assert isinstance(chaves, dict), 'O parâmetro chaves da classe' \
                                         'Subestacao deve ser do tipo dict'
        self.nome = nome
        for i, j in setores.iteritems():
            for k in j.nos_de_carga.values():
                if self.nome in k.vizinhos:
                    setor_subestacao = Setor(nome=self.nome,
                                             vizinhos=[j.nome],
                                             nos_de_carga=dict())
                    setores[self.nome] = setor_subestacao
                    break
            else:
                continue
            break

        self.setores = setores
        self.chaves = chaves
        self.arvore_da_rede = self._gera_arvore_da_rede()

        super(Subestacao, self).__init__(self.arvore_da_rede, str)

    def _gera_arvore_da_rede(self):
        arvore_da_rede = dict()
        for i, j in self.setores.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            arvore_da_rede[i] = j.vizinhos

        return arvore_da_rede


class Chave(Aresta):
    def __init__(self, nome, estado=1):
        assert estado == 1 or estado == 0, 'O parâmetro estado deve ser um inteiro de valor 1 ou 0'
        super(Chave, self).__init__(nome)
        self.estado = estado


if __name__ == '__main__':
    print 'Teste...'

    _chaves = dict()

    # chaves do alimentador de SE1
    _chaves['1'] = Chave(nome='1', estado=1)
    _chaves['2'] = Chave(nome='2', estado=1)
    _chaves['3'] = Chave(nome='3', estado=1)

    # chaves de Fronteira
    _chaves['4'] = Chave(nome='4', estado=0)
    _chaves['5'] = Chave(nome='5', estado=0)
    _chaves['8'] = Chave(nome='8', estado=0)

    # chaves do alimentador de SE2
    _chaves['6'] = Chave(nome='6', estado=1)
    _chaves['7'] = Chave(nome='7', estado=1)

    _setores_1 = dict()

    # nos de carga do setor A
    nos = dict()
    nos['A1'] = NoDeCarga(nome='A1', vizinhos=['A2'], potencia=160 + 120j)
    nos['A2'] = NoDeCarga(nome='A2', vizinhos=['A1', 'A3'], potencia=150 + 110j)
    nos['A3'] = NoDeCarga(nome='A3', vizinhos=['A2'], potencia=100 + 80j)

    _setores_1['A'] = Setor(nome='A', vizinhos=['B', 'C'], nos_de_carga=nos)

    # nos de carga do Setor B
    nos = dict()
    nos['B1'] = NoDeCarga(nome='B1', vizinhos=['B2'], potencia=200 + 140j)
    nos['B2'] = NoDeCarga(nome='B2', vizinhos=['B1', 'B2'], potencia=150 + 110j)
    nos['B3'] = NoDeCarga(nome='B3', vizinhos=['B2'], potencia=100 + 80j)

    _setores_1['B'] = Setor(nome='B', vizinhos=['A'], nos_de_carga=nos)

    # nos de carga do Setor C
    nos = dict()
    nos['C1'] = NoDeCarga(nome='C1', vizinhos=['C2', 'C3'], potencia=200 + 140j)
    nos['C2'] = NoDeCarga(nome='C2', vizinhos=['C1'], potencia=150 + 110j)
    nos['C3'] = NoDeCarga(nome='C3', vizinhos=['C1'], potencia=100 + 80j)

    _setores_1['C'] = Setor(nome='C', vizinhos=['A'], nos_de_carga=nos)

    _setores_2 = dict()

    # nos de carga do Setor D
    nos = dict()
    nos['D1'] = NoDeCarga(nome='D1', vizinhos=['D2', 'D3'], potencia=200 + 160j)
    nos['D2'] = NoDeCarga(nome='D2', vizinhos=['D1'], potencia=90 + 40j)
    nos['D3'] = NoDeCarga(nome='D3', vizinhos=['D1'], potencia=100 + 80j)

    _setores_2['D'] = Setor(nome='D', vizinhos=['E'], nos_de_carga=nos)

    # nos de carga do Setor E
    nos = dict()
    nos['E1'] = NoDeCarga(nome='E1', vizinhos=['E3', 'E2'], potencia=100 + 40j)
    nos['E2'] = NoDeCarga(nome='E2', vizinhos=['E1'], potencia=110 + 70j)
    nos['E3'] = NoDeCarga(nome='E3', vizinhos=['E1'], potencia=150 + 80j)

    _setores_2['E'] = Setor(nome='E', vizinhos=['D'], nos_de_carga=nos)

    _chaves['1'].n1 = _setores_1['A']

    _chaves['2'].n1 = _setores_1['A']
    _chaves['2'].n2 = _setores_1['B']

    _chaves['3'].n1 = _setores_1['A']
    _chaves['3'].n2 = _setores_1['C']

    _chaves['4'].n1 = _setores_1['B']
    _chaves['4'].n2 = _setores_2['E']

    _chaves['5'].n1 = _setores_1['B']
    _chaves['5'].n2 = _setores_1['C']

    _chaves['6'].n1 = _setores_2['D']

    _chaves['7'].n1 = _setores_2['D']
    _chaves['7'].n2 = _setores_2['E']

    _chaves['8'].n1 = _setores_1['C']
    _chaves['8'].n2 = _setores_2['E']

    sub1 = Subestacao(nome='SE1', setores=_setores_1, chaves=_chaves)
    #sub2 = Subestacao(nome='SE2', setores=_setores_2, chaves=_chaves)
    print sub1.arvore_da_rede

    for i, j in sub1.setores.iteritems():
        print j, j.arvore_do_setor
        if i == 'A':
            j.ordena(raiz='A2')
            print j.rnp
        elif i == 'C':
            j.ordena(raiz='C1')
            print j.rnp

    sub1.ordena(raiz='A')
    print sub1.rnp