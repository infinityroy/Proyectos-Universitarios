from ast import Try
import base64
import logging
import sys
import socket
import select
import binascii
import argparse
from flask import Flask, request
app = Flask(__name__)

'''
    Config de Logeo
'''
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('INFO: %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
'''
    Fin de config de Log
'''

parser = argparse.ArgumentParser(description='Api HTTPS para peticiones DNS')

parser.add_argument('custom_server', type=str,
                    help='Usa un servidor DNS remoto diferente')

TEST = False
UDP_IP = "8.8.8.8"
UDP_PORT = 53

@app.route('/api/dns_resolver', methods=["GET", 'POST'])
def dns_resolver():
    #if args.explorador is True:
    #    UDP_IP = 
    base64_bytes = request.data

    logging.info("Encoded: " + base64_bytes.decode('ascii'))
    message_bytes = base64.b64decode(base64_bytes)

    ''' Log message '''
    try:
        message = message_bytes.decode('ascii')
        logging.info("Decoded: " + message)
    except:
        logging.info("Decoded: NOT_ASCII")

    ''' Create socket '''
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if TEST:
        ''' Creo request de testeo - example.com'''
        queryBytes = "AA AA 01 00 00 01 00 00 00 00 00 00 07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"
        queryBytes = queryBytes.replace(" ", "").replace("\n", "")
        ''' Convierto de hexadecimal a byte string '''
        query_message = binascii.unhexlify(queryBytes)
        ''' Envio el request de prueba '''
        opened_socket.sendto(query_message, (UDP_IP, UDP_PORT))
    else:
        opened_socket.sendto(message_bytes, (UDP_IP, UDP_PORT))

    '''
        Habilito bloqueo en el socket y espero por 5 segundos respuesta de google
    '''
    opened_socket.setblocking(0)
    ready = select.select([opened_socket], [], [], 5)
    if ready[0]:
        data, addr = opened_socket.recvfrom(2048)
        data64 = base64.b64encode(data).decode('ascii')
        logging.info("Response: " + data64 + "{" + str(len(data)) + "}")
        return data64
    
if __name__ == '__main__':
    args = parser.parse_args()
    UDP_IP=args.custom_server
    logging.info("DNS Remote Server: " + str(UDP_IP))
        
    app.run(host='0.0.0.0', port=443, ssl_context='adhoc')