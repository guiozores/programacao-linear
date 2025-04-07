import numpy as np
from scipy.optimize import linprog
from tabulate import tabulate  # Será usado para formatar tabelas

def obter_dados_usuario():
    """Função para obter os dados do problema de programação linear do usuário."""
    try:
        # Número de variáveis de decisão
        num_vars = int(input("Informe o número de variáveis de decisão: "))
        
        # Função objetivo
        print("\nInforme os coeficientes da função objetivo (maximização):")
        coefs_obj = []
        for i in range(num_vars):
            coef = float(input(f"Coeficiente para x{i+1}: "))
            coefs_obj.append(-coef)  # Negativo para maximização
        
        # Número de restrições
        num_restricoes = int(input("\nInforme o número de restrições: "))
        
        # Matriz de coeficientes das restrições
        matriz_A = []
        vetor_b = []
        
        print("\nInforme os coeficientes das restrições:")
        for i in range(num_restricoes):
            linha = []
            for j in range(num_vars):
                coef = float(input(f"Restrição {i+1}, coeficiente para x{j+1}: "))
                linha.append(coef)
            matriz_A.append(linha)
            
            # Valor do lado direito da restrição
            valor_b = float(input(f"Valor máximo para restrição {i+1}: "))
            vetor_b.append(valor_b)
            
        return coefs_obj, matriz_A, vetor_b
    except ValueError:
        print("Erro: Por favor, insira valores numéricos válidos.")
        return obter_dados_usuario()

def exibir_problema_completo(c, A, b):
    """Exibe todas as funções e restrições do problema para verificação."""
    print("\n===== PROBLEMA DE PROGRAMAÇÃO LINEAR =====")
    print("Função Objetivo:")
    coefs_positivos = [-coef for coef in c]
    termos_z = []
    for i, coef in enumerate(coefs_positivos):
        if coef != 0:
            termos_z.append(f"{coef:.0f}x{i+1}")
    funcao_z = " + ".join(termos_z)
    print(f"Z = {funcao_z}")
    
    print("\nRestrições:")
    for i, (restricao, rhs) in enumerate(zip(A, b)):
        termos = []
        for j, coef in enumerate(restricao):
            if coef != 0:
                termos.append(f"{coef:.0f}x{j+1}")
        eq_restricao = " + ".join(termos)
        print(f"R{i+1}: {eq_restricao} ≤ {rhs:.0f}")
    
    print("\nNão-negatividade:")
    vars_x = [f"x{i+1}" for i in range(len(c))]
    print(", ".join(vars_x) + " ≥ 0")

