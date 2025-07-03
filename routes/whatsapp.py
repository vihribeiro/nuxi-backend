from flask import Blueprint, jsonify, request
from src.models.client import Client, db
from src.models.appointment import Appointment
from src.models.service import Service
from src.models.professional import Professional
from src.models.waitlist import Waitlist
from datetime import datetime, date, time, timedelta
import requests
import json
import pytz

whatsapp_bp = Blueprint('whatsapp', __name__)

# Configurações da Evolution API (devem ser configuradas via variáveis de ambiente)
EVOLUTION_API_URL = "https://evolutionapi.viniciusribeiro.dev.br"
EVOLUTION_API_KEY = "your-api-key"  # Deve ser configurado
INSTANCE_NAME = "nuxi-instance"  # Nome da instância

def get_brasilia_time():
    """Retorna o horário atual de Brasília"""
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(brasilia_tz)

def get_greeting():
    """Retorna a saudação baseada no horário de Brasília"""
    current_time = get_brasilia_time()
    hour = current_time.hour
    
    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

def send_whatsapp_message(phone_number, message, buttons=None):
    """Envia mensagem via Evolution API"""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    
    payload = {
        "number": phone_number,
        "text": message
    }
    
    if buttons:
        payload["options"] = {
            "buttons": buttons
        }
    
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return None

def get_or_create_client(phone_number, name=None):
    """Busca ou cria um cliente pelo telefone"""
    client = Client.query.filter_by(telefone=phone_number).first()
    
    if not client and name:
        client = Client(nome=name, telefone=phone_number)
        db.session.add(client)
        db.session.commit()
    
    return client

def get_available_periods():
    """Retorna os períodos disponíveis"""
    return {
        'manha': 'Manhã (08:00 - 12:00)',
        'tarde': 'Tarde (13:00 - 18:00)',
        'noite': 'Noite (19:00 - 22:00)'
    }

def get_available_times_for_period(period, target_date=None):
    """Retorna horários disponíveis para um período específico"""
    if not target_date:
        target_date = date.today()
    
    # Definir períodos
    periods = {
        'manha': (time(8, 0), time(12, 0)),
        'tarde': (time(13, 0), time(18, 0)),
        'noite': (time(19, 0), time(22, 0))
    }
    
    if period not in periods:
        return []
    
    start_time, end_time = periods[period]
    available_times = []
    
    # Gerar slots de 30 minutos
    current_time = start_time
    while current_time < end_time:
        # Verificar se o horário está ocupado
        existing_appointment = Appointment.query.filter(
            Appointment.data_agendamento == target_date,
            Appointment.hora_agendamento == current_time,
            Appointment.status.in_(['pendente', 'confirmado'])
        ).first()
        
        if not existing_appointment:
            available_times.append(current_time.strftime('%H:%M'))
        
        # Próximo slot (30 minutos)
        current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
    
    return available_times

def process_menu_selection(client, message_text):
    """Processa a seleção do menu principal"""
    greeting = get_greeting()
    
    if message_text == "1":
        # Agendar
        periods = get_available_periods()
        period_text = "\n".join([f"{key.upper()}: {value}" for key, value in periods.items()])
        
        response = f"Perfeito! Vamos agendar seu horário.\n\nEm qual período você gostaria de agendar?\n\n{period_text}\n\nDigite o período desejado (MANHA, TARDE ou NOITE):"
        
        return response
    
    elif message_text == "2":
        # Cancelar agendamento
        appointments = Appointment.query.filter(
            Appointment.client_id == client.id,
            Appointment.status.in_(['pendente', 'confirmado']),
            Appointment.data_agendamento >= date.today()
        ).all()
        
        if not appointments:
            return "Você não possui agendamentos ativos para cancelar."
        
        appointment_list = []
        for i, apt in enumerate(appointments, 1):
            appointment_list.append(
                f"{i}. {apt.data_agendamento.strftime('%d/%m/%Y')} às {apt.hora_agendamento.strftime('%H:%M')} - {apt.service.nome}"
            )
        
        response = f"Seus agendamentos:\n\n" + "\n".join(appointment_list)
        response += f"\n\nDigite o número do agendamento que deseja cancelar:"
        
        return response
    
    elif message_text == "3":
        # Verificar horários disponíveis
        periods = get_available_periods()
        period_text = "\n".join([f"{key.upper()}: {value}" for key, value in periods.items()])
        
        response = f"Consulta de horários disponíveis.\n\nEm qual período você gostaria de verificar?\n\n{period_text}\n\nDigite o período desejado (MANHA, TARDE ou NOITE):"
        
        return response
    
    else:
        # Opção inválida
        return f"{greeting}! Opção inválida. Por favor, escolha uma das opções:\n\n1 - Agendar\n2 - Cancelar agendamento\n3 - Verificar horários disponíveis"

