"""
app.py - Interface Web do AI-Powered Support System
Dashboard interativo usando Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Importa nossos módulos
from database import SupportDatabase, get_database
from ai_engine import AIEngine, get_ai_engine
from data_generator import TicketGenerator, get_generator

# Configuração da página
st.set_page_config(
    page_title="AI-Powered Support System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #856404;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)


# Inicializa sessão
@st.cache_resource
def init_system():
    """Inicializa banco de dados e IA"""
    db = get_database()
    ai = get_ai_engine()
    generator = get_generator()
    return db, ai, generator


# Funções auxiliares
def format_datetime(dt_string):
    """Formata data/hora para exibição"""
    if not dt_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return dt_string


def get_priority_color(priority):
    """Retorna cor baseada na prioridade"""
    colors = {
        "Baixa": "🟢",
        "Média": "🟡",
        "Alta": "🟠",
        "Crítica": "🔴"
    }
    return colors.get(priority, "⚪")


def get_status_color(status):
    """Retorna cor baseada no status"""
    colors = {
        "Open": "🔵",
        "In Progress": "🟡",
        "Resolved": "🟢",
        "Closed": "⚫"
    }
    return colors.get(status, "⚪")


# PÁGINAS DO SISTEMA
def show_dashboard(db):
    """Página principal - Dashboard com estatísticas"""
    
    st.markdown('<p class="main-header">🤖 AI-Powered Support System</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <b>💡 Sobre este projeto:</b> Sistema de suporte técnico com IA que demonstra 
        <b>Prompt Engineering</b>, <b>SQL</b> e automação end-to-end para Customer Support Engineering.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Estatísticas gerais
    stats = db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total de Tickets",
            value=stats.get('total_tickets', 0)
        )
    
    with col2:
        open_tickets = stats.get('by_status', {}).get('Open', 0)
        st.metric(
            label="🔵 Tickets Abertos",
            value=open_tickets
        )
    
    with col3:
        resolved = stats.get('by_status', {}).get('Resolved', 0)
        st.metric(
            label="🟢 Resolvidos",
            value=resolved
        )
    
    with col4:
        resolution_rate = stats.get('resolution_rate', 0)
        st.metric(
            label="✅ Taxa de Resolução",
            value=f"{resolution_rate:.1f}%"
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tickets por Categoria")
        
        if stats.get('by_category'):
            df_cat = pd.DataFrame([
                {"Categoria": k, "Quantidade": v}
                for k, v in stats['by_category'].items()
            ])
            
            fig = px.pie(
                df_cat,
                values='Quantidade',
                names='Categoria',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum ticket categorizado ainda.")
    
    with col2:
        st.subheader("📊 Tickets por Status")
        
        if stats.get('by_status'):
            df_status = pd.DataFrame([
                {"Status": k, "Quantidade": v}
                for k, v in stats['by_status'].items()
            ])
            
            fig = px.bar(
                df_status,
                x='Status',
                y='Quantidade',
                color='Status',
                color_discrete_map={
                    'Open': '#3498db',
                    'In Progress': '#f39c12',
                    'Resolved': '#2ecc71',
                    'Closed': '#95a5a6'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum ticket cadastrado ainda.")
    
    # Tickets recentes
    st.markdown("---")
    st.subheader("🕐 Últimos Tickets")
    
    recent_tickets = db.get_all_tickets()[:10]
    
    if recent_tickets:
        for ticket in recent_tickets:
            with st.expander(
                f"{get_status_color(ticket['status'])} "
                f"#{ticket['id']} - {ticket['subject']} "
                f"({get_priority_color(ticket.get('priority', 'Média'))} {ticket.get('priority', 'Média')})"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Cliente:** {ticket['customer_name']}")
                    st.write(f"**Email:** {ticket['customer_email']}")
                    st.write(f"**Descrição:** {ticket['description']}")
                
                with col2:
                    st.write(f"**Status:** {ticket['status']}")
                    st.write(f"**Categoria:** {ticket.get('category', 'Não categorizado')}")
                    st.write(f"**Criado em:** {format_datetime(ticket['created_at'])}")
    else:
        st.info("📭 Nenhum ticket cadastrado ainda. Use a aba 'Novo Ticket' ou 'Gerar Dados' para começar!")


def show_new_ticket(db, ai):
    """Página para criar novo ticket com análise de IA"""
    
    st.header("📝 Novo Ticket de Suporte")
    
    st.markdown("""
    <div class="info-box">
        <b>🤖 IA Ativada:</b> Ao criar o ticket, a IA irá automaticamente categorizar, 
        determinar prioridade e sugerir uma resposta!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulário
    with st.form("new_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("👤 Nome do Cliente", placeholder="Ex: João Silva")
        
        with col2:
            customer_email = st.text_input("📧 Email", placeholder="joao@email.com")
        
        subject = st.text_input("📌 Assunto", placeholder="Ex: Problema com PIX")
        
        description = st.text_area(
            "📄 Descrição do Problema",
            placeholder="Descreva o problema em detalhes...",
            height=150
        )
        
        submitted = st.form_submit_button("🤖 Criar e Analisar com IA", use_container_width=True)
    
    if submitted:
        if not customer_name or not customer_email or not subject or not description:
            st.error("⚠️ Por favor, preencha todos os campos!")
            return
        
        # Progress bar para mostrar processamento
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Passo 1: Criar ticket
        status_text.text("📝 Criando ticket no banco de dados...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        ticket_id = db.create_ticket(
            customer_name=customer_name,
            customer_email=customer_email,
            subject=subject,
            description=description
        )
        
        # Passo 2: Analisar com IA
        status_text.text("🤖 Analisando com IA (Prompt Engineering)...")
        progress_bar.progress(40)
        
        ai_result = ai.categorize_ticket(
            ticket_subject=subject,
            ticket_description=description
        )
        
        progress_bar.progress(60)
        
        # Passo 3: Atualizar ticket com dados da IA
        status_text.text("💾 Salvando categorização...")
        
        db.update_ticket(
            ticket_id=ticket_id,
            category=ai_result.get('category'),
            priority=ai_result.get('priority')
        )
        
        # Registra ação da IA
        db.log_ai_action(
            ticket_id=ticket_id,
            action_type="categorization",
            input_data=f"{subject} | {description}",
            output_data=str(ai_result),
            confidence_score=ai_result.get('confidence')
        )
        
        progress_bar.progress(80)
        
        # Passo 4: Gerar resposta sugerida
        status_text.text("💬 Gerando resposta sugerida...")
        
        # Busca soluções conhecidas
        keywords = ai_result.get('keywords', [])
        kb_results = db.search_knowledge_base(keywords)
        solutions = [kb['solution'] for kb in kb_results]
        
        suggested_response = ai.generate_response(
            ticket_description=description,
            category=ai_result.get('category'),
            similar_solutions=solutions,
            customer_name=customer_name
        )
        
        # Salva resposta sugerida
        db.save_suggested_response(ticket_id, suggested_response)
        
        progress_bar.progress(100)
        status_text.text("✅ Ticket criado e analisado com sucesso!")
        
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Mostra resultados
        st.success(f"✅ Ticket #{ticket_id} criado com sucesso!")
        
        st.markdown("---")
        st.subheader("🤖 Análise da IA")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📂 Categoria</h4>
                <h2>{ai_result.get('category')}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            priority = ai_result.get('priority')
            st.markdown(f"""
            <div class="metric-card">
                <h4>⚠️ Prioridade</h4>
                <h2>{get_priority_color(priority)} {priority}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎯 Confiança</h4>
                <h2>{ai_result.get('confidence')}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Palavras-chave
        st.markdown("**🔑 Palavras-chave identificadas:**")
        keywords_text = ", ".join(ai_result.get('keywords', []))
        st.info(keywords_text)
        
        # Raciocínio
        st.markdown("**🧠 Raciocínio da IA:**")
        st.write(ai_result.get('reasoning', 'N/A'))
        
        # Resposta sugerida
        st.markdown("---")
        st.subheader("💬 Resposta Sugerida pela IA")
        
        st.markdown(f"""
        <div class="success-box">
            {suggested_response}
        </div>
        """, unsafe_allow_html=True)
        
        # Soluções similares encontradas
        if kb_results:
            st.markdown("---")
            st.subheader("🔍 Soluções Similares da Base de Conhecimento")
            
            for kb in kb_results[:3]:
                with st.expander(f"📄 {kb['title']}"):
                    st.write(f"**Categoria:** {kb['category']}")
                    st.write(f"**Problema:** {kb['problem_description']}")
                    st.write(f"**Solução:** {kb['solution']}")


def show_all_tickets(db):
    """Página com lista de todos os tickets"""
    
    st.header("📋 Todos os Tickets")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filtrar por Status",
            ["Todos", "Open", "In Progress", "Resolved", "Closed"]
        )
    
    with col2:
        category_filter = st.selectbox(
            "Filtrar por Categoria",
            ["Todos", "Pagamentos", "Cadastro", "Técnico", "Financeiro", "Outros"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Ordenar por",
            ["Mais Recentes", "Mais Antigos", "Prioridade"]
        )
    
    # Busca tickets
    status = None if status_filter == "Todos" else status_filter
    category = None if category_filter == "Todos" else category_filter
    
    tickets = db.get_all_tickets(status=status, category=category)
    
    # Ordenação
    if sort_by == "Mais Antigos":
        tickets = list(reversed(tickets))
    elif sort_by == "Prioridade":
        priority_order = {"Crítica": 0, "Alta": 1, "Média": 2, "Baixa": 3}
        tickets = sorted(tickets, key=lambda x: priority_order.get(x.get('priority', 'Média'), 4))
    
    st.markdown(f"**Total: {len(tickets)} tickets**")
    st.markdown("---")
    
    if not tickets:
        st.info("📭 Nenhum ticket encontrado com os filtros selecionados.")
        return
    
    # Exibe tickets
    for ticket in tickets:
        with st.expander(
            f"{get_status_color(ticket['status'])} "
            f"#{ticket['id']} - {ticket['subject']} "
            f"({get_priority_color(ticket.get('priority', 'Média'))} {ticket.get('priority', 'Média')})"
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Cliente:** {ticket['customer_name']}")
                st.write(f"**Email:** {ticket['customer_email']}")
                st.write(f"**Descrição:** {ticket['description']}")
            
            with col2:
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Categoria:** {ticket.get('category', 'N/A')}")
                st.write(f"**Prioridade:** {ticket.get('priority', 'N/A')}")
                st.write(f"**Criado:** {format_datetime(ticket['created_at'])}")
            
            # Botões de ação
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"✅ Resolver", key=f"resolve_{ticket['id']}"):
                    db.update_ticket(
                        ticket['id'],
                        status='Resolved',
                        resolved_at=datetime.now().isoformat()
                    )
                    st.success("Ticket resolvido!")
                    st.rerun()
            
            with col2:
                if st.button(f"🔄 Em Progresso", key=f"progress_{ticket['id']}"):
                    db.update_ticket(ticket['id'], status='In Progress')
                    st.success("Status atualizado!")
                    st.rerun()
            
            with col3:
                if st.button(f"🔒 Fechar", key=f"close_{ticket['id']}"):
                    db.update_ticket(ticket['id'], status='Closed')
                    st.success("Ticket fechado!")
                    st.rerun()


def show_generate_data(db, generator):
    """Página para gerar dados sintéticos"""
    
    st.header("🎲 Gerar Dados de Teste")
    
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ Dados Sintéticos:</b> Esta funcionalidade gera tickets falsos mas realistas 
        para demonstração do sistema. Ideal para popular o banco e fazer testes!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_tickets = st.slider("Quantos tickets gerar?", 1, 100, 20)
    
    with col2:
        include_categories = st.checkbox("Categorizar automaticamente?", value=False)
    
    if st.button("🎲 Gerar Tickets Sintéticos", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        tickets_data = generator.generate_multiple_tickets(num_tickets)
        
        for i, ticket_data in enumerate(tickets_data):
            status_text.text(f"Gerando ticket {i+1}/{num_tickets}...")
            progress_bar.progress((i + 1) / num_tickets)
            
            # Cria ticket
            ticket_id = db.create_ticket(
                customer_name=ticket_data['customer_name'],
                customer_email=ticket_data['customer_email'],
                subject=ticket_data['subject'],
                description=ticket_data['description']
            )
            
            # Se quiser categorizar, atualiza
            if include_categories:
                db.update_ticket(
                    ticket_id,
                    category=ticket_data['category'],
                    priority=ticket_data['priority']
                )
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"✅ {num_tickets} tickets gerados com sucesso!")
        
        # Mostra estatísticas
        st.markdown("---")
        st.subheader("📊 Tickets Gerados")
        
        categories = {}
        for t in tickets_data:
            cat = t['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        df = pd.DataFrame([
            {"Categoria": k, "Quantidade": v}
            for k, v in categories.items()
        ])
        
        fig = px.bar(df, x='Categoria', y='Quantidade', color='Categoria')
        st.plotly_chart(fig, use_container_width=True)


# MAIN APP
def main():
    """Função principal do aplicativo"""
    
    # Inicializa sistema
    db, ai, generator = init_system()
    
    # Sidebar
    st.sidebar.title("🤖 AI Support System")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navegação",
        ["🏠 Dashboard", "📝 Novo Ticket", "📋 Todos os Tickets", "🎲 Gerar Dados"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Sobre o Projeto")
    st.sidebar.info("""
    Sistema de suporte técnico com IA que demonstra:
    
    - ✅ Prompt Engineering
    - ✅ SQL avançado
    - ✅ Automação end-to-end
    - ✅ IA local (Ollama)
    
    **Stack:** Python, Streamlit, SQLite, Ollama/Llama 3.2
    """)
    
    # Roteamento de páginas
    if page == "🏠 Dashboard":
        show_dashboard(db)
    elif page == "📝 Novo Ticket":
        show_new_ticket(db, ai)
    elif page == "📋 Todos os Tickets":
        show_all_tickets(db)
    elif page == "🎲 Gerar Dados":
        show_generate_data(db, generator)


if __name__ == "__main__":
    main()