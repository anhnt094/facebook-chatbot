import sys
import time
import yaml

from datetime import datetime

from dateutil import parser
from fbchat import Client
from fbchat.models import Message, ThreadType, FBchatException


def get_credentials():
    with open('/home/tuananh/credentials.yaml') as stream:
        data = yaml.load(stream)
        return data['email'], data['password']


class Bot(Client):
    old_senders = []

    def onMessage(self, message_object, author_id,
                  thread_id, thread_type, **kwargs):
        '''
        Called when listen, and somebody (including yourself) send a message.
        '''
        sender_info = self.fetchUserInfo(thread_id)
        sender_name = str(sender_info[thread_id])[6:-19]

        # Print message
        if author_id != self.uid:
            if message_object.attachments:
                print('New message from {}:\n{}\nattachments={}'
                      .format(sender_name, message_object.text,
                              message_object.attachments))
            else:
                print('New message from {}:\n{}'.format(sender_name,
                                                        message_object.text))

        # Reply to the message if it was sent in working hours
        now = datetime.now()

        morning_start = parser.parse("08:00:00")
        morning_end = parser.parse("12:00:00")

        afternoon_start = parser.parse("13:30:00")
        afternoon_end = parser.parse("17:30:00")

        reply_message = 'Tôi đang bận. Tôi sẽ trả lời tin nhắn của bạn sau. '\
                        'Nếu có việc quan trọng, vui lòng liên hệ với tôi ' \
                        'qua số điện thoại 0962126964. Xin cảm ơn!\n' \
                        'I\'m busy. I will reply to your message later. ' \
                        'If there are important things, please contact me ' \
                        'at 0962126964. Thank you!'
        if thread_type == ThreadType.USER:
            if (now > morning_start and now < morning_end) \
                    or (now > afternoon_start and now < afternoon_end):
                # If sender is not me, and sender sent message first time
                if author_id != self.uid \
                        and author_id not in self.old_senders:
                    self.old_senders.append(author_id)
                    time.sleep(2)
                    self.send(Message(text=reply_message),
                              thread_id=author_id,
                              thread_type=thread_type)


def main():
    email, password = get_credentials()

    while True:
        try:
            my_bot = Bot(email, password)
            my_bot.listen()
        except FBchatException.FBchatUserError:
            print('Invalid username or password / Or 2FA Fail')
            sys.exit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
