import os  # Import necessário para acessar variáveis de ambiente
import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
import openai
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Carregar a chave da API do OpenAI de uma variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

logo_path = "logo_branco.png"

st.set_page_config(page_title='Simulador de ROI', page_icon='💰', layout='centered')

# CSS personalizado com imagem de fundo condicional
st.markdown(f"""
   <style>
        /* Inputs de texto com bordas arredondadas */
        .stTextInput>div>div>input {{
            border-radius: 20px;
        }}

        /* Botões com estilo personalizado */
        .stButton>button {{
            border-radius: 20px;
            border: 1px solid #144383; /* Azul */
            color: white; /* Texto branco */
            background-color: #144383; /* Azul */
            padding: 10px 24px;
            cursor: pointer;
            font-size: 16px;
        }}

        /* Efeito ao passar o mouse sobre os botões */
        .stButton>button:hover {{
            background-color: #D3D3D3; /* Cinza claro */
            color: #144383; /* Texto azul */
        }}

        /* Estilo para textos em markdown */
        .reportview-container .markdown-text-container {{
            font-family: monospace;
        }}

        /* Cor personalizada para markdown */
        .stMarkdown {{
            color: #FF4B4B; /* Vermelho */
        }}

        /* Feedback de sucesso com cor de fundo personalizada */
        .st-success {{
            background-color: #D4EDDA;
        }}

        /* Feedback de informação com cor de fundo personalizada */
        .st-info {{
            background-color: #D1ECF1;
        }}
    </style>
    """, unsafe_allow_html=True)

# Definição dos usuários e senhas
usuarios = {
    'Matheus': 'senhaMatheus',
    'Augusto': '!7uP32lm',
    'Eduardo': ')rHaI024',
    'Ivonete': 'Ff014>1P',
    'Alvaro': '67{8Nk6l',
    'Dani': 'g16Bm!2o',
    'Cristiane': '2SP1l7C5',
    'Well': '6u6#1E}t',
    'Julio': 'xM75RF2p'
}

def verificar_login():
    usuario = st.sidebar.text_input('Usuário', key='usuario_input')
    senha = st.sidebar.text_input('Senha', type='password', key='senha_input')
    if st.sidebar.button('Login'):
        if usuario in usuarios and usuarios[usuario] == senha:
            st.session_state['autenticado'] = True
            st.session_state['usuario_atual'] = usuario
            st.sidebar.success('Você está logado!')
            # Recarrega a página para aplicar o novo estilo de fundo
            st.experimental_rerun()  # Correção aqui
        else:
            st.session_state['autenticado'] = False
            st.sidebar.error('Usuário ou senha inválidos.')
            st.sidebar.warning('Por favor, realize o login para acessar a calculadora.')

# Função de logout
def realizar_logout():
    if st.sidebar.button('Logout'):
        st.session_state['autenticado'] = False
        del st.session_state['usuario_atual']

# Inicialização do estado da sessão para autenticação, se necessário
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

verificar_login()
realizar_logout()

# Carrega dados e mostra a calculadora se o usuário estiver autenticado

