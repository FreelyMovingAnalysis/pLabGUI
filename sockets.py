# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 15:52:07 2020

@author: Timothe
"""

import socket
try:
    import cPickle as pickle
except ImportError:
    import pickle
import hmac
import hashlib

SEND_RECEIVE_CONF= lambda x:x
SEND_RECEIVE_CONF.key="ctv4eys984cavpavt5snldbkrw3"
SEND_RECEIVE_CONF.last_recipient="localhost"
SEND_RECEIVE_CONF.last_port= 23208
SEND_RECEIVE_CONF.hashfunction= hashlib.sha1
SEND_RECEIVE_CONF.hashsize= 160 / 8 #sha1 has 160 bits
SEND_RECEIVE_CONF.magic= b'sendreceive'
SEND_RECEIVE_CONF.buffer= 8192




def _send( obj, host=None, port=None):
    global SEND_RECEIVE_CONF
    SRC= SEND_RECEIVE_CONF
    host= host or SRC.last_recipient
    port= int( port or SRC.last_port)
    SRC.last_recipient= host
    SRC.last_port= port
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.settimeout(2)
    conn.connect( (host, port) )
    serialized= pickle.dumps( obj )
    signature= hmac.new( str.encode(SRC.key), serialized,  SRC.hashfunction).digest()
    assert len(signature)==SRC.hashsize
    print(len(SRC.magic))
    print(len(signature))
    print(len(serialized))
    message= SRC.magic + signature + serialized
    #print(message.decode())
    print(len(message))
    conn.send( message )
    response= conn.recv( SRC.buffer )
    if response!=SRC.magic:
        raise Exception("Bad acknowledge. Check host, port and keys")
    conn.close()

def _receive( timeout=None, port=None ):
    global SEND_RECEIVE_CONF
    SRC= SEND_RECEIVE_CONF
    port= int( port or SRC.last_port)
    SRC.last_port= port
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sk.settimeout( timeout )
    sk.bind(("0.0.0.0", port))
    sk.listen(1)
    try:
        conn, addr = sk.accept()
    except socket.error as e:
        sk.close()
        raise e
    data = conn.recv( SRC.buffer )
    print(len(data))
    if len(data) < len( SEND_RECEIVE_CONF.magic)+SEND_RECEIVE_CONF.hashsize:
        raise Exception("Message received was too small. Ignored")
    if not data.startswith( SRC.magic ):
        conn.close()
        sk.close()
        raise Exception("Wrong magic. We're probably receiving messages from elsewhere")
    i1= len(SRC.magic)
    i2= int( i1+SRC.hashsize )
    signature= data[i1:i2]
    message= data[i2:]
    good_signature= hmac.new( str.encode(SRC.key), message,  SRC.hashfunction).digest()
    if signature!=good_signature:
        conn.close()
        sk.close()
        raise Exception("Bad signature on sent data, implying different keys on sender and receiver")
    conn.send( SRC.magic )
    conn.close()
    sk.close()
    obj= pickle.loads(message)
    return obj

def send( obj, host=None, port=None ):
    #try:
    return _send(obj, host=None, port=None)
    #except Exception as e:
        #print( e )

def receive( timeout=None, port=None  ):
    #try:
    return _receive(timeout=None, port=None )
    #except Exception as e:
        #print( e )


def load_ipython_extension(ip):
    ip.push( {'s':send, 'r':receive} )

def unload_ipython_extension(ip):
    ip.plugin_manager.unregister_plugin('s')
    ip.plugin_manager.unregister_plugin('r')


if __name__=="__main__":
    print("kek")
    value = {"kek":12}
    #value = 12
    print( send( value ) )
    #print( receive(timeout = 30) )