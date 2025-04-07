import numpy as np
import streamlit as st
import pandas as pd
from scipy.optimize import linprog
import time
from app import SimplexTabulado, exibir_problema_completo  # Importar classes do arquivo original

# Configuração da página Streamlit
st.set_page_config(page_title="Simplex Tabulado - Método Passo a Passo", layout="wide")
st.title("Simplex Tabulado - Método Passo a Passo")

# Função para criar um dataframe estilizado da tabela simplex com destaque para o pivô
def criar_tabela_estilizada(simplex, col_pivo=None, row_pivo=None):
    # Preparar dados para o DataFrame
    colunas = [f'X{i+1}' for i in range(simplex.num_vars)] + \
              [f'F{i+1}' for i in range(simplex.num_restricoes)] + \
              ['Constante']
    
    # Obter as variáveis básicas atuais da tabela
    var_basicas = []
    for i in range(simplex.num_restricoes):
        vb_idx = simplex.base[i]
        if vb_idx < simplex.num_vars:
            var_basicas.append(f'X{vb_idx+1}')  # Variável de decisão na base
        else:
            var_basicas.append(f'F{vb_idx-simplex.num_vars+1}')  # Variável de folga na base
    
    # Criar dados para o DataFrame - Linha Z à parte e linhas das restrições
    linha_z = simplex.tabela[-1, :].copy()  # Linha Z com os valores negativos
    linhas_restricoes = simplex.tabela[:-1, :].copy()  # Linhas das restrições
    
    # Criar DataFrame com as linhas de restrições
    df_restricoes = pd.DataFrame(linhas_restricoes, columns=colunas)
    
    # Definir índices para as linhas de restrições usando as variáveis básicas ATUAIS
    indices_restricoes = [(var_basicas[i], f"{i+2}") for i in range(simplex.num_restricoes)]
    df_restricoes.index = pd.MultiIndex.from_tuples(indices_restricoes, names=["Variáveis", "N° Linha"])
    
    # Criar DataFrame para a linha Z
    linha_z_df = pd.DataFrame([linha_z], columns=colunas, index=pd.MultiIndex.from_tuples([("Z", "1")], names=["Variáveis", "N° Linha"]))
    
    # Concatenar a linha Z com as linhas de restrições
    df = pd.concat([linha_z_df, df_restricoes])
    
    # Adicionar coluna Z - valor 1 para linha Z e 0 para outras linhas
    coluna_z = [1] + [0] * simplex.num_restricoes
    df.insert(0, "Z", coluna_z)
    
    # Adicionar coluna de divisão se necessário
    if col_pivo is not None:
        razoes = []
        razoes.append(None)  # Sem razão para linha Z
        for i in range(simplex.num_restricoes):
            if simplex.tabela[i, col_pivo] > 0:
                razao = simplex.tabela[i, -1] / simplex.tabela[i, col_pivo]
                razoes.append(razao)
            else:
                razoes.append(None)
        df["Divisão"] = razoes
    
    # Estilizar o DataFrame
    def destacar_pivo(s):
        estilos = [''] * len(s)
        if col_pivo is not None and row_pivo is not None:
            # Destacar coluna do pivô - ajustar índice para considerar a coluna Z extra
            nome_coluna = colunas[col_pivo] if col_pivo < len(colunas) else None
            if s.name == nome_coluna:
                estilos = ['background-color: #ffeb99'] * len(s)
            
            # Destacar linha do pivô
            if s.name[0] == "Variáveis" or s.name[0] == "N° Linha":
                for i, idx in enumerate(s.index):
                    if isinstance(idx, tuple) and idx[1] == f"{row_pivo+2}":
                        estilos[i] = 'background-color: #ffeb99'
            
            # Destacar células na linha do pivô
            if isinstance(s.name, tuple) and s.name[1] == f"{row_pivo+2}":
                estilos = ['background-color: #ffeb99'] * len(s)
            
            # Destacar o elemento pivô com uma cor mais forte
            if isinstance(s.name, tuple) and s.name[1] == f"{row_pivo+2}":
                nome_coluna = colunas[col_pivo] if col_pivo < len(colunas) else None
                if nome_coluna in df.columns:
                    col_idx = list(df.columns).index(nome_coluna)
                    if col_idx < len(estilos):
                        estilos[col_idx] = 'background-color: #ff9900; font-weight: bold'
        return estilos
    
    styled_df = df.style.apply(destacar_pivo, axis=0).apply(destacar_pivo, axis=1)
    # Formato XX.XX para todos os números e centralizado
    styled_df = styled_df.format("{:.2f}", na_rep="-")
    
    # Centralizar todos os valores nas células
    styled_df = styled_df.set_properties(**{
        'text-align': 'center',
        'white-space': 'nowrap',
        'font-size': '14px',
        'padding': '5px 8px'
    })
    
    return styled_df