@whatsapp_bp.route('/webhook/messages', methods=['POST'])
def webhook_messages():
    """Webhook para receber mensagens do WhatsApp via Evolution API"""
    try:
        data = request.json
        
        # Verificar se é uma mensagem recebida
        if not data or 'data' not in data:
            return jsonify({'status': 'ignored'}), 200
        
        message_data = data['data']
        
        # Verificar se é uma mensagem de entrada (não enviada por nós)
        if message_data.get('key', {}).get('fromMe', False):
            return jsonify({'status': 'ignored - own message'}), 200
        
        # Extrair informações da mensagem
        phone_number = message_data.get('key', {}).get('remoteJid', '').replace('@s.whatsapp.net', '')
        message_text = message_data.get('message', {}).get('conversation', '').strip()
        
        if not phone_number or not message_text:
            return jsonify({'status': 'ignored - invalid data'}), 200
        
        # Buscar ou criar cliente
        client = get_or_create_client(phone_number)
        
        # Se é a primeira mensagem, criar cliente com nome padrão
        if not client:
            client = get_or_create_client(phone_number, f"Cliente {phone_number}")
        
        # Processar mensagem
        greeting = get_greeting()
        
        # Verificar se é uma saudação inicial ou comando
        if message_text.lower() in ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'menu', 'inicio']:
            response = f"{greeting}! Bem-vindo ao Nuxi! 🎉\n\nEu sou seu assistente virtual para agendamentos. Como posso ajudá-lo hoje?\n\n1 - Agendar\n2 - Cancelar agendamento\n3 - Verificar horários disponíveis\n\nDigite o número da opção desejada:"
        
        elif message_text in ["1", "2", "3"]:
            response = process_menu_selection(client, message_text)
        
        elif message_text.upper() in ["MANHA", "TARDE", "NOITE"]:
            # Mostrar horários disponíveis para o período
            period = message_text.lower()
            available_times = get_available_times_for_period(period)
            
            if available_times:
                times_text = "\n".join([f"• {time}" for time in available_times])
                response = f"Horários disponíveis para {period}:\n\n{times_text}\n\nDigite o horário desejado (ex: 09:00) ou digite MENU para voltar ao menu principal:"
            else:
                response = f"Não há horários disponíveis para o período da {period} hoje. Gostaria de:\n\n1 - Verificar outro período\n2 - Entrar na fila de espera\n\nDigite MENU para voltar ao menu principal."
        
        else:
            # Mensagem não reconhecida
            response = f"Desculpe, não entendi sua mensagem. Digite MENU para ver as opções disponíveis ou escolha uma das opções:\n\n1 - Agendar\n2 - Cancelar agendamento\n3 - Verificar horários disponíveis"
        
        # Enviar resposta
        send_whatsapp_message(phone_number, response)
        
        return jsonify({'status': 'processed'}), 200
    
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@whatsapp_bp.route('/webhook/setup', methods=['POST'])
def setup_webhook():
    """Configura o webhook na Evolution API"""
    try:
        webhook_url = request.json.get('webhook_url')
        
        if not webhook_url:
            return jsonify({'error': 'webhook_url é obrigatório'}), 400
        
        url = f"{EVOLUTION_API_URL}/webhook/instance/{INSTANCE_NAME}"
        
        payload = {
            "url": webhook_url,
            "webhook_by_events": False,
            "webhook_base64": False,
            "events": [
                "MESSAGES_UPSERT",
                "CONNECTION_UPDATE"
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": EVOLUTION_API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({'message': 'Webhook configurado com sucesso', 'data': response.json()}), 200
        else:
            return jsonify({'error': 'Erro ao configurar webhook', 'details': response.text}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/send-message', methods=['POST'])
def send_message():
    """Endpoint para enviar mensagens via WhatsApp"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'error': 'phone_number e message são obrigatórios'}), 400
        
        result = send_whatsapp_message(phone_number, message)
        
        if result:
            return jsonify({'message': 'Mensagem enviada com sucesso', 'data': result}), 200
        else:
            return jsonify({'error': 'Erro ao enviar mensagem'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@whatsapp_bp.route('/send-reminder', methods=['POST'])
def send_reminder():
    """Envia lembretes de agendamento"""
    try:
        appointment_id = request.json.get('appointment_id')
        reminder_type = request.json.get('reminder_type')  # 24h, 12h, 6h, 3h
        
        appointment = Appointment.query.get_or_404(appointment_id)
        client = appointment.client
        
        if reminder_type == '3h':
            # Lembrete com botões de ação
            message = f"🔔 Lembrete: Você tem um agendamento hoje às {appointment.hora_agendamento.strftime('%H:%M')} para {appointment.service.nome}.\n\nPor favor, confirme sua presença:\n\n1 - Confirmar presença\n2 - Cancelar agendamento\n3 - Reagendar\n4 - Entrar na fila de espera"
        else:
            # Lembrete simples
            hours = reminder_type.replace('h', '')
            message = f"🔔 Lembrete: Você tem um agendamento em {hours} horas.\n\nData: {appointment.data_agendamento.strftime('%d/%m/%Y')}\nHorário: {appointment.hora_agendamento.strftime('%H:%M')}\nServiço: {appointment.service.nome}\nProfissional: {appointment.professional.user.username}"
        
        result = send_whatsapp_message(client.telefone, message)
        
        if result:
            return jsonify({'message': 'Lembrete enviado com sucesso'}), 200
        else:
            return jsonify({'error': 'Erro ao enviar lembrete'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

