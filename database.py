"""
database.py - Sistema de Banco de Dados para AI Support System
Este arquivo gerencia toda a estrutura de dados usando SQLite
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class SupportDatabase:
    """Classe principal para gerenciar o banco de dados de suporte"""
    
    def __init__(self, db_name: str = "support_system.db"):
        """
        Inicializa a conexão com o banco de dados
        Args:
            db_name: Nome do arquivo do banco de dados
        """
        self.db_name = db_name
        self.conn = None
        self.create_tables()
    
    def get_connection(self):
        """Cria e retorna uma conexão com o banco de dados"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return self.conn
    
    def create_tables(self):
        """Cria todas as tabelas necessárias se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de Tickets (pedidos de suporte)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        """)
        
        # Tabela de Base de Conhecimento (soluções conhecidas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                problem_description TEXT NOT NULL,
                solution TEXT NOT NULL,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Histórico de IA (registro das ações da IA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                action_type TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        """)
        
        # Tabela de Respostas Sugeridas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggested_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                response_text TEXT NOT NULL,
                is_approved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets (id)
            )
        """)
        
        conn.commit()
        
        # Popula base de conhecimento inicial se estiver vazia
        self._populate_initial_knowledge_base()
    
    def _populate_initial_knowledge_base(self):
        """Adiciona conhecimento inicial à base de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe conteúdo
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Dados iniciais de conhecimento (exemplos de fintech)
            initial_knowledge = [
                {
                    "title": "PIX não está funcionando",
                    "category": "Pagamentos",
                    "problem": "Cliente não consegue realizar transferência via PIX",
                    "solution": "Verifique: 1) Se o limite diário foi atingido, 2) Se o saldo está disponível, 3) Se os dados do destinatário estão corretos, 4) Tente novamente após alguns minutos",
                    "keywords": "pix,transferencia,falha,erro,limite"
                },
                {
                    "title": "Erro ao cadastrar cartão",
                    "category": "Cadastro",
                    "problem": "Sistema não aceita dados do cartão de crédito",
                    "solution": "Confirme: 1) Número do cartão digitado corretamente, 2) Data de validade futura, 3) CVV correto, 4) Nome igual ao do cartão. Limpe cache do navegador e tente novamente.",
                    "keywords": "cartao,credito,cadastro,erro,recusado"
                },
                {
                    "title": "Saldo não atualizado",
                    "category": "Financeiro",
                    "problem": "Transação realizada mas saldo não foi atualizado",
                    "solution": "Transações podem levar até 2 horas para processar. Se após esse período ainda não atualizar, solicite protocolo de atendimento.",
                    "keywords": "saldo,atualização,transacao,demora"
                },
                {
                    "title": "Erro de login",
                    "category": "Técnico",
                    "problem": "Cliente não consegue fazer login no aplicativo",
                    "solution": "1) Verifique a senha (use 'esqueci minha senha'), 2) Limpe cache do app, 3) Atualize para última versão, 4) Reinstale o aplicativo",
                    "keywords": "login,senha,acesso,erro,autenticacao"
                },
                {
                    "title": "Cobrança duplicada",
                    "category": "Financeiro",
                    "problem": "Cliente foi cobrado duas vezes pela mesma transação",
                    "solution": "Verifique o histórico de transações. Se confirmado, solicite estorno imediato. Uma das cobranças será estornada em até 7 dias úteis.",
                    "keywords": "cobrança,duplicada,estorno,reembolso"
                }
            ]
            
            for kb in initial_knowledge:
                cursor.execute("""
                    INSERT INTO knowledge_base (title, category, problem_description, solution, keywords)
                    VALUES (?, ?, ?, ?, ?)
                """, (kb["title"], kb["category"], kb["problem"], kb["solution"], kb["keywords"]))
            
            conn.commit()
    
    # ===== FUNÇÕES PARA TICKETS =====
    
    def create_ticket(self, customer_name: str, customer_email: str, 
                     subject: str, description: str) -> int:
        """
        Cria um novo ticket no sistema
        Returns: ID do ticket criado
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tickets (customer_name, customer_email, subject, description)
            VALUES (?, ?, ?, ?)
        """, (customer_name, customer_email, subject, description))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Busca um ticket específico por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_tickets(self, status: Optional[str] = None, 
                       category: Optional[str] = None) -> List[Dict]:
        """
        Busca todos os tickets com filtros opcionais
        Args:
            status: Filtra por status (Open, In Progress, Resolved, Closed)
            category: Filtra por categoria
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_ticket(self, ticket_id: int, **kwargs):
        """
        Atualiza campos de um ticket
        Aceita: category, priority, status, resolved_at
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Campos permitidos para atualização
        allowed_fields = ['category', 'priority', 'status', 'resolved_at']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            # Sempre atualiza updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
            values.append(ticket_id)
            
            cursor.execute(query, values)
            conn.commit()
    
    def search_similar_tickets(self, keywords: List[str], limit: int = 5) -> List[Dict]:
        """
        Busca tickets similares baseado em palavras-chave
        Args:
            keywords: Lista de palavras para buscar
            limit: Número máximo de resultados
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cria condições LIKE para cada palavra-chave
        conditions = []
        params = []
        
        for keyword in keywords:
            conditions.append("(description LIKE ? OR subject LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query = f"""
            SELECT * FROM tickets 
            WHERE {' OR '.join(conditions)}
            AND status = 'Resolved'
            ORDER BY created_at DESC
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== FUNÇÕES PARA BASE DE CONHECIMENTO =====
    
    def search_knowledge_base(self, keywords: List[str]) -> List[Dict]:
        """Busca soluções na base de conhecimento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        for keyword in keywords:
            conditions.append("""
                (keywords LIKE ? OR 
                 problem_description LIKE ? OR 
                 solution LIKE ? OR
                 title LIKE ?)
            """)
            params.extend([f"%{keyword}%"] * 4)
        
        query = f"""
            SELECT * FROM knowledge_base 
            WHERE {' OR '.join(conditions)}
            LIMIT 5
        """
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== FUNÇÕES PARA HISTÓRICO DE IA =====
    
    def log_ai_action(self, ticket_id: int, action_type: str, 
                     input_data: str, output_data: str, 
                     confidence_score: float = None):
        """Registra uma ação da IA no histórico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_history 
            (ticket_id, action_type, input_data, output_data, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, action_type, input_data, output_data, confidence_score))
        
        conn.commit()
    
    def get_ai_history(self, ticket_id: int) -> List[Dict]:
        """Busca histórico de ações da IA para um ticket"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_history 
            WHERE ticket_id = ? 
            ORDER BY created_at DESC
        """, (ticket_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ===== FUNÇÕES PARA RESPOSTAS SUGERIDAS =====
    
    def save_suggested_response(self, ticket_id: int, response_text: str):
        """Salva uma resposta sugerida pela IA"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO suggested_responses (ticket_id, response_text)
            VALUES (?, ?)
        """, (ticket_id, response_text))
        
        conn.commit()
        return cursor.lastrowid
    
    # ===== FUNÇÕES DE ESTATÍSTICAS =====
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de tickets
        cursor.execute("SELECT COUNT(*) FROM tickets")
        stats['total_tickets'] = cursor.fetchone()[0]
        
        # Tickets por status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM tickets 
            GROUP BY status
        """)
        stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Tickets por categoria
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM tickets 
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        stats['by_category'] = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # Taxa de resolução
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'Resolved' THEN 1 END) * 100.0 / COUNT(*) as resolution_rate
            FROM tickets
        """)
        stats['resolution_rate'] = cursor.fetchone()[0] or 0
        
        return stats
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Função auxiliar para criar instância do banco
def get_database() -> SupportDatabase:
    """Retorna uma instância do banco de dados"""
    return SupportDatabase()


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando database.py...")
    
    # Cria banco de teste
    db = SupportDatabase("test_support.db")
    
    # Cria ticket de teste
    ticket_id = db.create_ticket(
        customer_name="João Silva",
        customer_email="joao@email.com",
        subject="Problema com PIX",
        description="Não consigo fazer transferência via PIX"
    )
    
    print(f"✅ Ticket criado com ID: {ticket_id}")
    
    # Busca o ticket
    ticket = db.get_ticket(ticket_id)
    print(f"✅ Ticket encontrado: {ticket['subject']}")
    
    # Busca na base de conhecimento
    kb_results = db.search_knowledge_base(["pix", "transferencia"])
    print(f"✅ Encontrados {len(kb_results)} artigos na base de conhecimento")
    
    # Estatísticas
    stats = db.get_statistics()
    print(f"✅ Estatísticas: {stats}")
    
    print("\n🎉 Todos os testes passaram!")
    
    db.close()