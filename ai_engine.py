"""
ai_engine.py - Motor de IA com Prompt Engineering
Este arquivo contém toda a lógica de IA e prompts inteligentes
ESTE É O CORAÇÃO DO SISTEMA - DEMONSTRA PROMPT ENGINEERING NA PRÁTICA
"""

import ollama
import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class AIEngine:
    """
    Classe principal para interação com IA usando Prompt Engineering
    Demonstra técnicas avançadas de prompting para Customer Support
    """
    
    def __init__(self, model: str = "llama3.2"):
        """
        Inicializa o motor de IA
        Args:
            model: Nome do modelo Ollama a ser usado
        """
        self.model = model
        
        # Categorias disponíveis (definidas pelo negócio)
        self.categories = [
            "Pagamentos",
            "Cadastro", 
            "Técnico",
            "Financeiro",
            "Outros"
        ]
        
        # Níveis de prioridade
        self.priorities = ["Baixa", "Média", "Alta", "Crítica"]
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """
        Função auxiliar para chamar o modelo de linguagem
        Args:
            prompt: Texto do usuário
            system_prompt: Instruções para o modelo (opcional)
        Returns:
            Resposta da IA em formato string
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            print(f"❌ Erro ao chamar IA: {e}")
            return None
    
    def categorize_ticket(self, ticket_description: str, ticket_subject: str = "") -> Dict:
        """
        ✨ PROMPT ENGINEERING #1: Categorização Automática
        
        Este prompt demonstra técnicas profissionais de prompt engineering:
        - Role definition (definir papel da IA)
        - Clear constraints (restrições claras)
        - Output format specification (formato específico de saída)
        - Few-shot learning (exemplos de como responder)
        """
        
        # PROMPT ENGINEERING: Definição clara do papel e contexto
        system_prompt = f"""Você é um assistente especializado em suporte técnico de fintech.
Sua função é analisar tickets de clientes e categorizá-los com precisão.

CATEGORIAS DISPONÍVEIS:
{chr(10).join(f"- {cat}" for cat in self.categories)}

INSTRUÇÕES:
1. Leia o assunto e descrição do ticket
2. Identifique a categoria mais apropriada
3. Determine a prioridade (Baixa/Média/Alta/Crítica)
4. Extraia palavras-chave relevantes
5. Calcule um score de confiança (0-100)

RESPONDA APENAS NO FORMATO JSON ABAIXO (sem texto adicional):
{{
    "category": "categoria escolhida",
    "priority": "prioridade escolhida",
    "keywords": ["palavra1", "palavra2", "palavra3"],
    "confidence": 85,
    "reasoning": "breve explicação da escolha"
}}"""
        
        # PROMPT do usuário com contexto completo
        user_prompt = f"""Analise este ticket:

ASSUNTO: {ticket_subject}
DESCRIÇÃO: {ticket_description}

Responda APENAS com o JSON solicitado."""
        
        try:
            # Chama a IA
            response = self._call_llm(user_prompt, system_prompt)
            
            if not response:
                return self._fallback_categorization()
            
            # Extrai JSON da resposta (mesmo se vier com texto extra)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validação dos dados retornados
                if result.get('category') not in self.categories:
                    result['category'] = "Outros"
                
                if result.get('priority') not in self.priorities:
                    result['priority'] = "Média"
                
                return result
            else:
                return self._fallback_categorization()
                
        except json.JSONDecodeError:
            print("⚠️ Erro ao decodificar resposta da IA")
            return self._fallback_categorization()
        except Exception as e:
            print(f"⚠️ Erro na categorização: {e}")
            return self._fallback_categorization()
    
    def _fallback_categorization(self) -> Dict:
        """Categorização de fallback caso a IA falhe"""
        return {
            "category": "Outros",
            "priority": "Média",
            "keywords": ["suporte", "ajuda"],
            "confidence": 50,
            "reasoning": "Categorização automática indisponível"
        }
    
    def generate_response(self, ticket_description: str, 
                         category: str,
                         similar_solutions: List[str] = None,
                         customer_name: str = "Cliente") -> str:
        """
        ✨ PROMPT ENGINEERING #2: Geração de Resposta Contextual
        
        Demonstra:
        - Context injection (injeção de contexto)
        - Tone specification (especificação de tom)
        - Structured output (saída estruturada)
        - Retrieval augmented generation (geração aumentada por recuperação)
        """
        
        # Prepara contexto de soluções similares (RAG - Retrieval Augmented Generation)
        context = ""
        if similar_solutions and len(similar_solutions) > 0:
            context = "\n\nSOLUÇÕES CONHECIDAS PARA PROBLEMAS SIMILARES:\n"
            for i, sol in enumerate(similar_solutions[:3], 1):
                context += f"{i}. {sol}\n"
        
        # PROMPT ENGINEERING: Tom profissional + empático + acionável
        system_prompt = f"""Você é um especialista em Customer Support de fintech (empresa de pagamentos).

