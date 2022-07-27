
from channels.generic.websocket import WebsocketConsumer
import json
from api.models import ChatMessage
from api.serializers import ChatMessageDeserializer, ChatMessageSerializer


def sendMessage(data):
    ser = ChatMessageDeserializer(data=data)
    ser.is_valid(True)
    m: ChatMessage = ser.save()
    m.toUser_id = m.fromUser_id
    if m.toUser_id in ChatConsumer.instances:
        friendChannel: ChatConsumer = ChatConsumer.instances[m.toUser_id]
        mser = ChatMessageSerializer(m)
        friendChannel.send({
            'type': 'message',
            'message': mser.data,
            'from': m.fromUser_id
        })


class ChatConsumer(WebsocketConsumer):
    instances = {}
    user = None

    def connect(self):
        self.user = self.scope['user']

        # ensure user is valid
        if self.user.is_anonymous:
            # refuse unknown connections
            self.close()

        ChatConsumer.instances[self.user.chatuser.id] = self

        # accept connection
        self.accept()

    def disconnect(self, code):
        del ChatConsumer.instances[self.user.chatuser.id]

    def send(self, text_data=None, bytes_data=None, close=False):
        return super().send(json.dumps(text_data), bytes_data, close)

    def receive(self, text_data=None):
        # get the connected user
        user = self.scope['user']

        # load the sent data
        req = json.loads(text_data)

        # check request type
        if ('type' in req and req['type'] == 'send'):
            # set the message source
            req['fromUser'] = user.chatuser.id

            try:
                # try send the message
                sendMessage(req)

                # on success return a success message
                self.send({
                    'id': req['id'],
                    'success': True
                })
            except Exception as ex:
                # on error return an error message
                self.send({
                    'id': req['id'],
                    'success': False,
                    'reason': 'MESSAGE_NOT_SENT'
                })
        else:
            # if type is unknown the nreturn an error
            self.send({
                'id': req['id'],
                'success': False,
                'reason': 'UNKNOWN_REQUEST'
            })
