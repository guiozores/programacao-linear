# Simplex Tabulado - Método Passo a Passo

Este projeto implementa o método Simplex passo a passo para resolver problemas de programação linear (PPL). Disponibilizamos duas interfaces e dois métodos de resolução:

- **Interface de Terminal**: Para execução simples via linha de comando
- **Interface Web**: Uma interface gráfica interativa usando Streamlit
- **Métodos de Resolução**: Tabulado (tabular) e Analítico (algébrico)

## Requisitos

- Python 3.6 ou superior
- Bibliotecas necessárias:
  - numpy
  - pandas
  - scipy
  - tabulate
  - streamlit (para interface gráfica)

## Instalação

1. Clone este repositório ou baixe os arquivos manualmente:

```bash
git clone https://github.com/guiozores/programacao-linear.git
```

2. Navegue até o diretório do projeto:

```bash
cd prova
```

3. Instale as dependências necessárias:

   **Opção 1**: Usando o arquivo requirements.txt:

   ```bash
   pip install -r requirements.txt
   ```

   **Opção 2**: Instalando manualmente cada biblioteca:

   ```bash
   pip install numpy pandas scipy tabulate streamlit
   ```

## Executando a Versão Terminal

A versão terminal permite resolver problemas de programação linear direto pelo terminal, mostrando o passo a passo da resolução.

Para o método tabulado:

```bash
python tabuladoterminal.py
```


Ao executar, você terá as opções:

- **E**: Usar o exemplo predefinido (maximização com 3 variáveis e 3 restrições)
- **M**: Inserir dados manualmente (você definirá o número de variáveis e restrições)

O programa exibirá:

1. A definição do problema completo
2. As tabelas do simplex em cada iteração (método tabulado)
3. As manipulações algébricas em cada passo (método analítico)
4. A solução final com valores das variáveis de decisão e folga

## Executando a Versão Web com Streamlit

A interface web oferece uma experiência mais visual e interativa:

```bash
streamlit run tabuladofrontend.py
```

Isso iniciará o servidor Streamlit e abrirá automaticamente seu navegador padrão. Se não abrir, acesse `http://localhost:8501`.

### Passos para usar a interface web:

1. **Configuração do Problema**:

   - Escolha entre usar o exemplo predefinido ou inserir dados manualmente
   - Se optar por dados manuais, defina o número de variáveis e restrições
   - Insira os coeficientes da função objetivo (para maximização)
   - Insira os coeficientes das restrições e seus limites
   - Clique em "Configurar Problema"

2. **Solução Tabulada Passo a Passo**:

   - Navegue para a aba "Solução Tabulada"
   - Use o botão "Próximo Passo" para avançar uma iteração de cada vez
   - Use o botão "Mostrar Solução Completa" para executar todas as iterações automaticamente
   - Use o botão "Reiniciar" para começar novamente com o mesmo problema

3. **Solução Analítica Passo a Passo**:

   - Navegue para a aba "Solução Analítica"
   - Clique em "Mostrar Solução Analítica Completa" para ver todos os passos do método analítico
   - Cada etapa do processo é detalhada com as manipulações algébricas
   - Use o botão "Reiniciar Solução Analítica" para começar novamente

4. **Visualização**:
   - Na solução tabulada: a tabela do simplex é exibida com formatação apropriada
   - Na solução analítica: cada passo algébrico é mostrado em detalhes
   - Os elementos importantes são destacados para facilitar o acompanhamento

## Estrutura do Projeto

- **tabuladocore.py**: Implementação do algoritmo Simplex Tabulado
- **analiticocore.py**: Implementação do algoritmo Simplex Analítico
- **tabuladofrontend.py**: Interface web usando Streamlit para ambos os métodos
- **tabulaterminal.py**: Implementação do algoritmo Simplex Tabulado em terminal com * nas fileiras/colunas pivo.
- **README.md**: Documentação do projeto

## Exemplo Predefinido

O exemplo padrão disponível é:

Maximizar Z = 40x₁ + 30x₂ + 20x₃

Sujeito a:

- 2x₁ + 5x₂ + 10x₃ ≤ 900
- 2x₁ + 5x₂ + 1x₃ ≤ 400
- 4x₁ + 2x₂ + 2x₃ ≤ 600
- x₁, x₂, x₃ ≥ 0

## Criando Seu Próprio Problema

Você pode inserir seus próprios problemas de programação linear através de qualquer uma das interfaces. Certifique-se de que:

1. Todas as restrições sejam do tipo "menor ou igual" (≤)
2. Todas as variáveis sejam não-negativas
3. O problema seja de maximização

## Diferença entre os Métodos

- **Método Tabulado**: Usa tabelas para resolver o simplex, mostrando as operações de pivotamento
- **Método Analítico**: Mostra o processo algébrico detalhado, com todas as substituições e manipulações

## Observações

- O algoritmo usa o método Simplex em sua forma tabulada e analítica
- Para problemas de minimização, você precisa multiplicar os coeficientes da função objetivo por -1
- A implementação atual não lida com problemas degenerados ou com múltiplas soluções ótimas