def executar_simplex_interativo():
    # Inicializar o estado da sessão se ainda não existir
    if 'simplex' not in st.session_state:
        simplex = st.session_state['simplex'] 
        st.session_state['iteracao'] = 0
        st.session_state['finalizado'] = False
        st.session_state['passos'] = []
        st.session_state['col_pivo'] = None
        st.session_state['row_pivo'] = None
    
    # Container para exibir a tabela atual
    tabela_container = st.container()
    
    # Botões para navegação - Adicionar botão de solução completa
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Próximo Passo"):
            avancar_simplex()
    
    with col2:
        if st.button("Mostrar Solução Completa"):
            # Executar todos os passos até encontrar a solução
            while not st.session_state['finalizado']:
                avancar_simplex(force_no_rerun=True)
            # Forçar atualização após completar todos os passos
            st.rerun()
    
    with col3:
        if st.button("Reiniciar"):
            # Limpar o estado e reiniciar o simplex
            if 'c' in st.session_state and 'A' in st.session_state and 'b' in st.session_state:
                simplex = SimplexTabulado(st.session_state['c'], st.session_state['A'], st.session_state['b'])
                st.session_state['simplex'] = simplex
                st.session_state['iteracao'] = 0
                st.session_state['finalizado'] = False
                st.session_state['passos'] = []
                st.session_state['col_pivo'] = None
                st.session_state['row_pivo'] = None
                
                # Adicionar a tabela inicial
                st.session_state['passos'].append({
                    'tipo': 'inicial',
                    'titulo': "Tabela Inicial",
                    'tabela': simplex.tabela.copy(),
                    'col_pivo': None,
                    'row_pivo': None
                })
                
                # Forçar a atualização da interface
                st.rerun()
    
    # Exibir os passos registrados
    exibir_passos_atuais(tabela_container)

def avancar_simplex(force_no_rerun=False):
    """Avança um passo no algoritmo simplex"""
    if st.session_state['finalizado']:
        return
        
    simplex = st.session_state['simplex']
    iteracao = st.session_state['iteracao']
    
    # Se não for a primeira iteração e temos um pivô, realizar o pivotamento
    if iteracao > 0 and st.session_state['col_pivo'] is not None and st.session_state['row_pivo'] is not None:
        col_pivo = st.session_state['col_pivo']
        row_pivo = st.session_state['row_pivo']
        
        # Realizar o pivotamento
        simplex.pivotar(row_pivo, col_pivo)
        
        # Registrar o passo de pivotamento
        st.session_state['passos'].append({
            'tipo': 'pivotamento',
            'titulo': f"Tabela após pivotamento (Iteração {iteracao})",
            'tabela': simplex.tabela.copy(),
            'base': simplex.base.copy(),
            'col_pivo': None,
            'row_pivo': None
        })
        
        # Limpar o pivô atual
        st.session_state['col_pivo'] = None
        st.session_state['row_pivo'] = None
    
    # Encontrar o próximo pivô
    col_pivo = simplex.encontrar_coluna_pivo()
    
    # Verificar se chegamos à solução ótima
    if col_pivo == -1:
        st.session_state['finalizado'] = True
        st.session_state['passos'].append({
            'tipo': 'final',
            'titulo': "Solução Ótima Encontrada",
            'tabela': simplex.tabela.copy(),
            'base': simplex.base.copy(),
            'col_pivo': None,
            'row_pivo': None
        })
    else:
        row_pivo = simplex.encontrar_linha_pivo(col_pivo)
        
        # Verificar se o problema é ilimitado
        if row_pivo == -1:
            st.session_state['finalizado'] = True
            st.session_state['passos'].append({
                'tipo': 'ilimitado',
                'titulo': "Problema Ilimitado",
                'tabela': simplex.tabela.copy(),
                'base': simplex.base.copy(),
                'col_pivo': col_pivo,
                'row_pivo': None
            })
        else:
            # Registrar o pivô para o próximo passo
            st.session_state['col_pivo'] = col_pivo
            st.session_state['row_pivo'] = row_pivo
            st.session_state['passos'].append({
                'tipo': 'pivotamento_pendente',
                'titulo': f"Iteração {iteracao+1} - Seleção do Pivô",
                'tabela': simplex.tabela.copy(),
                'base': simplex.base.copy(),
                'col_pivo': col_pivo,
                'row_pivo': row_pivo
            })
            st.session_state['iteracao'] += 1
    
    # Forçar a atualização da interface, apenas se não estiver no modo "sem rerun"
    if not force_no_rerun:
        st.rerun()

