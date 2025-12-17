from django.shortcuts import render, redirect
from authentication.models.User import User as UserModel
from django.contrib.auth.decorators import login_required
from clientbank.models.Client import Client
from chatbot.models import ChatSession, ChatMessage
from clientbank.models.Transfer import Transfer
from clientbank.models.Credit import Credit
from clientbank.models.Invoice import Invoice
from management.models.Manager import Manager
from management.models.Management import Management
from django.utils import timezone
from decimal import Decimal
from google import generativeai as genai
from os import getenv

# Create your views here.

def build_prompt(user, client, credit, invoices, historico_texto, transferencias_texto, user_message):
    return f"""
        Você é um assistente virtual bancário chamado AlphaBot, projetado para ajudar os clientes com suas dúvidas e fornecer informações sobre serviços bancários. Seja educado, profissional e útil em suas respostas.

                ***Histórico de Conversa***
                {historico_texto}
                
                ***Informações do Cliente:***
                Nome: {user.first_name} {user.last_name}
                Email: {user.email}
                CPF: {user.cpf}
                Conta Bancária: {client.account_number}
                Saldo Atual: R$ {client.balance:.2f}
                Crédito: R$ {credit.credit_limit:.2f}
                Faturas Pendentes: {len([inv for inv in invoices if not inv.pay])}
                Últimas Transferências:
                {transferencias_texto}
                
                ***Informações Para as perguntas pre definidas***
                CASO O USUARIO PERGUNTE COMO REALIZAR TRANSFERENCIA, RESPONDA:
                Para realizar uma transferência, siga estes passos:
                1. Acesse sua conta e selecione o botão realizar transferência.
                2. Insira os detalhes do destinatário, incluindo o número da conta e o valor a ser transferido.
                3. Confirme os detalhes e autorize a transferência.
                4. Você receberá uma notificação quando a transferência for concluída com sucesso.
                
                ***Instruções:***
                1. Forneça informações precisas sobre produtos e serviços bancários.
                2. Ajude com dúvidas
                3. Nunca solicite informações sensíveis, como senhas ou números de cartão.
                4. Mantenha a confidencialidade e a segurança dos dados do cliente.
                
                ***Pergunta do Cliente:***
                {user_message}
                
                Responda de forma útil e amigável.
                Dê Boas Vindas ao cliente no início da conversa, ***APENAS NO INICIO***.
                Se a pergunta estiver fora do escopo bancário, responda educadamente que você está aqui para ajudar com questões bancárias.
                Não precisar ficar dando olá a cada pergunta, só no inicio da conversa, ou se a ultima mensagem for de uma data diferente do dia atual.
    """

def build_transfer_history(transfers):
    if not transfers:
        return "Nenhuma transferência recente."
    return "; ".join([f"R$ {t.amount:.2f} em {t.timestamp.strftime('%d/%m/%Y')}" for t in transfers])

def build_history_text(chat_session):
    
    historico = []
    mensagens = list(chat_session.messages.all().order_by('timestamp'))
    
    for i, msg in enumerate(mensagens):
        if msg.sender == 'user':
            historico.append(f"Cliente: {msg.message}")
        else:
            historico.append(f"AlphaBot: {msg.message}")
    
    historico_texto = "\n".join(historico)

    return historico_texto

@login_required(login_url='login')
def assistant_view(request):

    auth_user = request.user
    user = UserModel.objects.get(email=auth_user.email)
    client = Client.objects.get(user=user)
    chat_session, created = ChatSession.objects.get_or_create(client=client)
    credit = Credit.objects.get(client=client)
    invoices = list(Invoice.objects.filter(client=client))
    transfers = list(Transfer.objects.filter(sender=client).order_by('-timestamp')[:5])

    if request.method == 'POST':
        user_message = request.POST.get('message')

        if user_message:
            # Salvar a mensagem do usuário
            user_chat_message = ChatMessage.objects.create(
                sender='user',
                message=user_message
            )
            chat_session.messages.add(user_chat_message)
            chat_session.updated_at = timezone.now()
            chat_session.save()

            genai.configure(api_key=getenv('GENAI_API_KEY'))
            model = genai.GenerativeModel('models/gemini-2.5-flash')

            historico_texto = build_history_text(chat_session)
            
            transferencias_texto = build_transfer_history(transfers)
            
            prompt = build_prompt(user, client, credit, invoices, historico_texto, transferencias_texto, user_message)

            try:
                response = model.generate_content([
                    prompt
                ])
                response = response.text.strip()
            except Exception as e:
                response = "O chatbot está indisponível agora. Por favor, tente novamente mais tarde."
                print(f"Erro ao gerar resposta do assistente: {e}")

            bot_reply = response

            # Salvar a mensagem do bot
            bot_chat_message = ChatMessage.objects.create(
                sender='bot',
                message=bot_reply
            )

            chat_session.messages.add(bot_chat_message)
            chat_session.updated_at = timezone.now()
            chat_session.save()

    context = {
        'client': client,
        'chat_session': chat_session,
    }

    return render(request, 'interface.html', context)