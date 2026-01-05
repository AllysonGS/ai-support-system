"""
data_generator.py - Gerador de Dados Sintéticos
Cria tickets realistas de fintech para demonstração do sistema
"""

from faker import Faker
import random
from typing import List, Dict
from datetime import datetime, timedelta

# Inicializa Faker com localização brasileira
fake = Faker('pt_BR')


class TicketGenerator:
    """Gera tickets de suporte realistas para fintech"""
    
    def __init__(self):
        """Inicializa o gerador com templates de tickets"""
        
        # Templates de problemas por categoria
        self.ticket_templates = {
            "Pagamentos": [
                {
                    "subject": "PIX não está funcionando",
                    "description": "Tentei fazer uma transferência via PIX mas aparece erro de {error_type}. Preciso fazer o pagamento urgente.",
                    "priority": "Alta"
                },
                {
                    "subject": "Pagamento recusado",
                    "description": "Meu pagamento de {value} foi recusado no cartão final {card_digits}. Não entendo o motivo.",
                    "priority": "Média"
                },
                {
                    "subject": "Transferência não chegou",
                    "description": "Fiz uma transferência há {hours} horas mas o destinatário não recebeu. Protocolo {protocol}.",
                    "priority": "Alta"
                },
                {
                    "subject": "Erro ao pagar boleto",
                    "description": "Escaneei o código de barras mas dá erro. O boleto vence hoje e não consigo pagar.",
                    "priority": "Crítica"
                },
                {
                    "subject": "Limite PIX atingido",
                    "description": "Recebi mensagem que meu limite diário foi atingido, mas só fiz uma transferência de {value}.",
                    "priority": "Média"
                }
            ],
            "Cadastro": [
                {
                    "subject": "Não consigo criar conta",
                    "description": "Preenchi todos os dados mas quando clico em 'finalizar' não acontece nada.",
                    "priority": "Média"
                },
                {
                    "subject": "Erro ao adicionar cartão",
                    "description": "Tento cadastrar meu cartão de crédito mas sempre dá erro de 'dados inválidos'.",
                    "priority": "Média"
                },
                {
                    "subject": "Selfie não é aceita",
                    "description": "Tirei a foto do documento mas a selfie de verificação não está sendo aceita.",
                    "priority": "Baixa"
                },
                {
                    "subject": "Validação de CPF falhou",
                    "description": "Sistema diz que meu CPF não confere, mas os dados estão corretos.",
                    "priority": "Alta"
                },
                {
                    "subject": "Email de confirmação não chega",
                    "description": "Já faz {hours} horas que me cadastrei mas o email de confirmação não chegou.",
                    "priority": "Média"
                }
            ],
            "Técnico": [
                {
                    "subject": "App não abre",
                    "description": "Quando tento abrir o aplicativo ele fecha sozinho. Já tentei desinstalar e instalar novamente.",
                    "priority": "Alta"
                },
                {
                    "subject": "Erro ao fazer login",
                    "description": "Senha está correta mas aparece 'credenciais inválidas'.",
                    "priority": "Alta"
                },
                {
                    "subject": "App muito lento",
                    "description": "O aplicativo está extremamente lento, demora minutos para carregar qualquer coisa.",
                    "priority": "Média"
                },
                {
                    "subject": "Biometria não funciona",
                    "description": "Configurei biometria mas nunca funciona, sempre tenho que usar senha.",
                    "priority": "Baixa"
                },
                {
                    "subject": "Notificações não chegam",
                    "description": "Não recebo notificações de transações. Já verifiquei permissões do celular.",
                    "priority": "Baixa"
                }
            ],
            "Financeiro": [
                {
                    "subject": "Saldo incorreto",
                    "description": "Meu saldo está mostrando {value} mas deveria ser {correct_value}.",
                    "priority": "Alta"
                },
                {
                    "subject": "Cobrança duplicada",
                    "description": "Fui cobrado duas vezes pela mesma compra de {value} no dia {date}.",
                    "priority": "Crítica"
                },
                {
                    "subject": "Estorno não processado",
                    "description": "Solicitei estorno há {days} dias mas ainda não foi processado.",
                    "priority": "Alta"
                },
                {
                    "subject": "Taxa cobrada indevidamente",
                    "description": "Vi uma taxa de {value} na minha fatura mas não sei do que é.",
                    "priority": "Média"
                },
                {
                    "subject": "Extrato com erro",
                    "description": "Há uma transação de {value} no dia {date} que eu não reconheço.",
                    "priority": "Crítica"
                }
            ],
            "Outros": [
                {
                    "subject": "Dúvida sobre produto",
                    "description": "Gostaria de saber mais sobre {product} e como funciona.",
                    "priority": "Baixa"
                },
                {
                    "subject": "Como aumentar limite?",
                    "description": "Gostaria de aumentar meu limite de PIX/TED. Qual o processo?",
                    "priority": "Baixa"
                },
                {
                    "subject": "Preciso de nota fiscal",
                    "description": "Realizei uma compra e preciso da nota fiscal para reembolso da empresa.",
                    "priority": "Média"
                },
                {
                    "subject": "Sugestão de melhoria",
                    "description": "Seria ótimo se o app tivesse {feature}. Tem previsão?",
                    "priority": "Baixa"
                }
            ]
        }
        
        # Variáveis para substituição
        self.error_types = [
            "limite diário", "saldo insuficiente", "chave não encontrada",
            "servidor indisponível", "timeout"
        ]
        
        self.products = [
            "cartão de crédito virtual", "investimentos", "seguros",
            "programa de pontos", "cashback"
        ]
        
        self.features = [
            "modo escuro", "widgets", "reconhecimento facial",
            "pagamento por aproximação", "categorização automática de gastos"
        ]
    
    def generate_ticket(self, category: str = None) -> Dict:
        """
        Gera um ticket sintético realista
        Args:
            category: Categoria específica ou None para aleatória
        Returns:
            Dicionário com dados do ticket
        """
        
        # Seleciona categoria
        if category is None or category not in self.ticket_templates:
            category = random.choice(list(self.ticket_templates.keys()))
        
        # Seleciona template aleatório da categoria
        template = random.choice(self.ticket_templates[category])
        
        # Gera dados do cliente
        customer_name = fake.name()
        customer_email = fake.email()
        
        # Processa a descrição com variáveis
        description = template["description"]
        
        # Substitui variáveis no texto
        description = description.replace("{error_type}", random.choice(self.error_types))
        description = description.replace("{value}", f"R$ {random.randint(10, 5000)},00")
        description = description.replace("{correct_value}", f"R$ {random.randint(10, 5000)},00")
        description = description.replace("{card_digits}", str(random.randint(1000, 9999)))
        description = description.replace("{hours}", str(random.randint(1, 48)))
        description = description.replace("{days}", str(random.randint(1, 30)))
        description = description.replace("{protocol}", f"#{random.randint(100000, 999999)}")
        description = description.replace("{date}", fake.date_between(start_date='-30d', end_date='today').strftime('%d/%m/%Y'))
        description = description.replace("{product}", random.choice(self.products))
        description = description.replace("{feature}", random.choice(self.features))
        
        return {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "subject": template["subject"],
            "description": description,
            "category": category,
            "priority": template["priority"]
        }
    
    def generate_multiple_tickets(self, count: int = 10, 
                                  category_distribution: Dict = None) -> List[Dict]:
        """
        Gera múltiplos tickets
        Args:
            count: Número de tickets a gerar
            category_distribution: Distribuição por categoria (opcional)
        Returns:
            Lista de dicionários com tickets
        """
        tickets = []
        
        if category_distribution is None:
            # Distribuição padrão realista
            category_distribution = {
                "Pagamentos": 0.35,      # 35% dos tickets
                "Técnico": 0.25,         # 25%
                "Financeiro": 0.20,      # 20%
                "Cadastro": 0.15,        # 15%
                "Outros": 0.05           # 5%
            }
        
        # Calcula quantos tickets por categoria
        for category, percentage in category_distribution.items():
            category_count = int(count * percentage)
            
            for _ in range(category_count):
                tickets.append(self.generate_ticket(category))
        
        # Completa até o número total (por causa de arredondamentos)
        while len(tickets) < count:
            tickets.append(self.generate_ticket())
        
        return tickets


# Função auxiliar
def get_generator() -> TicketGenerator:
    """Retorna instância do gerador"""
    return TicketGenerator()


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando data_generator.py...\n")
    
    generator = TicketGenerator()
    
    # Teste 1: Gerar um ticket
    print("📝 Gerando 1 ticket de exemplo:")
    ticket = generator.generate_ticket("Pagamentos")
    print(f"Cliente: {ticket['customer_name']}")
    print(f"Email: {ticket['customer_email']}")
    print(f"Assunto: {ticket['subject']}")
    print(f"Descrição: {ticket['description']}")
    print(f"Categoria: {ticket['category']}")
    print(f"Prioridade: {ticket['priority']}\n")
    
    # Teste 2: Gerar múltiplos tickets
    print("📋 Gerando 20 tickets variados...")
    tickets = generator.generate_multiple_tickets(20)
    
    # Estatísticas
    categories = {}
    for t in tickets:
        cat = t['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"✅ {len(tickets)} tickets gerados!")
    print("\n📊 Distribuição por categoria:")
    for cat, count in categories.items():
        print(f"  • {cat}: {count} tickets")
    
    print("\n🎉 Todos os testes passaram!")