def exibir_passos_atuais(container):
    """Exibe os passos atuais do algoritmo simplex"""
    if 'passos' not in st.session_state or not st.session_state['passos']:
        return
    
    for idx, passo in enumerate(st.session_state['passos']):
        with container:
            st.subheader(passo['titulo'])
            
            # Criar tabela estilizada
            simplex = SimplexTabulado(st.session_state['c'], st.session_state['A'], st.session_state['b'])
            
            # Definir a tabela para este passo
            simplex.tabela = passo['tabela'].copy()
            
            # Se for a tabela inicial, usar a base original (todas as folgas)
            # Se não, usar a base salva para este passo específico
            if passo['tipo'] == 'inicial' or idx == 0:
                # Base inicial: todas as folgas F1, F2, F3...
                simplex.base = [simplex.num_vars + i for i in range(simplex.num_restricoes)]
            elif 'base' in passo:
                # Base salva com este passo
                simplex.base = passo['base'].copy()
            
            # Criar e exibir a tabela estilizada
            styled_df = criar_tabela_estilizada(
                simplex,
                passo['col_pivo'], 
                passo['row_pivo']
            )
            
            # Exibir tabela centralizada e com tamanho ajustado
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                # Definir largura automática e altura menor para a tabela
                st.dataframe(
                    styled_df,
                    width=None,  # Permite que a tabela tenha largura automática
                    height=None,  # Permite que a tabela tenha altura automática
                    use_container_width=False,  # Não usar toda a largura do contêiner
                    column_config={  # Configurações específicas de colunas
                        "Z": st.column_config.Column(width="small"),
                        "Constante": st.column_config.Column(width="small"),
                        "Divisão": st.column_config.Column(width="small"),
                    },
                    hide_index=False  # Mostrar índices de linha
                )
            
            # Exibir informações adicionais sobre o pivô
            if passo['tipo'] == 'pivotamento_pendente' and passo['col_pivo'] is not None and passo['row_pivo'] is not None:
                col_idx = passo['col_pivo']
                row_idx = passo['row_pivo']
                elemento_pivo = simplex.tabela[row_idx, col_idx]
                
                if col_idx < simplex.num_vars:
                    var_entrada = f"X{col_idx+1}"
                else:
                    var_entrada = f"F{col_idx-simplex.num_vars+1}"
                    
                vb_idx = simplex.base[row_idx]
                if vb_idx < simplex.num_vars:
                    var_saida = f"X{vb_idx+1}"
                else:
                    var_saida = f"F{vb_idx-simplex.num_vars+1}"
                
                with col2:
                    st.info(f"""
                    **Elemento pivô**: ({row_idx+1}, {col_idx+1}) = {elemento_pivo:.2f}
                    **Variável que entra na base**: {var_entrada}
                    **Variável que sai da base**: {var_saida}
                    """)
            
            # Exibir resultados finais
            elif passo['tipo'] == 'final':
                z_otimo = -simplex.tabela[-1, -1]
                
                # Valores das variáveis de decisão
                valores_x = [0] * simplex.num_vars
                for i, var_base in enumerate(simplex.base):
                    if var_base < simplex.num_vars:
                        valores_x[var_base] = simplex.tabela[i, -1]
                
                # Valores das variáveis de folga
                valores_folga = [0] * simplex.num_restricoes
                for i, var_base in enumerate(simplex.base):
                    if var_base >= simplex.num_vars:
                        idx = var_base - simplex.num_vars
                        valores_folga[idx] = simplex.tabela[i, -1]
                
                with col2:
                    st.success(f"""
                    **Função Objetivo (Z)** = {z_otimo:.2f}
                    
                    **Variáveis de Decisão:**
                    {', '.join([f"x{i+1} = {val:.2f}" for i, val in enumerate(valores_x)])}
                    
                    **Variáveis de Folga:**
                    {', '.join([f"f{i+1} = {val:.2f}" for i, val in enumerate(valores_folga)])}
                    """)
            
            # Exibir mensagem para problema ilimitado
            elif passo['tipo'] == 'ilimitado':
                with col2:
                    st.error("O problema é ilimitado! Não há solução ótima finita.")
            
            st.markdown("---")