class SimplexTabulado:
    def __init__(self, c, A, b):
        """
        Inicializa o problema de programação linear.
        
        Args:
            c: coeficientes da função objetivo (negativos para maximização)
            A: matriz de coeficientes das restrições
            b: vetor de limites das restrições
        """
        self.c_original = [-coef for coef in c]  # Converter de volta para positivo
        self.c = c.copy()
        self.A = [row.copy() for row in A]
        self.b = b.copy()
        self.num_vars = len(c)
        self.num_restricoes = len(b)
        
        # Preparar tabela inicial do simplex
        self.preparar_tabela_inicial()
        
    def preparar_tabela_inicial(self):
        """Prepara a tabela inicial do simplex."""
        # Criar tabela com variáveis de folga
        self.num_total_vars = self.num_vars + self.num_restricoes
        self.tabela = np.zeros((self.num_restricoes + 1, self.num_total_vars + 1))
        
        # Preencher as restrições
        for i in range(self.num_restricoes):
            for j in range(self.num_vars):
                self.tabela[i, j] = self.A[i][j]
            
            # Adicionar variáveis de folga (matriz identidade)
            self.tabela[i, self.num_vars + i] = 1.0
            
            # Adicionar lado direito das restrições
            self.tabela[i, -1] = self.b[i]
        
        # Preencher função objetivo (última linha)
        for j in range(self.num_vars):
            self.tabela[-1, j] = self.c[j]
        
        # Inicializar base (variáveis básicas) - começa com as variáveis de folga
        self.base = [self.num_vars + i for i in range(self.num_restricoes)]
        
    def exibir_tabela(self, iteracao=None, col_pivo=None, row_pivo=None):
        """Exibe a tabela atual do simplex."""
        if iteracao is not None:
            print(f"\n===== Iteração {iteracao} =====")
        else:
            print("\n===== Tabela Inicial =====")
        
        # Criar cabeçalhos para as colunas
        colunas = ["Z"] + [f'X{i+1}' for i in range(self.num_vars)] + \
                  [f'F{i+1}' for i in range(self.num_restricoes)] + \
                  ['Constante']
                  
        # Adicionar cabeçalho extra para divisão quando mostrando pivô
        headers = ["Variaveis", "N de linha"] + colunas
        if col_pivo is not None:
            headers.append("Divisão")
            
        tabela_dados = []
        
        # Adicionar linha Z (função objetivo)
        row_z = ["Z", "1", "1"] + \
                [f"{self.tabela[-1, j]:.2f}" for j in range(self.num_vars + self.num_restricoes)] + \
                [f"{self.tabela[-1, -1]:.2f}"]
        tabela_dados.append(row_z)
        
        # Adicionar linhas das restrições
        for i in range(self.num_restricoes):
            # Variável básica para esta linha
            vb_idx = self.base[i]
            if vb_idx < self.num_vars:
                vb = f'X{vb_idx+1}'
            else:
                vb = f'F{vb_idx-self.num_vars+1}'
            
            row_data = [vb, f"{i+2}", "0"] + \
                      [f"{self.tabela[i, j]:.2f}" for j in range(self.num_total_vars)] + \
                      [f"{self.tabela[i, -1]:.2f}"]
                      
            # Adicionar coluna de divisão se estivermos mostrando um pivô
            if col_pivo is not None:
                if self.tabela[i, col_pivo] > 0:
                    ratio = self.tabela[i, -1] / self.tabela[i, col_pivo]
                    row_data.append(f"{ratio:.2f}")
                else:
                    row_data.append("--")
                    
            tabela_dados.append(row_data)
        
        # Exibir a tabela formatada com um header duplo
        print(tabulate(tabela_dados, headers=headers, tablefmt="grid", stralign="center"))
        
        # Se tivermos elementos pivô, exibi-los
        if col_pivo is not None and row_pivo is not None:
            print(f"\nElemento pivô: ({row_pivo+1}, {col_pivo+1}) = {self.tabela[row_pivo, col_pivo]:.2f}")
            if col_pivo < self.num_vars:
                var_entrada = f"X{col_pivo+1}"
            else:
                var_entrada = f"F{col_pivo-self.num_vars+1}"
                
            if self.base[row_pivo] < self.num_vars:
                var_saida = f"X{self.base[row_pivo]+1}"
            else:
                var_saida = f"F{self.base[row_pivo]-self.num_vars+1}"
                
            print(f"Variável que entra na base: {var_entrada}")
            print(f"Variável que sai da base: {var_saida}")
        
    def encontrar_coluna_pivo(self):
        """Encontra a coluna do elemento pivô (variável de entrada)."""
        # O menor coeficiente negativo na linha Z indica a variável de entrada
        min_val = 0
        min_col = -1
        for j in range(self.num_total_vars):
            if self.tabela[-1, j] < min_val:
                min_val = self.tabela[-1, j]
                min_col = j
        
        return min_col
    
    def encontrar_linha_pivo(self, col_pivo):
        """Encontra a linha do elemento pivô (variável de saída)."""
        # Regra da razão mínima: encontra a linha com a menor razão positiva
        min_ratio = float('inf')
        min_row = -1
        
        for i in range(self.num_restricoes):
            if self.tabela[i, col_pivo] > 0:
                ratio = self.tabela[i, -1] / self.tabela[i, col_pivo]
                if ratio < min_ratio:
                    min_ratio = ratio
                    min_row = i
        
        return min_row
    
    def pivotar(self, row_pivo, col_pivo):
        """Realiza a operação de pivotamento."""
        print("\n===== Operação de Pivotamento =====")
        
        # Normalizar a linha do pivô
        elemento_pivo = self.tabela[row_pivo, col_pivo]
        print(f"1. Normalizar linha {row_pivo+1} dividindo por {elemento_pivo:.2f}")
        
        self.tabela[row_pivo] = self.tabela[row_pivo] / elemento_pivo
        
        # Exibir linha normalizada
        print(f"Linha {row_pivo+1} normalizada: {', '.join([f'{val:.2f}' for val in self.tabela[row_pivo]])}")
        
        # Atualizar as outras linhas
        print("\n2. Eliminar a variável das outras linhas:")
        
        for i in range(self.num_restricoes + 1):
            if i != row_pivo:
                fator = self.tabela[i, col_pivo]
                if fator != 0:
                    print(f"   Linha {i+1}: Subtrair {fator:.2f} vezes a linha {row_pivo+1}")
                    self.tabela[i] = self.tabela[i] - fator * self.tabela[row_pivo]
        
        # Atualizar a base
        self.base[row_pivo] = col_pivo
    
    def resolver(self):
        """Resolve o problema usando o método simplex."""
        iteracao = 0
        self.exibir_tabela()
        
        while True:
            # Encontrar variável de entrada (coluna do pivô)
            col_pivo = self.encontrar_coluna_pivo()
            
            # Verificar condição de otimalidade
            if col_pivo == -1:
                print("\n===== Solução Ótima Encontrada =====")
                break
            
            # Encontrar variável de saída (linha do pivô)
            row_pivo = self.encontrar_linha_pivo(col_pivo)
            
            # Verificar se o problema é ilimitado
            if row_pivo == -1:
                print("\nO problema é ilimitado! Não há solução ótima finita.")
                return
            
            # Exibir informações sobre o pivô
            self.exibir_tabela(iteracao+1, col_pivo, row_pivo)
            
            # Realizar operação de pivotamento
            self.pivotar(row_pivo, col_pivo)
            
            # Incrementar iteração e exibir a tabela resultante
            iteracao += 1
            print(f"\nTabela após pivotamento (Iteração {iteracao}):")
            self.exibir_tabela()
        
        # Extrair e exibir a solução
        self.mostrar_solucao()
    
    def mostrar_solucao(self):
        """Exibe a solução final."""
        # Valor ótimo (negativo da célula z na coluna RHS para maximização)
        z_otimo = -self.tabela[-1, -1]
        
        # Valores das variáveis de decisão
        valores_x = [0] * self.num_vars
        
        for i, var_base in enumerate(self.base):
            if var_base < self.num_vars:
                valores_x[var_base] = self.tabela[i, -1]
        
        # Valores das variáveis de folga
        valores_folga = []
        for i in range(self.num_restricoes):
            idx = self.num_vars + i
            if idx in self.base:
                pos = self.base.index(idx)
                valores_folga.append(self.tabela[pos, -1])
            else:
                valores_folga.append(0)
        
        # Exibir resultados
        print("\n===== Resultado Final =====")
        print("Função Objetivo (Z) =", z_otimo)
        print("\nVariáveis de Decisão:")
        for i, val in enumerate(valores_x):
            print(f"x{i+1} = {val:.2f}")
        
        print("\nVariáveis de Folga:")
        for i, val in enumerate(valores_folga):
            print(f"f{i+1} = {val:.2f}")

