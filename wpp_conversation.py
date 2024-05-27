from dataclasses import dataclass

from db_handler import get_session, reset_step, update_step
from wpp_client import WhatsappAPI


@dataclass
class WhatsAppMessage:
    from_number: str
    body: str
    ts: int


class WhatsAppConversation:
    client = WhatsappAPI()

    def __init__(self, number):
        self.number = number

    def process_message(self, input_message: WhatsAppMessage):
        step = self.session.get("step")
        ts = self.session.get("ts", 0)
        if ts > input_message.ts:
            return
        if input_message.body.lower() in ["tchau", "encerrar"]:
            reset_step(self.number)
            message = "Tchau, se precisar de alguma ajuda, conte comigo."
            self.client.send_message(self.number, message)
            return
        if step == 0:
            message = "Olá sou Ypaîó assistente virtual no apoio a saúde.\n"
            self.client.send_message(self.number, message)
            message = "Vou te fazer algumas perguntas para tentar entender qual pode ser seu problema e lhe encaminhar ajuda caso precise."
            self.client.send_message(self.number, message)
            message = "Você também pode me dar tchau para encerrar o atendimento."
            self.client.send_message(self.number, message)
            message = "Por favor, compartilhe a sua localização, ela será útil para o encaminhamento à profissionais de saúde."
            self.client.send_message(self.number, message, "location")
            update_step(self.number, input_message.ts)
        elif step == 1:
            message = "Se não mediu selecione não sei"
            self.client.send_question(
                self.number, "Febre", message, ["Sim", "Não", "Não sei"]
            )
            update_step(self.number, input_message.ts)
        elif step == 2:
            message = "preencha"
            self.client.send_question(
                self.number, "Dor de cabeça", message, ["Sim", "Não"]
            )
            update_step(self.number, input_message.ts)
        else:
            reset_step(self.number)
            message = "Tchau, se precisar de alguma ajuda, conte comigo."
            self.client.send_message(self.number, message)

    @property
    def session(self):
        return get_session(self.number)