def interface_entrada_dados():
    st.subheader("Configuração do Problema de Programação Linear")
    
    opcao = st.radio("Escolha uma opção:", ["Usar exemplo predefinido", "Inserir dados manualmente"])
    
    if opcao == "Usar exemplo predefinido":
        st.info("Usando o exemplo predefinido:")
        c = [-40, -30, -20]  # Negativo para maximização
        A = [
            [2, 5, 10],
            [2, 5, 1],
            [4, 2, 2]
        ]
        b = [900, 400, 600]
        
        # Exibir o problema
        st.markdown("**Maximizar Z = 40x₁ + 30x₂ + 20x₃**")
        st.markdown("**Sujeito a:**")
        st.markdown("2x₁ + 5x₂ + 10x₃ ≤ 900")
        st.markdown("2x₁ + 5x₂ + 1x₃ ≤ 400")
        st.markdown("4x₁ + 2x₂ + 2x₃ ≤ 600")
        st.markdown("x₁, x₂, x₃ ≥ 0")
        
    else:  # Inserir dados manualmente
        st.subheader("Configuração Manual")
        
        # Número de variáveis
        num_vars = st.number_input("Número de variáveis de decisão:", min_value=1, max_value=10, value=3)
        
        # Coeficientes da função objetivo
        st.subheader("Função Objetivo (Maximização)")
        c = []
        cols = st.columns(num_vars)
        for i in range(num_vars):
            with cols[i]:
                val = st.number_input(f"Coeficiente de x{i+1}:", value=0)
                c.append(-val)  # Negativo para maximização
        
        # Número de restrições
        num_restricoes = st.number_input("Número de restrições:", min_value=1, max_value=10, value=3)
        
        # Coeficientes das restrições
        A = []
        b = []
        
        for i in range(num_restricoes):
            st.markdown(f"**Restrição {i+1}:**")
            row = []
            cols = st.columns(num_vars + 1)
            
            for j in range(num_vars):
                with cols[j]:
                    val = st.number_input(f"Coef. de x{j+1} em R{i+1}:", key=f"r{i}c{j}", value=0)
                    row.append(val)
            
            with cols[-1]:
                val_b = st.number_input(f"Valor máximo para R{i+1}:", key=f"b{i}", value=0)
                b.append(val_b)
            
            A.append(row)
    
    # Exibir formulação completa
    if st.button("Configurar Problema"):
        # Armazenar os dados no estado da sessão
        st.session_state['c'] = c
        st.session_state['A'] = A
        st.session_state['b'] = b
        
        # Inicializar o simplex
        simplex = SimplexTabulado(c, A, b)
        st.session_state['simplex'] = simplex
        
        # Inicializar as variáveis de controle
        st.session_state['iteracao'] = 0
        st.session_state['finalizado'] = False
        st.session_state['passos'] = []
        st.session_state['col_pivo'] = None
        st.session_state['row_pivo'] = None
        
        # Adicionar a tabela inicial
        st.session_state['passos'].append({
            'tipo': 'inicial',
            'titulo': "Tabela Inicial",
            'tabela': simplex.tabela.copy(),
            'col_pivo': None,
            'row_pivo': None
        })
        
        # Exibir o problema completo
        st.subheader("Problema de Programação Linear")
        coefs_positivos = [-coef for coef in c]
        termos_z = []
        for i, coef in enumerate(coefs_positivos):
            if coef != 0:
                termos_z.append(f"{coef:.0f}x{i+1}")
        funcao_z = " + ".join(termos_z)
        st.markdown(f"**Z = {funcao_z}**")
        
        st.markdown("**Restrições:**")
        for i, (restricao, rhs) in enumerate(zip(A, b)):
            termos = []
            for j, coef in enumerate(restricao):
                if coef != 0:
                    termos.append(f"{coef:.0f}x{j+1}")
            eq_restricao = " + ".join(termos)
            st.markdown(f"R{i+1}: {eq_restricao} ≤ {rhs:.0f}")
        
        st.markdown("**Não-negatividade:**")
        vars_x = [f"x{i+1}" for i in range(len(c))]
        st.markdown(", ".join(vars_x) + " ≥ 0")
        
        # Forçar a atualização da interface
        st.rerun()

# Interface principal
if 'simplex' not in st.session_state:
    interface_entrada_dados()
else:
    # Abas para navegar entre configuração e solução
    tab1, tab2 = st.tabs(["Configuração", "Solução Passo a Passo"])
    
    with tab1:
        interface_entrada_dados()
    
    with tab2:
        executar_simplex_interativo()

# Instruções/ajuda
with st.expander("Ajuda"):
    st.markdown("""
    ### Como usar este aplicativo
    
    1. Na aba **Configuração**, defina o problema de programação linear:
       - Escolha entre usar o exemplo predefinido ou inserir dados manualmente
       - Para dados manuais, especifique o número de variáveis e restrições
       - Insira os coeficientes da função objetivo e das restrições
       - Clique em "Configurar Problema" para inicializar o simplex
    
    2. Na aba **Solução Passo a Passo**, você pode:
       - Ver o estado atual da tabela simplex
       - Clicar em "Próximo Passo" para avançar uma iteração
       - Clicar em "Mostrar Solução Completa" para executar todas as iterações automaticamente
       - Clicar em "Reiniciar" para começar de novo com o mesmo problema
       
    3. Entendendo a visualização:
       - A linha e coluna do pivô são destacadas em amarelo claro
       - O elemento pivô é destacado em laranja
       - Quando a solução ótima é encontrada, os valores finais são exibidos
    """)
