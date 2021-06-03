# -*-coding:utf-8-*-
import __future__
import os
import sys
import re

class fileDBC(object):
    """ .dbc file format
    DBC file format
    DBC_file = 
    version
    new_symbols
    bit_timing (*obsolete but required*)
    nodes
    value_tables
    messages
    message_transmitters
    environment_variables
    environment_variables_data
    signal_types
    comments
    attribute_definitions
    sigtype_attr_list
    attribute_defaults
    attribute_values
    value_descriptions
    category_definitions (*obsolete*)
    categories (*obsolete*)
    filter (*obsolete*)
    signal_type_refs
    signal_groups
    signal_extended_value_type_list
    """
    def __init__(self, filedbc, encoding='utf-8'):
        self.__file = filedbc
        self.__encoding = encoding
        self.__contents = ''
 
        if os.path.exists(filedbc) == False:
            raise('{0} is not exist'.format(filedbc))
        
        with open(filedbc, 'r', encoding=encoding) as d:
            self.__contents = d.read()

            self.__version = ''
            # version = ['VERSION' '"' { CANdb_version_string } '"' ];
            pattern_version = re.compile('(?P<version0>VERSION) \"(?P<version>\w+)\"')
            matchobj = pattern_version.search(self.contents)
            if matchobj is not None:
                version = matchobj.group('version')
                self.__version = version

            self.__new_symbols = list()
            # new_symbols = [ '_NS' ':' ['CM_'] ['BA_DEF_'] ['BA_'] ['VAL_']
            # ['CAT_DEF_'] ['CAT_'] ['FILTER'] ['BA_DEF_DEF_'] ['EV_DATA_']
            # ['ENVVAR_DATA_'] ['SGTYPE_'] ['SGTYPE_VAL_'] ['BA_DEF_SGTYPE_']
            # ['BA_SGTYPE_'] ['SIG_TYPE_REF_'] ['VAL_TABLE_'] ['SIG_GROUP_']
            # ['SIG_VALTYPE_'] ['SIGTYPE_VALTYPE_'] ['BO_TX_BU_']
            # ['BA_DEF_REL_'] ['BA_REL_'] ['BA_DEF_DEF_REL_'] ['BU_SG_REL_']
            # ['BU_EV_REL_'] ['BU_BO_REL_'] ];
            pattern_new_symbols = re.compile('(?P<new_symbols0>NS_)\s*:\s*\n(?P<new_symbols>.*)\nBS_', re.S)
            matchobj = pattern_new_symbols.search(self.contents)
            if matchobj is not None:
                new_symbols = matchobj.group('new_symbols')
                new_symbols = new_symbols.strip()
                new_symbols = re.sub('\s+', ' ', new_symbols)
                self.__new_symbols = re.split('\s+', new_symbols)

            self.__bit_timing = None

            self.__nodes = list()
            # nodes = 'BU_:' {node_name} ;
            # node_name = C_identifier ;
            pattern_nodes = re.compile('(?P<nodes0>BU_): (?P<nodes>.*)', re.M)
            matchobj = pattern_nodes.search(self.contents)
            if matchobj is not None:
                nodes = matchobj.group('nodes')
                self.__nodes = re.split('\s+', nodes)

            self.__value_tables = list()
            
            self.__messages = list()
            # messages = {message} ;
            # message = BO_ message_id message_name ':' message_size transmitter {signal} ;
            # message_id = unsigned_integer ;
            pattern_messages = re.compile('(?P<messages0>BO_) (?P<message_id>\d+) (?P<message_name>\w+): (?P<message_size>\d+) (?P<transmitter>\w+)\s+(?P<signal>SG_ .+?\n\n)', re.M|re.S)
            for matchobj in pattern_messages.finditer(self.contents):
                messages = matchobj.group('messages0')
                message_id = matchobj.group('message_id')
                message_name = matchobj.group('message_name')
                message_size = matchobj.group('message_size')
                transmitter = matchobj.group('transmitter')
                signal = matchobj.group('signal')
                signalx = list()

                # signal = 'SG_' signal_name multiplexer_indicator ':' start_bit '|' signal_size '@' byte_order value_type '(' factor ',' offset ')' '[' minimum '|' maximum ']' unit receiver {',' receiver} ;
                # signal_name = C_identifier ;
                # multiplexer_indicator = ' ' | 'M' | m multiplexer_switch_value ;
                # multiplexer_switch_value = unsigned_integer
                # start_bit = unsigned_integer ;
                # signal_size = unsigned_integer ;
                # byte_order = '0' | '1' ; (* 0=little endian, 1=big endian *)
                # value_type = '+' | '-' ; (* +=unsigned, -=signed *)
                # factor = double ;
                # offset = double ;
                # physical_value = raw_value * factor + offset
                # raw_value = (physical_value – offset) / factor
                # minimum = double ;
                # maximum = double ;
                # unit = char_string ;
                # receiver = node_name | 'Vector__XXX' ;
                pattern_signal = re.compile('SG_ (?P<signal_name>[\w]+)\s+(?P<multiplexer_indicator>''|M|m\d?)\s*:\s*(?P<start_bit>\d+)\|(?P<signal_size>\d+)@(?P<byte_order>[01])(?P<value_type>[+-])\s+\((?P<factor_offset>.+)\)\s+\[(?P<minimum_maximum>.+)\]\s+\"(?P<unit>.*)\"\s+(?P<receiver>[\w,]+)', re.M)
                # m = pattern_signal.match(signal)
                for m in pattern_signal.finditer(signal):
                # if m:
                    signal_name = m.group('signal_name')
                    multiplexer_indicator = m.group('multiplexer_indicator')
                    start_bit = m.group('start_bit')
                    signal_size = m.group('signal_size')
                    byte_order = m.group('byte_order')
                    value_type = m.group('value_type')
                    factor_offset = m.group('factor_offset')
                    factor, offset = factor_offset.split(',')
                    minimum_maximum = m.group('minimum_maximum') # fixme:
                    minimum, maximum = minimum_maximum.split('|')
                    unit = m.group('unit')
                    receiver = m.group('receiver')
                    receivers = receiver.split(',')

                    # print('{0} {1} : {2}|{3}@{4}{5} ({6},{7}) [{8}|{9}] "{10}" {11}'.format(signal_name, multiplexer_indicator, start_bit, signal_size, byte_order, value_type, factor, offset, minimum, maximum, unit, receiver))
                    signal0 = {'signal_name':signal_name,
                               'multiplexer_indicator':multiplexer_indicator,
                               'start_bit':start_bit,
                               'signal_size':signal_size,
                               'byte_order':byte_order,
                               'value_type':value_type,
                               'factor':factor, 'offset':offset,
                               'minimum':minimum, 'maximum':maximum,
                               'unit':unit,
                               'receiver':receivers}
                    signalx.append(signal0)
                    
                
                message = {'message_id':message_id, 'message_name':message_name, 'message_size':message_size, 'transmitter':transmitter, 'signal':signalx}
                self.__messages.append(message)

            self.__message_transmitters = None
            # message_transmitters = {message_transmitter} ;
            # Message_transmitter = 'BO_TX_BU_' message_id ':' {transmitter} ';' ;

            self.__environment_variables = None
            # environment_variables

            self.__environment_variables_data = None
            # environment_variables_data

            self.__signal_types = None
            # signal_types

            self.__comments = list()
            #ex)CM_ BO_ 137 "[EC] On Event and On Change";
            # comments = {comment} ;
            # comment = 'CM_' (char_string |
            #                  'BU_' node_name char_string |
            #                  'BO_' message_id char_string |
            #                  'SG_' message_id signal_name char_string |
            #                  'EV_' env_var_name char_string)
            # ';' ;
            pattern_comments0 = re.compile('^CM_\s+(?P<comment>.*?\")\s*;', re.S|re.M)
            for m in pattern_comments0.finditer(self.contents):
                comment = m.group('comment')
                # print('<<', comment, '>>')
                pattern_comments = re.compile('((BU_)\s+(\w+)|(BO_)\s+(\d+)|(SG_)\s+(\d+)\s+(\w+)|(EV_)\s+(\w+))\s+(?P<char_string>\".*\")', re.S)
                n = pattern_comments.match(comment)
                if n:
                    # print('  matched  ', n.group(2), n.group(3), n.group(4))
                    signature = None
                    node_name = None
                    message_id = None
                    signal_name = None
                    env_var_name = None
                    char_string = n.group('char_string')
                    if n.group(2) == 'BU_':
                        signature = n.group(2)
                        node_name = n.group(3)
                        c = {'signature':signature, 'node_name':node_name, 'char_string':char_string}
                        self.comments.append(c)
                    elif n.group(4) == 'BO_':
                        signature = n.group(4)
                        message_id = n.group(5)
                        c = {'signature':signature, 'message_id':message_id, 'char_string':char_string}
                        self.comments.append(c)
                    elif n.group(6) == 'SG_':
                        signature = n.group(6)
                        message_id= n.group(7)
                        signal_name = n.group(8)
                        c = {'signature':signature, 'message_id':message_id, 'signal_name':signal_name, 'char_string':char_string}
                        self.comments.append(c)
                    elif n.group(9) == 'EV_':
                        signature = n.group(9)
                        env_var_name = n.group(10)
                        c = {'signature':signature, 'env_var_name':env_var_name, 'char_string':char_string}
                        self.comments.append(c)
                else:
                    print('  xxx {0}'.format(comment))

            #fixme:
            self.__attribute_definitions = list()
            # attribute_definitions = { attribute_definition } ;
            # attribute_definition = 'BA_DEF_' object_type attribute_name attribute_value_type ';' ;
            # object_type = '' | 'BU_' | 'BO_' | 'SG_' | 'EV_' ;
            # attribute_name = '"' C_identifier '"' ;
            # attribute_value_type = 'INT' signed_integer signed_integer | 'HEX' signed_integer signed_integer | 'FLOAT' double double | 'STRING' | 'ENUM' [char_string {',' char_string}]
            pattern_attribute_definitions = re.compile('(?P<attribute_definitions0>BA_DEF_)(?P<object_type>\s+|\s+BU_\s+|\s+BO_\s+|\s+SG_\s+|\s+EV_\s+)\"(?P<attribute_name>[-\w]+)\" (?P<attribute_value_type>.*)', re.M)
            for m in pattern_attribute_definitions.finditer(self.contents):
                attribute_definitions = m.group('attribute_definitions0')
                object_type = m.group('object_type')
                attribute_name = m.group('attribute_name')
                attribute_value_type = m.group('attribute_value_type')
                self.__attribute_definitions.append({'object_type':object_type, 'attribute_name':attribute_name, 'attribute_value_type':attribute_value_type})

            self.__attribute_definitions2 = list()
            # BA_DEF_REL_
            # BA_DEF_REL_ BU_SG_REL_  "GenSigTimeoutMsg" HEX 0 2047;
            pattern_attribute_definitions2 = re.compile('(BA_DEF_REL_)\s+(?P<message_rel>\w+)\s+\"(?P<message_name>\w+)\"\s+(\w+)\s+(\w+)\s+(\w+)\s*;')
            for m in pattern_attribute_definitions2.finditer(self.contents):
                signature = m.group(1)
                message_rel = m.group('message_rel')
                message_name = m.group('message_name')
                attribute_definitions2_4 = m.group(4)
                attribute_definitions2_5 = m.group(5)
                attribute_definitions2_6 = m.group(6)
                self.__attribute_definitions2.append({'message_rel':message_rel,
                                                      'message_name':message_name,
                                                      '4':attribute_definitions2_4,
                                                      '5':attribute_definitions2_5,
                                                      '6':attribute_definitions2_6})
                
            self.__sigtype_attr_list = None
            # sigtype_attr_list

            self.__attribute_defaults = list()
            # attribute_defaults = { attribute_default } ;
            # attribute_default = 'BA_DEF_DEF_' attribute_name attribute_value ';' ;
            # attribute_name = '"' C_identifier '"' ;
            # attribute_value = unsigned_integer | signed_integer | double | char_string ;
            pattern_attribute_defaults = re.compile('(?P<attribute_defaults0>BA_DEF_DEF_)(?P<attribute_name>\s+|\s+\w+\s+)(?P<attribute_value>\d+|.*)\s*;' , re.M)
            for matchobj in pattern_attribute_defaults.finditer(self.contents):
                attribute_defaults = matchobj.group('attribute_defaults0')
                attribute_name = matchobj.group('attribute_name')
                attribute_value = matchobj.group('attribute_value')
                attribute_default = {'attribute_name':attribute_name, 'attribute_value':attribute_value}
                self.__attribute_defaults.append(attribute_default)

            self.__attribute_defaults2 = list()
            # BA_DEF_DEF_REL_
            # BA_DEF_DEF_REL_ "GenSigTimeoutMsg" 0;
            pattern_attribute_defaults2 = re.compile('(BA_DEF_DEF_REL_)\s+\"(?P<message_name>\w+)\"\s+(\w+)\s*;')
            for m in pattern_attribute_defaults2.finditer(self.contents):
                signature = m.group(1)
                message_name = m.group('message_name')
                attribute_default2_3 = m.group(3)
                # print(f'{signature} {message_name} {attribute_default2_3}')
                self.__attribute_defaults2.append({'message_name':message_name,
                                                   '3':attribute_default2_3})

            self.__attribute_values = list()
            # attribute_values = { attribute_value_for_object } ;
            # attribute_value_for_object = 'BA_' attribute_name (attribute_value |'BU_' node_name attribute_value |
                                                               # 'BO_' message_id attribute_value |
                                                               # 'SG_' message_id signal_name attribute_value |
                                                               # 'EV_' env_var_name attribute_value) ';' ;
            # attribute_value = unsigned_integer | signed_integer | double | char_string ;
            pattern_attribute_values = re.compile('(?P<attribute_values0>BA_)\s+\"(?P<attribute_name>[\w-]+)\"\s+(?P<attribute_value>.*|\".*\")\s*;', re.M)
            for matchobj in pattern_attribute_values.finditer(self.contents):
                attribute_values0 = matchobj.group('attribute_values0')
                attribute_name = matchobj.group('attribute_name')
                attribute_value0 = matchobj.group('attribute_value')
                attribute = {'attribute_name':attribute_name, 'attribute_value':None}
                pattern_attribute_value1 = re.compile('([\d.-]+|\"[\w .]+\")')
                pattern_attribute_value2 = re.compile('BU_\s+(?P<node_name>\w+)\s(?P<attribute_value>[-\w.]+|\".*\")')
                pattern_attribute_value3 = re.compile('BO_\s+(?P<message_id>\w+)\s(?P<attribute_value>[-\w.]+|\".*\")')
                pattern_attribute_value4 = re.compile('SG_\s+(?P<message_id>\w+)\s(?P<signal_name>\w+)\s+(?P<attribute_value>[-\w.]+|\".*\")')
                pattern_attribute_value5 = re.compile('EV_\s+(?P<env_var_name>\w+)\s(?P<attribute_value>[-\w.]+|\".*\")')
                m = pattern_attribute_value1.match(attribute_value0)
                if m:
                    attribute['attribute_value'] = {'signature':None, 'attribute_value':m.group(1)}
                else:
                    m = pattern_attribute_value2.match(attribute_value0)
                    if m:
                        node_name = m.group('node_name')
                        attribute_value = m.group('attribute_value')
                        # print(node_name, attribute_value)
                        attribute['attribute_value'] = {'signature':'BU_', 'node_name':node_name, 'attribute_value':attribute_value}
                    else:
                        m = pattern_attribute_value3.match(attribute_value0)
                        if m:
                            message_id = m.group('message_id')
                            attribute_value = m.group('attribute_value')
                            # print(message_id, attribute_value)
                            attribute['attribute_value'] = {'signature':'BO_', 'message_id':message_id, 'attribute_value':attribute_value}
                        else:
                            m = pattern_attribute_value4.match(attribute_value0)
                            if m:
                                message_id = m.group('message_id')
                                signal_name = m.group('signal_name')
                                attribute_value = m.group('attribute_value')
                                # print(message_id, signal_name, attribute_value)
                                attribute['attribute_value'] = {'signature':'SG_', 'message_id':message_id, 'signal_name':signal_name, 'attribute_value':attribute_value}
                            else:
                                m = pattern_attribute_value5.match(attribute_value0)
                                if m:
                                    env_var_name = m.group('env_var_name')
                                    attribute_value = m.group('attribute_value')
                                    # print(env_var_name, attribute_value)
                                    attribute['attribute_value'] = {'signature':'EV_', 'env_var_name':env_var_name, 'attribute_value':attribute_value}
                                else:
                                    print('  xxx {0} {1}'.format(attribute_name, attribute_value0))
                                    continue
                self.__attribute_values.append(attribute)

            # checkme: format
            self.__attribute_values2 = list()
            # BA_REL_ "GenSigTimeoutTime" BU_SG_REL_ CLU SG_ 1345 CF_Gway_PassiveAccessUnlock 1500;
            pattern_attribute_values2 = re.compile('(BA_REL_)\s+\"(?P<message_name>\w*)\"\s+(?P<message_rel>\w+)\s+(?P<ecu>\w+)\s+(?P<message_id>\w+)\s+(\w+)\s+(?P<signal>\w+)\s+(\w+)\s*')
            for m in pattern_attribute_values2.finditer(self.contents):
                # print(m.group(0))
                signature = m.group(1)
                message_name = m.group('message_name')
                message_rel = m.group('message_rel')
                ecu = m.group('ecu')
                message_id = m.group('message_id')
                attribute_values2_6 = m.group(6)
                signal = m.group('signal')
                attribute_values2_8 = m.group(8)
                self.__attribute_values2.append({'message_name':message_name,
                                                 'message_rel':message_rel,
                                                 'ecu':ecu,
                                                 'message_id':message_id,
                                                 '6':attribute_values2_6,
                                                 'signal':signal,
                                                 '8':attribute_values2_8})
                
            self.__value_descriptions = list()
            # value_descriptions = { value_descriptions_for_signal | value_descriptions_for_env_var } ;
            # value_descriptions_for_signal = 'VAL_' message_id signal_name { value_description } ';' ;
            pattern_value_descriptions = re.compile('(?P<value_descriptions0>VAL_) (?P<message_id>\w+) (?P<signal_name>\w+) (?P<value_description>.*) ;')
            for matchobj in pattern_value_descriptions.finditer(self.contents):
                value_descriptions = matchobj.group('value_descriptions0')
                message_id = matchobj.group('message_id')
                signal_name = matchobj.group('signal_name')
                value_description = matchobj.group('value_description')
                self.__value_descriptions.append({'message_id':message_id, 'signal_name':signal_name, 'value_description':value_description})

            self.__category_definitions = None
            # category_definitions (*obsolete*)

            self.__categories = None
            # categories (*obsolete*)

            self.__filters = None
            # filter (*obsolete*)

            self.__signal_type_refs = None

            self.__signal_groups = None

            self.__signal_extended_value_type_list = None

    @property
    def contents(self):
        return self.__contents

    @property
    def version(self):
        return self.__version

    @property
    def new_symbols(self):
        return self.__new_symbols

    @property
    def bit_timing(self):
        return self.__bit_timing

    @property
    def nodes(self):
        return self.__nodes

    @property
    def messages(self):
        return self.__messages

    @property
    def message_transmitters(self):
        return self.__message_transmitters

    @property
    def environment_variables(self):
        return self.__environment_variables

    @property
    def envronment_variables_data(self):
        return self.__environment_variables_data

    @property
    def signal_types(self):
        return self.__signal_types

    @property
    def comments(self):
        return self.__comments

    @property
    def attribute_definitions(self):
        return self.__attribute_definitions
    
    @property
    def attribute_definitions2(self):
        return self.__attribute_definitions2

    @property
    def sigtype_attr_list(self):
        return self.__sigtype_attr_list

    @property
    def attribute_defaults(self):
        return self.__attribute_defaults

    @property
    def attribute_defaults2(self):
        return self.__attribute_defaults2

    @property
    def attribute_values(self):
        return self.__attribute_values

    @property
    def attribute_values2(self):
        return self.__attribute_values2
    
    @property
    def value_descriptions(self):
        return self.__value_descriptions

    @property
    def category_definitions(self):
        return self.__category_definitions

    @property
    def categories(self):
        return self.__categories

    @property
    def filters(self):
        return self.__filters

    @property
    def signal_type_refs(self):
        return self.__signal_type_refs

    @property
    def signal_groups(self):
        return self.__signal_groups

    @property
    def signal_extended_value_type_list(self):
        return self.__signal_extended_value_type_list

    def duplicate(self, output=None):
        """ duplicate dbc file using parsed data
        """
        if output is None:
            # print('file: {0}'.format(self.__file))
            output = os.path.splitext(self.__file)[0] + '.duplicate' + os.path.splitext(self.__file)[1]
        with open(output, mode='w', encoding=self.__encoding) as f:
            print('VERSION "{0}"'.format(self.version), file=f)
            print(file=f)
            print(file=f)
            print('NS_ : ', file=f)
            for symbol in self.new_symbols:
                print('\t{0}'.format(symbol), file=f)
            print(file=f)
            print('BS_:', file=f)
            print(file=f)
            nodes = 'BU_: '
            nodes = nodes + ' '.join(self.nodes)
            print(nodes, file=f)
            print(file=f)
            print(file=f)
            for message in self.messages:
                print('BO_ {0} {1}: {2} {3}'.format(message['message_id'],
                                                    message['message_name'],
                                                    message['message_size'],
                                                    message['transmitter']), file=f)
                for signal in message['signal']:
                    if signal['multiplexer_indicator'] == '':
                        print(' SG_ {0} : {1}|{2}@{3}{4} ({5},{6}) [{7}|{8}] "{9}"  {10}'.format(signal['signal_name'],
                                                                                                 signal['start_bit'],
                                                                                                 signal['signal_size'],
                                                                                                 signal['byte_order'],
                                                                                                 signal['value_type'],
                                                                                                 signal['factor'],
                                                                                                 signal['offset'],
                                                                                                 signal['minimum'],
                                                                                                 signal['maximum'],
                                                                                                 signal['unit'],
                                                                                                 ','.join(signal['receiver'])), file=f)
                    else:
                        print(' SG_ {0} {1} : {2}|{3}@{4}{5} ({6},{7}) [{8}|{9}] "{10}"  {11}'.format(signal['signal_name'],
                                                                                                      signal['multiplexer_indicator'],
                                                                                                      signal['start_bit'],
                                                                                                      signal['signal_size'],
                                                                                                      signal['byte_order'],
                                                                                                      signal['value_type'],
                                                                                                      signal['factor'],
                                                                                                      signal['offset'],
                                                                                                      signal['minimum'],
                                                                                                      signal['maximum'],
                                                                                                      signal['unit'],
                                                                                                      ','.join(signal['receiver'])), file=f)
                print(file=f)
            print(file=f)
            print(file=f)
            
            for comment in self.comments:
                signature = comment['signature']
                char_string = comment['char_string']
                if 'BU_' == signature:
                    print(f"CM_ {signature} {comment['node_name']} {char_string};", file=f)
                elif 'BO_' == signature:
                    print(f"CM_ {signature} {comment['message_id']} {char_string};", file=f)
                elif 'SG_' == signature:
                    print(f"CM_ {signature} {comment['message_id']} {comment['signal_name']} {char_string};", file=f)
                elif 'EV_' == signature:
                    print(f"CM_ {signature} {comment['env_var_name']} {char_string};", file=f)
                else:
                    print(f"CM_ {signature} {char_string};", file=f)
                    
            for attribute_definition in self.attribute_definitions:
                if attribute_definition['object_type'] == '':
                    print('BA_DEF_  "{0}" {1}'.format(attribute_definition['attribute_name'],
                                                      attribute_definition['attribute_value_type']), file=f)
                else:
                    print('BA_DEF_ {0}  "{1}" {2}'.format(attribute_definition['object_type'],
                                                          attribute_definition['attribute_name'],
                                                          attribute_definition['attribute_value_type']), file=f)
            # fixme:BA_DEF_REL_
            for attribute_definition in self.attribute_definitions2:
                message_name = '"{0}"'.format(attribute_definition['message_name'])
                print(f"BA_DEF_REL_ {attribute_definition['message_rel']} {message_name} {attribute_definition['4']} {attribute_definition['5']} {attribute_definition['6']};", file=f)
    
            for attribute_default in self.attribute_defaults:
                print('BA_DEF_DEF_  {0} {1};'.format(attribute_default['attribute_name'],
                                                     attribute_default['attribute_value']), file=f)

            # checkme:BA_DEF_DEF_REL
            for attribute_default in self.attribute_defaults2:
                print(f"BA_DEF_DEF_REL_ \"{attribute_default['message_name']}\" {attribute_default['3']};", file=f)
    
            for attribute_value in self.attribute_values:
                attribute_name = attribute_value['attribute_name']
                value = attribute_value['attribute_value']
                if value['signature'] is None:
                    print('BA_ "{0}" {1};'.format(attribute_name,
                                                  value['attribute_value']), file=f)
                elif value['signature'] == 'BU_':
                    print('BA_ "{0}" {1} {2} {3};'.format(attribute_name,
                                                          value['signature'],
                                                          value['node_name'],
                                                          value['attribute_value']), file=f)
                elif value['signature'] == 'BO_':
                    print('BA_ "{0}" {1} {2} {3};'.format(attribute_name,
                                                          value['signature'],
                                                          value['message_id'],
                                                          value['attribute_value']), file=f)
                elif value['signature'] == 'SG_':
                    print('BA_ "{0}" {1} {2} {3} {4};'.format(attribute_name,
                                                              value['signature'],
                                                              value['message_id'],
                                                              value['signal_name'],
                                                              value['attribute_value']), file=f)
                elif value['signature'] == 'EV_':
                    print('BA_ "{0}" {1} {2} {3};'.format(attribute_name,
                                                          value['signature'],
                                                          value['env_var_name'],
                                                          value['attribute_value']), file=f)

            # checkme:BA_REL_
            for attribute_value in self.attribute_values2:
                # print(attribute_value)
                message_name = attribute_value['message_name']
                message_rel = attribute_value['message_rel']
                ecu = attribute_value['ecu']
                message_id = attribute_value['message_id']
                attribute_values2_6 = attribute_value['6']
                signal = attribute_value['signal']
                attribute_values2_8 = attribute_value['8']
                print(f'BA_REL_ "{message_name}" {message_rel} {ecu} {message_id} {attribute_values2_6} {signal} {attribute_values2_8};', file=f)
            
    
            for value_description in self.value_descriptions:
                print('VAL_ {0} {1} {2} ;'.format(value_description['message_id'],
                                                  value_description['signal_name'],
                                                  value_description['value_description']), file=f)

            print(file=f)
    
if __name__ == '__main__':
    # 사용법
    # # dbc = fileDBC(u'./sample/20190212_AI3_2019_바디_1.4(고속).dbc', encoding='euc-kr')
    # dbc = fileDBC(u'sample/20201224_SU2r_2021_Body(고속)_v0.5_R1.dbc', encoding='euc-kr')
    f = 'd.dbc'
    # dbc = fileDBC(f, 'euc-kr')
    # dbc.duplicate()
    # exit(0)
    os.makedirs('duplicate', exist_ok=True)
    for folder, sub, files in os.walk('./sample'):
        for file in files:
            i = os.path.join(folder, file)
            print('file: {0}'.format(i))
            try:
                dbc = fileDBC(i)
            except UnicodeDecodeError as e:
                dbc = fileDBC(i, encoding='euc-kr')
            dbc.duplicate(output=os.path.join('duplicate', file))
    
    print('done')