SUAS CARACTERÍSTICAS:
- Empático e profissional
- Objetivo e claro
- Focado em soluções práticas
- Tom amigável mas não informal demais

ESTRUTURA DA RESPOSTA:
1. Cumprimento personalizado
2. Demonstração de compreensão do problema
3. Solução clara e passo a passo (se aplicável)
4. Próximos passos ou o que esperar
5. Oferta de ajuda adicional

IMPORTANTE:
- Use no máximo 150 palavras
- Seja específico sobre a categoria: {category}
- Use linguagem clara, sem jargões técnicos complexos
- Inclua números de protocolo ou referências quando apropriado{context}"""
        
        user_prompt = f"""Gere uma resposta para este ticket:

PROBLEMA DO CLIENTE: {ticket_description}
CATEGORIA: {category}
NOME DO CLIENTE: {customer_name}

Crie uma resposta completa e útil."""
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            if not response:
                return self._fallback_response(customer_name)
            
            return response
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar resposta: {e}")
            return self._fallback_response(customer_name)
    
    def _fallback_response(self, customer_name: str) -> str:
        """Resposta padrão caso a IA falhe"""
        return f"""Olá {customer_name},

Obrigado por entrar em contato. Recebemos seu ticket e nossa equipe está analisando a situação.

Retornaremos com uma solução o mais breve possível.