def main():
    print("\n==== SIMPLEX TABULADO - MÉTODO PASSO A PASSO ====\n")
    
    try:
        # Tentar importar tabulate
        import tabulate
    except ImportError:
        print("Instalando a biblioteca tabulate necessária para formatação...")
        import subprocess
        subprocess.check_call(["pip", "install", "tabulate"])
    
    # Pedir ao usuário para escolher entrada manual ou usar exemplo
    escolha = input("Deseja inserir dados manualmente (M) ou usar o exemplo do código (E)? ").strip().upper()
    
    if escolha == 'M':
        c, A, b = obter_dados_usuario()
    else:
        # Usar o novo exemplo fornecido
        print("\nUsando o exemplo do código...")
        c = [-40, -30, -20]  # Negativo para maximização
        A = [
            [2, 5, 10],
            [2, 5, 1],
            [4, 2, 2]
        ]
        b = [900, 400, 600]
    
    # Exibir o problema completo antes de iniciar
    exibir_problema_completo(c, A, b)
    
    # Resolver usando o simplex tabulado
    simplex = SimplexTabulado(c, A, b)
    simplex.resolver()
    
    # Opcional: comparar com a solução da biblioteca scipy
    print("\n===== Verificação usando scipy =====")
    res = linprog(c=c, A_ub=A, b_ub=b, method='highs')
    print("Resultado scipy:")
    print(f"X = {res.x}")
    print(f"Z = {-res.fun}")

if __name__ == "__main__":
    main()
