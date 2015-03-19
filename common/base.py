#!/usr/bin/env python

"""
Application Base module
"""
import sys
import os
import re
import logging.config

from cStringIO import StringIO
import Ft.Xml.Domlette as domlette
import gnosis.xml.objectify
import yaml

def exepath(filename):
    """
    Takes a relative filepath and returns the correct execution path 
    regaurdless of where the containing file is run from
    """
    return os.path.abspath(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename))

logging.config.fileConfig(exepath('../logging_config.txt'))


# Metaprogramming Helpers -----------------------------


def rw_property(function):
    """Object decorator that exposes get, set, delete functions for a value"""
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function(None)
    return property(**func_locals)

RE_METHODIZE_FLATTEN  = re.compile(r'[- ]+')
RE_METHODIZE_CLEAN    = re.compile(r'[^a-zA-Z0-9_]')
RE_METHODIZE_COMPRESS = re.compile(r'_{2,}')
def methodize_label(label):
    """Converts a human readable label to a valid method name"""
    method_name = label.lower()
    method_name = re.sub(RE_METHODIZE_FLATTEN, '_', method_name)
    method_name = re.sub(RE_METHODIZE_CLEAN, '', method_name)
    method_name = re.sub(RE_METHODIZE_COMPRESS, '_', method_name)
    return method_name

def append_reference(obj, label, ref):
    """Adds a reference to ref on obj using a methodized version of label"""
    method_name = methodize_label(label)
    i=0
    while method_name in obj.__dict__:
        method_name = '%s_%s' % (method_name, i)
        i += 1
    obj.__dict__[method_name] = ref


# Type Casting Helpers -----------------------------


VAL_TO_TYPE_UNIT = re.compile(r'^(-?\d+(\.\d+)?)[ ]?(\w*)$')
def val_to_type_unit(s):
    """
    Given a value of an unknown type, this method will return a tuple containing an 
    appropriately type casted number (t[0]) and it's unit (t[1]) if one existed.
    
    Example:    
        val_to_num_unit('1sec')    >> (1,   'sec')
        val_to_num_unit('1.1 SEC') >> (1.1, 'sec')
        val_to_num_unit('1.1 S')   >> (1.1, 's')
        val_to_num_unit('1.1')     >> (1.1, None)
    """
    s = ('%s' % s)
    sre = re.search(VAL_TO_TYPE_UNIT, s)
    if sre == None:
        val, unit = s, None
    else:
        unit = sre.group(3) if sre.group(3) != '' else None
        if sre.group(2)==None:
            val = int(sre.group(1))
        else:
            val = float(sre.group(1))
        
    return (val, unit)

PARSE_FREQ = re.compile(r'^(\d+(\.\d+)?)[ ]?(hz|khz|mhz|ghz|thz)?$')
def xhz_to_hz(freq):
    """
    Convert any scale of Hz down to base Hz
    
    Examples:
        Hz  (hertz)
        kHz (kilohertz)  10^3 Hz
        MHz (megahertz)  10^6 Hz
        GHz (gigahertz)  10^9 Hz
        THz (terahertz)  10^12 Hz
    """    
    freq, unit = val_to_type_unit(freq)
    multipliers = {'khz':1000, 'mhz':1000000, 'ghz':1000000000, 'thz':1000000000000}
    if unit != None:
        unit = unit.lower()
    if unit in multipliers.keys():
        freq *= multipliers[unit]
    elif unit in [None, 'hz']:
        pass
    else:
        raise ValueError('Unrecognized frequency unit: %s' % unit)
    return freq


def time_to_sec(duration):
    """
    Parses a value and returns the equivalent in seconds
    
    Seconds (default unit if no unit designation present):
        second, seconds, secs, sec, s
        
    Minutes
        minute, minutes, mins, min, m
        
    Hours
        hour, hours, hrs, hr, h
        
    Examples:
        1        = 1 Second     >> 1
        1.3sec   = 1.3 Seconds  >> 1.3
        1m       = 60 Seconds   >> 60
        1 m      = 60 Seconds   >> 60
        1hours   = 1 Hour       >> 3600
    """
    duration, unit = val_to_type_unit(duration)
    if unit in ['h', 'hr', 'hrs', 'hours', 'hour']:
        duration *= 60 * 60
    elif unit in ['m', 'min', 'mins', 'minutes', 'minute']:
        duration *= 60
    elif unit in [None, 's', 'sec', 'secs', 'seconds', 'second']:
        pass
    else:
        raise ValueError('Unrecognized time unit: %s' % unit)

    return duration

def int_to_bin(n, width = 24):
    """Returns the binary of integer n, using (count) number of digits"""
    return ''.join([str((n >> y) & 1) for y in range(width-1, -1, -1)])  

def bin_to_int(bit_string):
    """Converts a binary string to an integer by applying int(bit_string, radix = 2)"""
    return int(''.join(bit_string), 2)

def hex_to_int(hex_string):
    """Converts a hex string to an integer by applying int(hex_string, radix = 16)"""
    return int(hex_string, 16)

def int_to_hex(n):
    """Return the hexadecimal string representation of integer n"""
    #return "0x%X" % n
    return hex(n)

def data_to_int(data):
    """Converts binary or hex string to it's integer value"""   
    data = str(data).strip().upper()
    if data[0]== 'B':
        return bin_to_int(data[1:])
    elif data[0]== 'H':
        return hex_to_int(data[1:])
    else:
        return int(data, 10)