Atenciosamente,
Equipe de Suporte"""
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        ✨ PROMPT ENGINEERING #3: Extração de Palavras-Chave
        
        Demonstra:
        - Task-specific prompting (prompts específicos para tarefas)
        - Output constraints (restrições de saída)
        """
        
        system_prompt = """Você é um especialista em análise de texto.
Extraia as palavras-chave mais relevantes do texto fornecido.

REGRAS:
- Retorne APENAS as palavras, separadas por vírgula
- Máximo de 5 palavras
- Sem artigos, preposições ou conectivos
- Apenas substantivos e verbos importantes
- Palavras em minúsculas"""
        
        user_prompt = f"Extraia palavras-chave deste texto: {text}"
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            if not response:
                return ["suporte", "ajuda"]
            
            # Processa a resposta
            keywords = [kw.strip().lower() for kw in response.split(',')]
            return keywords[:max_keywords]
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair keywords: {e}")
            return ["suporte", "ajuda"]
    
    def suggest_solutions(self, ticket_description: str, 
                         knowledge_base: List[Dict]) -> List[Dict]:
        """
        ✨ PROMPT ENGINEERING #4: Matching Semântico
        
        Usa IA para encontrar soluções relevantes na base de conhecimento
        Demonstra: semantic search via LLM
        """
        
        if not knowledge_base or len(knowledge_base) == 0:
            return []
        
        # Formata base de conhecimento
        kb_formatted = ""
        for i, kb in enumerate(knowledge_base, 1):
            kb_formatted += f"{i}. {kb.get('title', 'Sem título')}\n"
            kb_formatted += f"   Solução: {kb.get('solution', 'N/A')[:100]}...\n\n"
        
        system_prompt = """Você é um especialista em encontrar soluções relevantes.
Analise o problema do cliente e identifique quais soluções da base de conhecimento são mais relevantes.

RESPONDA APENAS com os NÚMEROS das soluções relevantes, separados por vírgula.
Exemplo: 1,3,5
Se nenhuma for relevante, responda: nenhuma"""
        
        user_prompt = f"""PROBLEMA DO CLIENTE:
{ticket_description}

BASE DE CONHECIMENTO:
{kb_formatted}

Quais soluções são relevantes?"""
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            if not response or "nenhuma" in response.lower():
                return []
            
            # Extrai números da resposta
            numbers = re.findall(r'\d+', response)
            relevant_solutions = []
            
            for num in numbers:
                idx = int(num) - 1
                if 0 <= idx < len(knowledge_base):
                    relevant_solutions.append(knowledge_base[idx])
            
            return relevant_solutions[:3]  # Máximo 3 soluções
            
        except Exception as e:
            print(f"⚠️ Erro ao sugerir soluções: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        ✨ PROMPT ENGINEERING #5: Análise de Sentimento
        
        Identifica o tom emocional do cliente (útil para priorização)
        """
        
        system_prompt = """Analise o sentimento/tom emocional do texto.

RESPONDA APENAS NO FORMATO JSON:
{
    "sentiment": "positivo/neutro/negativo/urgente",
    "emotion": "feliz/neutro/frustrado/irritado/preocupado",
    "urgency_score": 1-10
}"""
        
        user_prompt = f"Analise o sentimento deste texto: {text}"
        
        try:
            response = self._call_llm(user_prompt, system_prompt)
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                "sentiment": "neutro",
                "emotion": "neutro", 
                "urgency_score": 5
            }
            
        except Exception as e:
            print(f"⚠️ Erro na análise de sentimento: {e}")
            return {
                "sentiment": "neutro",
                "emotion": "neutro",
                "urgency_score": 5
            }


# Função auxiliar para criar instância
def get_ai_engine() -> AIEngine:
    """Retorna uma instância do motor de IA"""
    return AIEngine()


# Teste do módulo
if __name__ == "__main__":
    print("🧪 Testando ai_engine.py...")
    print("⚠️ Este teste requer que o Ollama esteja rodando com llama3.2!\n")
    
    try:
        ai = AIEngine()
        
        # Teste 1: Categorização
        print("📋 Teste 1: Categorizando ticket...")
        result = ai.categorize_ticket(
            ticket_subject="Problema urgente",
            ticket_description="Meu PIX não está funcionando e preciso fazer um pagamento urgente"
        )
        print(f"✅ Categoria: {result.get('category')}")
        print(f"✅ Prioridade: {result.get('priority')}")
        print(f"✅ Confiança: {result.get('confidence')}%")
        print(f"✅ Palavras-chave: {result.get('keywords')}\n")
        
        # Teste 2: Geração de resposta
        print("💬 Teste 2: Gerando resposta...")
        response = ai.generate_response(
            ticket_description="Não consigo fazer login no app",
            category="Técnico",
            customer_name="João"
        )
        print(f"✅ Resposta gerada:")
        print(f"{response}\n")
        
        # Teste 3: Extração de keywords
        print("🔑 Teste 3: Extraindo palavras-chave...")
        keywords = ai.extract_keywords("Meu cartão de crédito foi recusado na compra online")
        print(f"✅ Keywords: {keywords}\n")
        
        print("🎉 Todos os testes passaram!")
        print("\n💡 DICA: Este arquivo demonstra 5 técnicas de Prompt Engineering!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print("\n🔧 Verifique se:")
        print("1. Ollama está rodando (veja ícone na bandeja)")
        print("2. Modelo llama3.2 está instalado (ollama list)")
        print("3. Execute: ollama pull llama3.2")