if st.session_state.get('autenticado', False):
    # Função para criar um gráfico de barras personalizado
    def criar_grafico(receita_mensal, investimento_mensal, logo_path=None):
        import io
        import numpy as np
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox

        # Define o fundo do gráfico como transparente
        background_color = 'none'

        fig, ax = plt.subplots(figsize=(10, 6))

        # Ajusta a cor de fundo do gráfico e dos eixos para transparente
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)

        # Dados para o gráfico
        categorias = ['Receita Mensal', 'Investimento Mensal']
        valores = [receita_mensal, investimento_mensal]

        # Criando o gráfico de barras
        bars = ax.bar(categorias, valores, color=['#4CAF50', '#FF5733'])

        # Adicionando valores no topo das barras
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'R$ {height:,.2f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, color='white')

        # Título e rótulos
        ax.set_title('Comparativo de Receita e Investimento Mensal', fontsize=16, color='white')
        ax.set_ylabel('Valor (R$)', fontsize=14, color='white')
        ax.set_ylim(0, max(valores) * 1.2)

        # Ajustando a cor dos rótulos dos eixos
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Removendo borda do gráfico para um visual mais clean
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('black')
        ax.spines['bottom'].set_color('black')

        # Adicionando o logotipo da empresa com transparência
        if logo_path:
            logo = Image.open(logo_path).convert("RGBA")  # Garante que a imagem está em RGBA
            logo_array = np.array(logo)

            # Cria o OffsetImage sem alterar o alfa
            imagebox = OffsetImage(logo_array, zoom=0.09)

            # Define a posição da imagem
            ab = AnnotationBbox(imagebox, (1, 1),
                                xycoords='axes fraction',
                                frameon=False,
                                box_alignment=(1, 1),
                                pad=0.1)

            ax.add_artist(ab)

        # Salvar o gráfico em um buffer com fundo transparente
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, bbox_inches='tight')
        buf.seek(0)

        # Exibir a imagem no Streamlit
        st.image(buf)

        # Fechar a figura para liberar memória
        plt.close(fig)

    # Função para gerar argumento
    def gerar_argumento(receita_mensal, investimento_mensal, roi):
        prompt = f"""
        O cliente está avaliando a compra de um equipamento para a sua clínica de estética que custa R$ {investimento_mensal:,.2f} por mês. Ele está interessado em entender o retorno sobre esse investimento (ROI) e como isso pode impactar positivamente sua operação. Com base em um ROI de {roi:.2%} e nas receitas mensais esperadas de R$ {receita_mensal:,.2f}, forneça argumentos claros e persuasivos que demonstrem os benefícios financeiros, operacionais e estratégicos deste investimento, e como ele ajudará o cliente a atingir seus principais objetivos. Adote um tom confiante e direto, focando em incentivar o cliente a perceber o valor do investimento e a tomar a decisão de compra.
        """
        response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                            {"role": "system", "content": "Você é um assistente de vendas que ajuda a argumentar com clientes."},
                            {"role": "user", "content": prompt}
                        ]
                    )
        # Assumindo que 'response' é o objeto retornado pela chamada à API
        argumento = response.choices[0].message.content
        return argumento

    # Título do aplicativo
    st.title('💰 Simulador de ROI')

    # Sidebar com o logotipo
    # st.sidebar.image(logo_path, use_column_width=True)

    # Inputs do usuário com layout melhorado
    st.header('📊 Insira os dados para simulação')
    with st.form(key='roi_form'):
        col1, col2 = st.columns(2)
        with col1:
            qtd_pessoas = st.number_input('Quantidade de pessoas atendidas por dia', min_value=1, value=10)
            preco_atendimento = st.number_input('Preço cobrado por atendimento (R$)', min_value=0.0, value=100.0, step=0.01)
        with col2:
            qtd_dias = st.number_input('Quantidade de dias trabalhados por mês', min_value=1, max_value=31, value=22)
            investimento_mensal = st.number_input('Investimento mensal (R$)', min_value=0.0, value=5000.0, step=0.01)
        submit_button = st.form_submit_button(label='Calcular')

    # Verifica se o botão 'Calcular' foi clicado ou se os dados já estão armazenados
    if submit_button:
        # Cálculos
        receita_mensal = qtd_pessoas * qtd_dias * preco_atendimento
        roi = (receita_mensal - investimento_mensal) / investimento_mensal

        # Armazenar os resultados no st.session_state
        st.session_state['receita_mensal'] = receita_mensal
        st.session_state['investimento_mensal'] = investimento_mensal
        st.session_state['roi'] = roi

    # Verifica se os valores estão disponíveis no st.session_state
    if 'receita_mensal' in st.session_state and 'investimento_mensal' in st.session_state and 'roi' in st.session_state:
        receita_mensal = st.session_state['receita_mensal']
        investimento_mensal = st.session_state['investimento_mensal']
        roi = st.session_state['roi']

        # Resultados com métricas estilizadas
        st.header('📈 Resultados')
        col1, col2 = st.columns(2)
        col1.metric('Receita Mensal', f'R$ {receita_mensal:,.2f}', delta=f'R$ {receita_mensal - investimento_mensal:,.2f}')
        col2.metric('ROI', f'{roi:.2%}', delta_color="inverse")

        # Gráfico de barras para visualização
        st.header('📊 Visualização do Retorno')
        criar_grafico(receita_mensal, investimento_mensal, logo_path)

        # Gerando argumentos com IA
        st.header('📝 Sugestões de Argumentos para Venda - IA')
        if st.button('Gerar Argumento'):
            # Função para limpar o texto
            def limpar_texto(texto):
                # Remove quebras de linha e retornos de carro
                texto_limpo = texto.replace('\n', ' ').replace('\r', ' ')
                # Remove espaços duplicados
                texto_limpo = ' '.join(texto_limpo.split())
                return texto_limpo

            # Função para definir o estilo da fonte
            def set_font_style():
                st.markdown(
                    """
                    <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
                    html, body, [class*="css"]  {
                        font-family: 'Roboto', sans-serif;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

            set_font_style()
            def gerar_argumento(receita_mensal, investimento_mensal, roi):
                prompt = f"""
                O cliente está avaliando a compra de um equipamento para a sua clínica de estética que custa R$ {investimento_mensal:,.2f} por mês. Ele está interessado em entender o retorno sobre esse investimento (ROI) e como isso pode impactar positivamente sua operação. Com base em um ROI de {roi:.2%} e nas receitas mensais esperadas de R$ {receita_mensal:,.2f}, forneça argumentos claros e persuasivos que demonstrem os benefícios financeiros, operacionais e estratégicos deste investimento, e como ele ajudará o cliente a atingir seus principais objetivos. Adote um tom confiante e direto, focando em incentivar o cliente a perceber o valor do investimento e a tomar a decisão de compra.
                """
                response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                            {"role": "system", "content": "Você é um assistente de vendas que ajuda a argumentar com clientes."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                # Assumindo que 'response' é o objeto retornado pela chamada à API
                argumento = response.choices[0].message.content
                return argumento

            argumento = gerar_argumento(receita_mensal, investimento_mensal, roi)
            st.write(argumento)
    else:
        st.info('Por favor, preencha os dados da simulação e clique em "Calcular" antes de gerar o argumento.')