# Formatting Helpers -----------------------------


#class AutoPCDATA(gnosis.xml.objectify._XO_):
#    def __repr__(self):
#        return self.PCDATA

def xml_as_obj(xml_seed):
    """
    Returns a gnosis.xml.objectify instance derived from the xml seed. The xml_seed can be, 
    raw xml, a filepath to an xml document, or an object created by gnosis.xml.objectify.
    """
    if hasattr(xml_seed,'PCDATA'):
        return xml_seed
    else:
        # gnosis.xml.objectify._XO_manufacturer = AutoPCDATA
        return gnosis.xml.objectify.XML_Objectify(xml_seed).make_instance()

#def walk_xo(o):
#    yield o
#    for node in children(o):
#        for child in walk_xo(node):
#            yield child

#class Family(gnosis.xml.objectify._XO_):
#    def __getitem__(self, key):
#        for member in self.Member:
#            if member.Name = key:
#                return member
#gnosis.xml.objectify._XO_Family = Family
#Family = make_instance('family.xml')
#print Family['Janet'].DOB


# Root Class -----------------------------

       
class AppBase(object):
    """Root application object"""
    
    entity_name = 'app_base'
    entity_atts = []
    
    def __init__(self):
        """Initializes a logger"""
        self.log = logging.getLogger('root')
        

    # Representation Formatters --------------------------------------------


    def current_instance_state(self):
        """Returns the current state of the object instance's class __properties__ as a dictionary"""
        cur = {}
        for prop in self.__class__.entity_atts:
            cur[prop] = getattr(self, prop)
        return cur

    def __repr__(self):
        """Native code representation of the object instance"""
        r = str(self.current_instance_state())
        return r

    def to_yaml(self):
        """YAML representation of the object instance"""
        entity = {self.__class__.entity_name.lower() : self.current_instance_state()}
        return yaml.dump(entity, default_flow_style = False)

    def to_xml(self, doc = None, output = None, indent = False):
        """
        XML representation of the object instance
        to_xml(output = 'str', indent = True)
        """
        
        # Determine what format to return the values as
        if output != None and output.lower() != 'str' and output.lower() != 'dom':
            # Check to see if it's a filepath
            if output.lower().split('.')[-1] == 'xml':
                output = os.path.abspath(output)
            else:
                raise ValueError('Unrecognized format: %s' % output)
        
        # If doc is None, create a document
        if doc != None:
            is_root = False
        else:
            is_root = True
            doc = domlette.implementation.createDocument(None, None, None)
            #doc.publicId = "-//W3C//DTD XHTML 1.0 Strict//EN"
            #doc.systemId = "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
        
        # Prepare an XML fragment to hold this entity's data
        frag = doc.createDocumentFragment()
        frag_root=doc.createElementNS(None, self.__class__.entity_name.lower())
        frag.appendChild(frag_root)

        # Append all of the key value pairs       
        for att_name in self.__class__.entity_atts:
            att = getattr(self, att_name)
            self.__att_to_xml(doc, frag_root, att_name, att)

        # Return the result
        if not is_root:
            return frag
        else:
            # Determine how to return
            doc.appendChild(frag)            
            if output == None:
                # Default returns XML as an objectified gnosis object
                return gnosis.xml.objectify.XML_Objectify(doc, parser='DOM').make_instance()
            elif output == 'str':
                # Return as string
                buf = StringIO()
                if indent:
                    domlette.PrettyPrint(doc, stream=buf, encoding='us-ascii')
                else:
                    domlette.Print(doc, stream=buf)
                xml_string = buf.getvalue()
                buf.close()                    
                return xml_string
            elif output == 'dom':
                # Return as a XML Document (Raw DOM)
                return doc
            else:
                f = open(output, 'w')
                if indent:
                    domlette.PrettyPrint(doc, stream=f)
                else:
                    domlette.Print(doc, stream=f)
                f.close()
                return True


    def __att_to_xml(self, doc, parent, att_name, att):
        """Recursive evaluator that converts entity attributes to XML nodes"""
                            
        if att == None:
            e=doc.createElementNS(None, att_name)
            parent.appendChild(e)
            e.appendChild(doc.createTextNode(''))
        elif type(att) == str or type(att) == unicode or type(att) == int:
            e=doc.createElementNS(None, att_name)
            parent.appendChild(e)
            e.appendChild(doc.createTextNode('%s' % att))
            #e.setAttributeNS(None, "class", "sample")
        elif hasattr(att, 'to_xml'):
            # Looks like an entity object, so call it's to_xml and append it
            child_frag = att.to_xml(doc)
            parent.appendChild(child_frag)
        elif type(att) == list or type(att) == tuple:
            # Looks like an ordered collection
            col = doc.createElementNS(None, att_name)
            parent.appendChild(col)
            for item in att:
                self.__att_to_xml(doc, col, att_name, item)
        elif isinstance(att, dict):
            # Looks like a dictionary
            col = doc.createElementNS(None, att_name)
            parent.appendChild(col)
            att_keys = att.keys()
            att_keys.sort()
            for item in att_keys:
                self.__att_to_xml(doc, col, item, att[item])
        else:
            # Not sure, so treat it like a string
            e=doc.createElementNS(None, att_name)
            parent.appendChild(e)
            e.appendChild(doc.createTextNode('%s' % att))


if __name__ == '__main__':
    pass


    
    