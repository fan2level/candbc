# -*-coding:utf-8-*-
# parse .dbc file format
# 
# v0.1 ... no validation, only parse

import __future__
import os
import sys
import re

class fileDBC(object):
    """
    """
    def __init__(self, filedbc, encoding='utf-8'):
        self.__file = filedbc
        self.__encoding = encoding

        if os.path.exists(filedbc) != True:
            raise('{0} is not exist'.format(filedbc))
        
        with open(filedbc, 'r', encoding=encoding) as d:
            self.__contents = d.read()

            self.__version = ''
            # version = ['VERSION' '"' { CANdb_version_string } '"' ];
            pt_version = re.compile('(?P<signature>VERSION) \"(?P<version>.*)\"')
            m = pt_version.search(self.__contents)
            if m is not None:
                self.__version = {'signature':m.group('signature'),
                                  'version':m.group('version')}

            self.__new_symbols = list()
            pt_new_symbols = re.compile('(?P<signature>NS_)\s+:(?P<new_symbols>.+?)\n\n', re.M|re.S)
            m = pt_new_symbols.search(self.contents)
            if m is not None:
                new_symbols = m.group('new_symbols')
                new_symbols = re.sub('\s+', ' ', new_symbols)
                new_symbols = new_symbols.strip()
                self.__new_symbols = {'signature':m.group('signature'),
                                      'new_symbols':new_symbols.split(' ')}
            
            self.__bit_timing = None
                
            self.__nodes = list()
            # nodes = 'BU_:' {node_name} ;
            # node_name = C_identifier ;
            pt_nodes = re.compile('(?P<signature>BU_:)\s+(?P<node_names>.*)', re.M)
            m = pt_nodes.search(self.contents)
            if m is not None:
                node_name = m.group('node_names')
                node_name = node_name.strip()
                self.__nodes = {'signature':m.group('signature'),
                                'node_names':node_name.split(' ')}
            
            self.__value_tables = list()
            pt_value_tables = re.compile('(?P<signature>VAL_TABLE_)\s+(?P<value_table_name>\w+)(?P<value_description>.+?)\s*;', re.M)
            pt_value_description =re.compile('(?P<value>[\d.-]+)\s+\"(?P<description>[\w_\s]+)\"')
            for m in pt_value_tables.finditer(self.contents):
                value_table_name = m.group('value_table_name')
                value_description = m.group('value_description')
                value_table = {'signature':m.group('signature'),
                               'value_table_name':value_table_name,
                               'value_description':list()}
                for n in pt_value_description.finditer(value_description):
                    value = n.group('value')
                    description = n.group('description')
                    value_table['value_description'].append({'value':value, 'description':description})
                self.__value_tables.append(value_table)
            
            self.__messages = None
            self.__message_transmitters = None
            self.__environment_variables = None
            self.__environment_variables_data = None
            self.__signal_types = None

            self.__comments = list()
            pt_comments = re.compile('(?P<signature>CM_)\s+(|BU_\s+(?P<bu>[\w_\d]+)|BO_\s+(?P<bo>[\w_\d]+)|SG_\s+(?P<sg>[\w_\d]+)\s+(?P<sg1>[\w_]+)|EV_\s+(?P<ev>[\w_\d]+))\s+\"(?P<char_string>.+?)\";', re.M|re.S)
            for m in pt_comments.finditer(self.contents):
                comment = {'signature':m.group('signature'),
                           'bu_node_name':m.group('bu'),
                           'bo_message_id':m.group('bo'),
                           'sg_message_id':m.group('sg'),
                           'sg_signal_name':m.group('sg1'),
                           'ev_var_name':m.group('ev'),
                           'char_string':m.group('char_string')}
                self.__comments.append(comment)
            
            self.__attribute_definitions = None
            self.__attribute_defaults = None
            self.__attribute_values = None
            self.__value_descriptions = None
            self.__category_definitions = None
            self.__categories = None
            self.__filter = None
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
    def value_tables(self):
        return self.__value_tables

    @property
    def comments(self):
        return self.__comments

    def duplicate(self, output=''):
        """ duplicate dbc file using parsed data
        """
        if os.path.exists(output) == False:
            output = self.__file
        output = os.path.splitext(output)[0] + '.duplicate' + os.path.splitext(output)[1]
        with open(output, mode='w', encoding=self.__encoding) as f:
            pass

if __name__ == '__main__':

    dbc = fileDBC('sample.dbc')
    # print(dbc.version['signature'])
    # print(dbc.new_symbols['signature'])
    # print(dbc.nodes['signature'])
    
    # for value_table in dbc.value_tables:
    #     print(value_table['value_table_name'])
    #     for value_description in value_table['value_description']:
    #         print('  ' + value_description['value'], value_description['description'])

    # for comment in dbc.comments:
    #     print(comment)
    print('done')
