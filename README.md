# Trabalho-de-Conclusao-de-Curso

Trabalho realizado como requisito para conclusão do curso de Ciência da Computação

Linguagem utilizada para desenvolvimento: Python 3.8

# Non Dominated Sorting Genetic algorithm II (NSGA-II)

Existe inicialmente uma população Pt, que contém indivíduos com genes aleatórios, podem existir indivíduos melhores que
outros

A partir dessa população Pt, são criadas diversas proles, chamadas Qt, que são resultado de um mix de genes dos melhores 
indivíduos de Pt

A população com todos os indivíduos de Pt e Qt é chamada de Rt

Cada indivíduo possui um rank, que mostra o quão bom aquele indivíduo é, a partir disso os melhores são selecionados,
até que o tamanho da população seja igual ao da população original Pt, formando assim a população Pt+1

NON-DOMINATED SORTING

Cada indivíduo é comparado com todos os outros, e para esse indivíduo é criada um contador de indivíduos que ele
é dominado e uma lista de quais indivíduos ele domina

Para formar a primeira fronteira, basta selecionar todos os indivíduos que tem o seu contador igual a zero

Para formar a segunda fronteira, são percorridos todos os indivíduos da fronteira 1, mais especificamente as listas
desses indivíduos. Cada elemento que estiver nessa lista, terá seu contador diminuido em -1, e os integrantes da segunda
fronteira são aqueles que conseguirem ter seu contador igual a 0. Esse processo é repetido até que cada indivíduo 
pertença a uma fronteira
