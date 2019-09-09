# coding=utf-8
from smartcard.CardConnectionObserver import CardConnectionObserver
from smartcard.util import toHexString

from Utils.Convert import convert_int_2_hex_str
from Utils.EMVValues.CommandMap import command_map
from Utils.EMVValues.ResponseMap import response_map


class ConnectionObserverWrapper(CardConnectionObserver):
    """This observer will interpret some APDU commands
    and replace them with a human readable string."""

    def __init__(self):
        self.handleMap = {'connect': self.on_connect,
                          'disconnect': self.on_disconnect,
                          'command': self.on_command,
                          'response': self.on_response}
        super(ConnectionObserverWrapper, self).__init__()

    @staticmethod
    def on_connect(card_connection, _):
        print('connecting to ' + card_connection.getReader())

    @staticmethod
    def on_disconnect(card_connection, _):
        print('disconnecting from ' + card_connection.getReader())

    @staticmethod
    def on_command(_, ccevent):
        str_ = toHexString(ccevent.args[0])
        command = toHexString(ccevent.args[0])[0:5]
        try:
            print('*' * 100)
            print(command_map[command])
        except KeyError:
            print(f'Undefined command "{command}"')
        print('>', str_)

    @staticmethod
    def on_response(_, ccevent):
        response_meaning = ''
        try:
            hex_result = convert_int_2_hex_str(ccevent.args[-2:][0])
            response_meaning = response_map[hex_result]
        except KeyError:
            pass
        print('<',
              toHexString(ccevent.args[0]),
              ' | ',
              'SW: ' + toHexString(ccevent.args[-2:]),
              ' | ',
              response_meaning
              )

    def update(self, card_connection, ccevent):
        callback = self.handleMap[ccevent.type]
        callback(card_connection, ccevent)
