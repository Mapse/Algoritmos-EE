# coding=utf-8


if __name__ == '__main__':

# chaves do alimentador
ch1 = Chave(nome='1', estado=1)

# Nos de carga do alimentador
# a1 = 632 ; a2 = 633/634 ; a3 = 645 ; a4 = 646
# a5 = 671 ; a6 = 680 ; a7 = 684 ; a8 = 611 
# a9 = 652 ; b1 = 692 ; b2 = 675 ; s1 = 650

s1 = NoDeCarga(nome='650',
			   vizinhos=['632'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_b=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_c=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a1 = NoDeCarga(nome='632',
			   vizinhos=['650','633','645','670'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a2 = NoDeCarga(nome='634',
			   vizinhos=['632'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a3 = NoDeCarga(nome='645',
			   vizinhos=['632'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a4 = NoDeCarga(nome='646',
			   vizinhos=['645'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[]) 
a5 = NoDeCarga(nome='671',
			   vizinhos=['632', '692','680','684'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=['1'])
a6 = NoDeCarga(nome='680',
			   vizinhos=['671'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a7 = NoDeCarga(nome='684',
			   vizinhos=['671','652','611'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a8 = NoDeCarga(nome='611',
			   vizinhos=['684'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
a9 = NoDeCarga(nome='652',
			   vizinhos=['684'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])
b1 = NoDeCarga(nome='692',
			   vizinhos=['671','675'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=['1'])
b2 = NoDeCarga(nome='675',
			   vizinhos=['692'],
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   potencia_fase_a=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
			   chaves=[])

# Condutores aéreos

cond_1 = Condutor(tamanho='1',
				  nome='AA',
			      rp=0.06524,
			      dia_ext=0.0292,
			      raio_m_g=0.0112,
			      ampacidade=698)

cond_2 = Condutor(tamanho='556.5',
				  nome='ACSR',
			      rp=0.1155,
			      dia_ext=0.0235,
			      raio_m_g=0.00954,
			      ampacidade=730)

cond_3 = Condutor(tamanho='500',
				  nome='AA',
			      rp=0.128,
			      dia_ext=0.0206,
			      raio_m_g=0.0079,
			      ampacidade=483)

cond_4 = Condutor(tamanho='336.4'
				  nome='ACSR',
			      rp=0.1901,
			      dia_ext=0.0183,
			      raio_m_g=0.0074,
			      ampacidade=530)

cond_5 = Condutor(tamanho='250'
				  nome='AA',
			      rp=0.2548,
			      dia_ext=0.0144,
			      raio_m_g=0.0052,
			      ampacidade=329)

cond_6 = Condutor(tamanho='#4/0'
				  nome='ACSR',
			      rp=0.368,
			      dia_ext=0.0143,
			      raio_m_g=0.00248,
			      ampacidade=340)

cond_7 = Condutor(tamanho='#2/0'
				  nome='AA',
			      rp=0.4778,
			      dia_ext=0.0105,
			      raio_m_g=0.0038,
			      ampacidade=230)

cond_8 = Condutor(tamanho='#1/0'
				  nome='acsr',
			      rp=0.6959,
			      dia_ext=0.0101,
			      raio_m_g=0.00136,
			      ampacidade=230)

cond_9 = Condutor(tamanho='#1/0'
				  nome='AA',
			      rp=0.6027,
			      dia_ext=0.0093,
			      raio_m_g=0.00338,
			      ampacidade=310)

cond_10 = Condutor(tamanho='#2'
				  nome='AA',
			      rp=0.9569,
			      dia_ext=0.00742,
			      raio_m_g=0.00269,
			      ampacidade=156)

cond_11 = Condutor(tamanho='#2'
				  nome='ACSR',
			      rp=1.050,
			      dia_ext=0.0080,
			      raio_m_g=0.00127,
			      ampacidade=180)

cond_12 = Condutor(tamanho='#4'
				  nome='AA',
			      rp=1.5845,
			      dia_ext=0.00653,
			      raio_m_g=0.00138,
			      ampacidade=140)

cond_13 = Condutor(tamanho='#10'
				  nome='CU',
			      rp=3.668,
			      dia_ext=0.00259,
			      raio_m_g=0.001,
			      ampacidade=80)

cond_14 = Condutor(tamanho='#12'
				  nome='CU',
			      rp=5.8254,
			      dia_ext=0.00206,
			      raio_m_g=0.0007986,
			      ampacidade=75)

cond_15 = Condutor(tamanho='#14'
				  nome='CU',
			      rp=9.241,
			      dia_ext=0.001626,
			      raio_m_g=0.000634,
			      ampacidade=20)

# Condutores subterrâneos

cond_16 = Condutor(tamanho='2(7x)',
				  nome='AA',
			      rp='',
			      d_iso='0.19812',
			      d_tela='0.2159',
			      dia_ext='0.2489',
			      raio_m_g='',
			      ampacidade='135')

cond_17 = Condutor(tamanho='1/0(19x)',
				  nome='AA',
			      rp='',
			      d_iso='0.2159',
			      d_tela='0.23622',
			      dia_ext='0.26924',
			      raio_m_g='',
			      ampacidade='175')

cond_18 = Condutor(tamanho='2/0(19x)',
				  nome='AA',
			      rp='',
			      d_iso='0.2286',
			      d_tela='0.24638',
			      dia_ext='0.2794',
			      raio_m_g='',
			      ampacidade='200')

cond_19 = Condutor(tamanho='250(37x)',
				  nome='AA',
			      rp='',
			      d_iso='0.26924',
			      d_tela='0.2946',
			      dia_ext='0.32766',
			      raio_m_g='',
			      ampacidade='260')

cond_20 = Condutor(tamanho='500(37x)',
				  nome='AA',
			      rp='',
			      d_iso='0.32766',
			      d_tela='0.35306',
			      dia_ext='0.39624',
			      raio_m_g='',
			      ampacidade='385')

cond_21 = Condutor(tamanho='1000(61x)',
				  nome='AA',
			      rp='',
			      d_iso='0.41656',
			      d_tela='0.44958',
			      dia_ext='0.50292',
			      raio_m_g='',
			      ampacidade='550')










# a1 = 632 ; a2 = 633/634 ; a3 = 645 ; a4 = 646
# a5 = 671 ; a6 = 680 ; a7 = 684 ; a8 = 611 
# a9 = 652 ; b1 = 692 ; b2 = 675 ; s1 = 650

# 1 polegada = 0,0254 m
# 1 milhas = 1,60934 m
# 1 pé = 0,3048 m