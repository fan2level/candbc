# -*-coding:utf-8-*-

import os,sys
import argparse
from pDBC import *
from graphviz import Digraph
import json

parser = argparse.ArgumentParser()
parser.add_argument('--candb', '-c', required=True, help="candb directory")
parser.add_argument('--ecu', '-e', default="CGW", help="specify ecu")
parser.add_argument('--signal-tx', action='store_true')
parser.add_argument('--signal-rx', action='store_true')
parser.add_argument('--debug', '-d', action='store_true')
args = parser.parse_args()

candb = args.candb
ecu = args.ecu
signal_tx = args.signal_tx
signal_rx = args.signal_rx
_debug = args.debug

if _debug == True:
    print(f"--candb: {candb}")
    print(f"--ecu: {ecu}")
    print(f"--signal-tx : {signal_tx}")
    print(f"--signal-rx : {signal_rx}")

if os.path.exists(candb) == False:
    raise FileNotFoundError()

pdbc = pDBC(candb)
xmldbc = pdbc.toXml()
j = pdbc.toJson()
pj= json.loads(j)

jnode = next((x for x in pj['nodes'] if x.lower() == ecu.lower()), None)
if jnode is None:
    print(f"{ecu} is not exist")
    exit(1)

dot = Digraph(comment="plot candb", format="svg", encoding="utf-8", engine="neato")
dot.attr('graph', overlap='false')
dot.attr('graph', concentrate='true')

dot.attr('node', width='.3', height='.3')
dot.attr('node', shape='box3d', style='filled', fillcolor='salmon')
dot.node(ecu)

messages_tx = [x for x in pj['messages'] if x['transmitter'].lower() == ecu.lower()]
# message tx
for message in messages_tx:
    message_id = message['id']
    message_name = message['name']
    message_size = message['size']

    dot.attr('node', shape='box', style='filled', fillcolor='lightsalmon')
    dot.node(message_name)
    dot.edge(ecu, message_name)

    if signal_tx == True:
        for signal in message['signals']:
            signal_name = signal
            dot.attr('node', shape='box', style='filled', fillcolor='white')
            dot.node(signal_name)
            dot.edge(message_name, signal_name)

# message rx
signals_rx = [x for x in pj['signals'] if ecu.lower() in [y.lower() for y in x['receivers']]]
for signal in signals_rx:
    message = next((x for x in pj['messages'] if [y for y in x['signals'] if y == signal['name']]), None)
    if message is None:
        continue
    message_id = message['id']
    message_name = message['name']
    message_size = message['size']
    node = message['transmitter']
    
    dot.attr('node', shape='box3d', style='filled', fillcolor='blue')
    dot.node(node)
    
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
    dot.node(message_name)
    dot.edge(node, message_name)

    if signal_rx == True:
        signal_name = signal['name']
        dot.attr('node', shape='box', style='filled', fillcolor='white')
        dot.node(signal_name)
        dot.edge(message_name, signal_name)
    
dot.view()
