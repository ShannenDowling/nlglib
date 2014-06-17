#############################################################################
##
## Copyright (C) 2013 Roman Kutlak, University of Aberdeen.
## All rights reserved.
##
## This file is part of SAsSy NLG library.
##
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of University of Aberdeen nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
#############################################################################


import logging
from copy import deepcopy
from urllib.parse import quote_plus
import json


def get_log():
    return logging.getLogger(__name__)

get_log().addHandler(logging.NullHandler())


""" Data structures used by other packages. """

# macroplanning level structures
#   for content determination and content structuring

def enum(*sequential, **named):
    """ This functions declares a new type 'enum' that acts as an enum. """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


""" Rhetorical Structure Theory relations """
RST = enum( 'Elaboration', 'Exemplification',
            'Contrast', 'Exception', 'Set',
            'List', 'Sequence', 'Alternative',
            'Conjunction', 'Disjunction',
            'Leaf'
          )


class Document:
    """ The class Document represents a container holding information about
        a document - title and a list of sections.

    """
    def __init__(self, title, *sections):
        """ Create a new Document instance with given title and with
            zero or more sections.

        """
        self.title = title
        self.sections = [s for s in sections if s is not None]

    def __repr__(self):
        descr = (repr(self.title) + '\n' +
                '\n\n'.join([repr(s) for s in self.sections if s is not None]))
        return 'Document:\ntitle: %s' % descr.strip()

    def __str__(self):
        descr = (str(self.title) + '\n' +
                '\n\n'.join([str(s) for s in self.sections if s is not None]))
        return descr

    def __eq__(self, other):
        return (isinstance(other, Document) and
                self.title == other.title and
                self.sections == other.sections)

    def constituents(self):
        """ Return a generator to iterate through the elements. """
        yield self.title
        for x in self.sections: yield from x.constituents()


class Section:
    """ The class Section represents a container holding information about
        a section of a document - a title and a list of paragraphs.

    """
    def __init__(self, title, *paragraphs):
        """ Create a new section with given title and zero or more paragraphs.

        """
        self.title = title
        self.paragraphs = [p for p in paragraphs if p is not None]

    def __repr__(self):
        descr = (repr(self.title) + '\n' +
                '\n'.join([repr(p) for p in self.paragraphs if p is not None]))
        return 'Section:\ntitle: %s' % descr.strip()

    def __str__(self):
        descr = (str(self.title) + '\n' +
                '\n'.join([str(p) for p in self.paragraphs if p is not None]))
        return descr

    def __eq__(self, other):
        return (isinstance(other, Section) and
                self.title == other.title and
                self.paragraphs == other.paragraphs)

    def constituents(self):
        """ Return a generator to iterate through the elements. """
        yield self.title
        for x in self.paragraphs: yield from x.constituents()


class Paragraph:
    """ The class Paragraph represents a container holding information about
        a paragraph of a document - a list of messages.

    """
    def __init__(self, *messages):
        """ Create a new Paragraph with zero or more messages. """
        self.messages = [m for m in messages if m is not None]

    def __repr__(self):
        descr = '; '.join([repr(m) for m in self.messages if m is not None])
        return 'Paragraph (%d):\n%s' % (len(self.messages), descr.strip())

    def __str__(self):
        descr = ('\t' +
                 '; '.join([str(m) for m in self.messages if m is not None]))
        return descr

    def __eq__(self, other):
        return (isinstance(other, Paragraph) and
                self.messages == other.messages)

    def constituents(self):
        """ Return a generator to iterate through the elements. """
        for x in self.messages: yield from x.constituents()


class Message:
    """ A representation of a message (usually a sentence).
        A message has a nucleus and zero or more satelites joined 
        by an RST (Rhetorical Structure Theory) relation.

    """
    def __init__(self, rel, nucleus, *satelites):
        """ Create a new Message with given relation between the nucleus
            and zero or more satelites. 

        """
        self.rst = rel
        self.nucleus = nucleus
        self.satelites = [s for s in satelites if s is not None]
        self.marker = ''

    def __repr__(self):
        descr = ' '.join( [repr(x) for x in
            ([self.nucleus] + self.satelites) if x is not None ] )
        if descr == '': descr = '_empty_'
        return 'Message (%s): %s' % (self.rst, descr.strip())

    def __str__(self):
        descr = ' '.join( [str(x) for x in
            ([self.nucleus] + self.satelites) if x is not None ] )
        return (descr.strip() if descr is not None else '')

    def __eq__(self, other):
        return (isinstance(other, Message) and
                self.rst == other.rst and
                self.nucleus == other.nucleus and
                self.satelites == other.satelites)

    def constituents(self):
        """ Return a generator to iterate through the elements. """
        if self.nucleus:
            if hasattr(self.nucleus, 'constituents'):
                yield from self.nucleus.constituents()
            else:
                yield self.nucleus
        for x in self.satelites:
            if hasattr(x, 'constituents'):
                yield from x.constituents()
            else:   
                yield x


class MsgSpec:
    """ MsgSpec specifies an interface for various message specifications.
    Because the specifications are domain dependent, this is just a convenience 
    interface that allows the rest of the library to operate on the messages.
    
    The name of the message is used during lexicalisation where the name is 
    looked up in an ontology to find corresponding syntactic frame. To populate
    the frame, the lexicaliser finds all variables and uses their names 
    as a key to look up the values in the corresponding message. For example,
    if the syntactic structure in the domain ontology specifies a variable
    named 'foo', the lexicaliser will call msg.value_for('foo'), which
    in turn calls self.foo(). This should return the value for the key 'foo'.
    
    """
    def __init__(self, name):
        self.name = name
        self._features = dict()

    def __repr__(self):
        return 'MsgSpec: %s' % str(self)

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.name == other.name)

    def value_for(self, data_member):
        """ Return a value for an argument using introspection. """
        if not hasattr(self, data_member):
            raise ValueError('Error: cannot find value for key: %s' %
                                data_member)
        m = getattr(self, data_member)
        if not hasattr(m, '__call__'):
            raise ValueError('Error: cannot call the method "%s"' %
                                data_member)
        return m()

    @classmethod
    def instantiate(Klass, data):
        return None


class StringMsgSpec(MsgSpec):
    """ Use this as a simple message that contains canned text. """
    def __init__(self, text):
        super().__init__('simple_message')
        self.text = text

    def value_for(self, param_idx):
        return String(self.text)


# microplanning level structures


class ElemntCoder(json.JSONEncoder):
    @staticmethod
    def to_json(python_object):
        if isinstance(python_object, Element):
            return {'__class__': str(type(python_object)),
                    '__value__': python_object.__dict__} 
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    @staticmethod
    def from_json(json_object):
        if '__class__' in json_object:
            if json_object['__class__'] == "<class 'nlg.structures.Element'>":
                return Element.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.String'>":
                return String.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.Word'>":
                return Word.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.PlaceHolder'>":
                return PlaceHolder.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.Phrase'>":
                return Phrase.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.Clause'>":
                return Clause.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.NP'>":
                return NP.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.VP'>":
                return VP.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.PP'>":
                return PP.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.AdjP'>":
                return AdjP.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.AdvP'>":
                return AdvP.from_dict(json_object['__value__'])
            if json_object['__class__'] == "<class 'nlg.structures.CC'>":
                return CC.from_dict(json_object['__value__'])
                
        return json_object
        
        
class Element:
    """ A base class representing an NLG element.
        Aside for providing a base class for othe kinds of NLG elements,
        the class also implements basic functionality for elements.

    """
    def __init__(self, vname='visit_element'):
        self.id = 0 # this is useful for replacing elements
        self._visitor_name = vname
        self._features = dict()
#        self.realisation = ""

    def __eq__(self, other):
        if (not isinstance(other, Element)):
            return False
        # disregard realisation as that is only a cached value
        return (self.id == other.id and
                self._visitor_name == other._visitor_name and
                self._features == other._features)

    @classmethod
    def from_dict(Cls, dct):
        o = Cls()
        o.__dict__ = dct
        return o

    def to_str(self):
        return ""
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
        
    def __repr__(self):
        return self.to_JSON()
        text = 'Element (%s): ' % self._visitor_name
        text += str(self._features)
        if '' != self.realisation:
            text += ' realisation:' + self.realisation
        return text

    def __str__(self):
        v = StrVisitor()
        self.accept(v)
        return v.to_str()
        
    def accept(self, visitor, element='child'):
        """Implementation of the Visitor pattern."""
        if self._visitor_name == None:
            raise ValueError('Error: visit method of uninitialized visitor '
                             'called!')
        # get the appropriate method of the visitor instance
        m = getattr(visitor, self._visitor_name)
        # ensure that the method is callable
        if not hasattr(m, '__call__'):
            raise ValueError('Error: cannot call undefined method: %s on '
                             'visitor' % self._visitor_name)
        # and finally call the callback
        m(self, element)

    def features_to_xml_attributes(self):
        features = ""
        for (k, v) in self._features.items():
            features += '%s="%s" ' % (quote_plus(str(k)), quote_plus(str(v)))
        return features

    def add_feature(self, feature, value):
        """ Add a feature to the feature set.
        If the feature exists, overwrite the old value.
        
        """
        self._features[feature] = value

    def has_feature(self, feature):
        """ Return True if the element has the given feature. """
        return (feature in self._features)

    def get_feature(self, feature):
        """ Return value for given feature or raise KeyError. """
        return self._features[feature]

    def feature(self, feat):
        """ Return value for given feature or None. """
        if feat in self._features: return self._features[feat]
        else: return None

    def del_feature(self, feat, val=None):
        """ Delete a feature, if the element has it else do nothing.
        If val is None, delete whathever value is assigned to the feature.
        Otherwise only delete the feature if it has matching value.

        """
        if feat in self._features:
            if val is not None: del self._features[feat]
            elif val == self._features[feat]: del self._features[feat]

    def constituents(self):
        """ Return a generator representing constituents of an element. """
        return []

    def arguments(self):
        """ Return any arguments (placeholders) from the elemen as a generator.
        
        """
        return list(filter(lambda x: isinstance(x, PlaceHolder),
                           self.constituents()))

    def replace(self, one, another):
        """ Replace first occurance of one with another.
        Return True if successful.
        
        """
        return False # basic implementation does nothing

    def replace_argument(self, arg_id, repl):
        """ Replace an argument with given id by repl if such argumen exists."""
        for a in self.arguments():
            if a.id == arg_id:
                return self.replace(a, repl)
        return False

    def replace_arguments(self, *args, **kwargs):
        """ Replace arguments with ids in the kwargs by the corresponding
        values.
        Replacements can be passed as a single dictionary or a kwarg list
        (e.g., arg1=x, arg2=y, ...)
        
        """
        # FIXME: this does not look correct...
        if len(args) > 0 and len(args) > 1:
            raise ValueError('too many parameters')
        elif len(args) > 0:
            for k, v in args[0]:
                self.replace_argument(k, v)
        else:
            for k, v in kwargs.items():
                self.replace_argument(k, v)

    @staticmethod
    def _strings_to_elements(*params):
        """ Check that all params are Elements and convert
        and any strings to String.
        
        """
        fn = lambda x: String(x) if isinstance(x, str) else x
        return map(fn, params)

    @staticmethod
    def _add_to_list(lst, *mods):
        """ Add modifiers to the given list. Convert any strings to String. """
        for p in Element._strings_to_elements(*mods):
            if p not in lst: lst.append(p)

    @staticmethod
    def _del_from_list(lst, *mods):
        """ Delete elements from a list. Convert any strings to String. """
        for p in Element._strings_to_elements(*mods):
            if p in lst: lst.remove(p)


class String(Element):
    """ String is a basic element representing canned text. """
    def __init__(self, val=""):
        super().__init__('visit_string')
        self.val = val
    
    def to_xml(self, element):
        text = ('<%s xsi:type="StringElement">'
                '\n\t<val>%s</val>\n</%s>\n'
                % (element, quote_plus(str(self.val)), element))
        return text
    
    def to_str(self):
        return str(self.val)
    
    def __eq__(self, other):
        if (not isinstance(other, String)):
            return False
        return (self.val == other.val and
                super().__eq__(other))

    def __str__(self):
        return str(self.val) if self.val is not None else ''

    def __repr__(self):
        return self.to_JSON()
        return ('String(%s)' % self.val)
        
    def constituents(self):
        return [self]


class Word(Element):
    """ Word represents word and its corresponding POS (Part-of-Speech) tag. """
    def __init__(self, word=None, pos=None):
        super().__init__('visit_word')
        self.word = word
        self.pos = pos

    def to_xml(self, element):
        # FIXME
        # a bug in simplenlg treats 'is' differently from 'be'
        # so keep 'is' in templates to allow simple to_str realisation
        # but change it to 'be' for simplenlg
        word = self.word
        if word == 'is': word = 'be'
        text = ('<%s xsi:type="WordElement" cat="%s">'
                '\n\t<base>%s</base>\n</%s>\n'
                % (element, quote_plus(str(self.pos)),
                    quote_plus(str(word)), element))
        return text
    
    def to_str(self):
        return self.word if self.word is not None else ''
    
    def __eq__(self, other):
        if (not isinstance(other, Word)):
            return False
        return (self.word == other.word and
                self.pos == other.pos and
                super().__eq__(other))

    def __str__(self):
        return self.word if self.word is not None else ''

    def __repr__(self):
        return self.to_JSON()
        text = 'Word: %s (%s) %s' % (str(self.word),
                                     str(self.pos),
                                     str(self._features))
        return text

    def constituents(self):
        return [self]


class PlaceHolder(Element):
    """ An element used as a place-holder in a sentence. The purpose of this
        element is to make replacing arguments easier. For example, in a plan
        one might want to replace arguments of an action with the instantiated
        objects
        E.g.,   move (x, a, b) -->
                move PlaceHolder(x) from PlaceHolder(a) to PlaceHolder(b) -->
                move (the block) from (the table) to (the green block)
        
    """
    def __init__(self, id=None, obj=None):
        super().__init__('visit_placeholder')
        self.id = id
        self.set_value(obj)

    def to_xml(self, element):
        text = ('<%s xsi:type="StringElement">'
                '\n\t<val>%s</val>\n</%s>\n'
                % (element, quote_plus(str(self.id)), element))
        return text

    def to_str(self):
        if (self.value):
            return str(self.value)
        return str(self.id)

    def __eq__(self, other):
        if (not isinstance(other, PlaceHolder)):
            return False
        else:
            return (self.id == other.id and
                    self.value == other.value and
                    super().__eq__(other))

    def __repr__(self):
        return self.to_JSON()
        return ('PlaceHolder: id=%s value=%s %s' %
                (repr(self.id), repr(self.value), repr(self._features)))

    def __str__(self):
        return self.to_str()

    def constituents(self):
        return [self]

    def set_value(self, val):
        self.value = String(val) if isinstance(val, str) else val


class Phrase(Element):
    """ A base class for all kinds of phrases - elements containing other
        elements in specific places of the construct (front-, pre-, post-
        modifiers as well as the head of the phrase and any complements.
        
        Not every phrase has need for all of the kinds of modiffications.

    """
    def __init__(self, type=None, discourse_fn=None, vname='visit_phrase'):
        super().__init__(vname)
        self.type = type
        self.discourse_fn = discourse_fn
        self.front_modifier = list()
        self.pre_modifier = list()
        self.head = None
        self.complement = list()
        self.post_modifier = list()

    def __eq__(self, other):
        if (not isinstance(other, Phrase)):
            return False
        return (self.type == other.type and
                self.discourse_fn == other.discourse_fn and
                self.front_modifier == other.front_modifier and
                self.pre_modifier == other.pre_modifier and
                self.head == other.head and
                self.complement == other.complement and
                self.post_modifier == other.post_modifier and
                super().__eq__(other))

    def __str__(self):
        if 'COMPLEMENTISER' in self._features:
            compl = self._features['COMPLEMENTISER']
        else:
            compl = ''
        data = [' '.join([str(o) for o in self.front_modifier]),
                 ' '.join([str(o) for o in self.pre_modifier]),
                 str(self.head) if self.head is not None else '',
                 compl,
                 ' '.join([str(o) for o in self.complement]),
                 ' '.join([str(o) for o in self.post_modifier])]
        # remove empty strings
        data = filter(lambda x: x != '', data)
        return (' '.join(data))

    def __repr__(self):
        return self.to_JSON()
        return ('(Phrase %s %s: "%s" %s)' %
                (self.type, self.discourse_fn, str(self), str(self._features)))

    def set_front_modifiers(self, *mods):
        """ Set front-modifiers to the passed parameters. """
        self.front_modifier = list(self._strings_to_elements(*mods))

    def add_front_modifier(self, *mods):
        """ Add one or more front-modifiers. """
        self._add_to_list(self.front_modifier, *mods)

    def del_front_modifier(self, *mods):
        """ Remove one or more front-modifiers if present. """
        self._del_from_list(self.front_modifier, *mods)

    def set_pre_modifiers(self, *mods):
        """ Set pre-modifiers to the passed parameters. """
        self.pre_modifier = list(self._strings_to_elements(*mods))

    def add_pre_modifier(self, *mods):
        """ Add one or more pre-modifiers. """
        self._add_to_list(self.pre_modifier, *mods)

    def del_pre_modifier(self, *mods):
        """ Delete one or more pre-modifiers if present. """
        self._del_from_list(self.pre_modifier, *mods)

    def set_complements(self, *mods):
        """ Set complemets to the given ones. """
        self.complement = list(self._strings_to_elements(*mods))

    def add_complement(self, *mods):
        """ Add one or more complements. """
        self._add_to_list(self.complement, *mods)

    def del_complement(self, *mods):
        """ Delete one or more complements if present. """
        self._del_from_list(self.complement, *mods)

    def set_post_modifiers(self, *mods):
        """ Set post-modifiers to the given parameters. """
        self.post_modifier = list(self._strings_to_elements(*mods))

    def add_post_modifier(self, *mods):
        """ Add one or more post-modifiers. """
        self._add_to_list(self.post_modifier, *mods)

    def del_post_modifier(self, *mods):
        """ Delete one or more post-modifiers if present. """
        self._del_from_list(self.post_modifier, *mods)

    def set_head(self, elt):
        """ Set head of the phrase to the given element. """
        self.head = String(elt) if isinstance(elt, str) else elt

    def yield_front_modifiers(self):
        """ Iterate through front modifiers. """
        for o in self.front_modifier:
            for x in o.constituents():
                yield x

    def yield_pre_modifiers(self):
        """ Iterate through pre-modifiers. """
        for o in self.pre_modifier:
            for x in o.constituents():
                yield x

    def yield_head(self):
        """ Iterate through the elements composing the head. """
        if self.head is not None:
            for x in self.head.constituents():
                yield x

    def yield_complements(self):
        """ Iterate through complements. """
        for o in self.complement:
            for x in o.constituents():
                yield x

    def yield_post_modifiers(self):
        """ Iterate throught post-modifiers. """
        for o in self.post_modifier:
            for x in o.constituents():
                yield x

    def constituents(self):
        """ Return a generator to iterate through constituents. """
        yield from self.yield_front_modifiers()
        yield from self.yield_pre_modifiers()
        yield from self.yield_head()
        yield from self.yield_complements()
        yield from self.yield_post_modifiers()

    # TODO: consider spliting the code below similarly to 'constituents()'
    def replace(self, one, another):
        """ Replace first occurance of one with another.
        Return True if successful.
        
        """
        for i, o in enumerate(self.front_modifier):
            if o == one:
                if another is None:
                    del sent.front_modifier[i]
                else:
                    self.front_modifier[i] = another
                return True
            else:
                if o.replace(one, another):
                    return True

        for i, o in enumerate(self.pre_modifier):
            if o == one:
                if another is None:
                    del sent.pre_modifier[i]
                else:
                    self.pre_modifier[i] = another
                return True
            else:
                if o.replace(one, another):
                    return True

        if self.head == one:
            self.head = another
            return True
        elif self.head is not None:
            if self.head.replace(one, another):
                return True

        for i, o in enumerate(self.complement):
            if o == one:
                if another is None:
                    del sent.complement[i]
                else:
                    self.complement[i] = another
                return True
            else:
                if o.replace(one, another):
                    return True

        for i, o in enumerate(self.post_modifier):
            if o == one:
                if another is None:
                    del sent.front_modifier[i]
                else:
                    self.front_modifier[i] = another
                return True
            else:
                if o.replace(one, another):
                    return True
        return False


class Clause(Phrase):
    """ Clause - sentence.
    From simplenlg:
     * <UL>
     * <li>FrontModifier (eg, "Yesterday")
     * <LI>Subject (eg, "John")
     * <LI>PreModifier (eg, "reluctantly")
     * <LI>Verb (eg, "gave")
     * <LI>IndirectObject (eg, "Mary")
     * <LI>Object (eg, "an apple")
     * <LI>PostModifier (eg, "before school")
     * </UL>

    """

    def __init__(self, subj=None, vp=None):
        super().__init__(type='CLAUSE', vname='visit_clause')
        self.set_subj(subj)
        self.set_vp(vp)

    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="SPhraseSpec" %s>\n' % (element, features)
        return text
    
    def __eq__(self, other):
        if (not isinstance(other, Clause)):
            return False
        return (self.subj == other.subj and
                self.vp == other.vp and
                super().__eq__(other))

    def __str__(self):
        return ' '.join([str(x) for x in
                        [self.subj, self.vp] if x is not None])

    def __repr__(self):
        return self.to_JSON()
        return ('Clause: subj=%s vp=%s\n(%s)' %
                (str(self.subj), str(self.vp), super().__str__()))

    def set_subj(self, subj):
        """ Set the subject of the clause. """
        # convert str to String if necessary
        self.subj = String(subj) if isinstance(subj, str) else subj

    def set_vp(self, vp):
        """ Set the vp of the clause. """
        self.vp = String(vp) if isinstance(vp, str) else vp

    def constituents(self):
        """ Return a generator to iterate through constituents. """
        yield from self.yield_front_modifiers()
        if self.subj is not None:
            # TODO: can we use yield from here? I think so...
            for c in self.subj.constituents(): yield c
        yield from self.yield_pre_modifiers()
        if self.vp is not None:
            for c in self.vp.constituents(): yield c
        yield from self.yield_complements()
        yield from self.yield_post_modifiers()

    def replace(self, one, another):
        """ Replace first occurance of one with another.
        Return True if successful.
        
        """
        if self.subj == one:
            self.subj = another
            return True
        elif self.subj is not None:
            if self.subj.replace(one, another): return True

        if self.vp == one:
            self.vp = another
            return True
        elif self.vp is not None:
            if self.vp.replace(one, another): return True

        return super().replace(one, another)


class NP(Phrase):
    """
     * <UL>
     * <li>Specifier    (eg, "the")</LI>
     * <LI>PreModifier  (eg, "green")</LI>
     * <LI>Noun         (eg, "apple")</LI>
     * <LI>PostModifier (eg, "in the shop")</LI>
     * </UL>
     """
    def __init__(self, head=None, spec=None, compl=None):
        super().__init__(type='NOUN_PHRASE', vname='visit_np')
        self.set_spec(spec)
        self.set_head(head)
        if compl is not None: self.add_complement(compl)

    def __eq__(self, other):
        if (not isinstance(other, NP)):
            return False
        return (self.spec == other.spec and
                self.head == other.head and
                super().__eq__(other))

    def __str__(self):
        """ Return string representation of the class. """
        if self.spec is not None:
            return str(self.spec) + ' ' + super().__str__()
        else:
            return super().__str__()

    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="NPPhraseSpec" %s>\n' % (element, features)
        return text

    def set_spec(self, spec):
        """ Set the specifier (e.g., determiner) of the NP. """
        # convert str to String if necessary
        self.spec = String(spec) if isinstance(spec, str) else spec

    def constituents(self):
        """ Return a generator to iterate through constituents. """
        if self.spec is not None:
            for c in self.spec.constituents(): yield c
        yield from self.yield_front_modifiers()
        yield from self.yield_pre_modifiers()
        yield from self.yield_head()
        yield from self.yield_complements()
        yield from self.yield_post_modifiers()

    def replace(self, one, another):
        """ Replace first occurance of one with another.
        Return True if successful.
        
        """
        if self.spec == one:
            self.spec = another
            return True
        elif self.spec is not None:
            if self.spec.replace(one, another): return True

        return super().replace(one, another)


class VP(Phrase):
    """
    * <UL>
     * <LI>PreModifier      (eg, "reluctantly")</LI>
     * <LI>Verb             (eg, "gave")</LI>
     * <LI>IndirectObject   (eg, "Mary")</LI>
     * <LI>Object           (eg, "an apple")</LI>
     * <LI>PostModifier     (eg, "before school")</LI>
     * </UL>
     """
    def __init__(self, head=None, *compl):
        super().__init__(type='VERB_PHRASE', vname='visit_vp')
        self.set_head(head)
        self.add_complement(*compl)

    def get_object(self):
        for c in self.complement:
            if ('discourseFunction' in c.features and
                c.features['discourseFunction'] == 'OBJECT'):
                return c
        return None

    def remove_object(self):
        compls = list()
        for c in self.complement:
            if ('discourseFunction' in c.features and
                c.features['discourseFunction'] == 'OBJECT'):
                continue
            else:
                compls.append(c)
        self.complement = compls

    def set_object(self, obj):
        self.remove_object()
        if obj is not None:
            if isinstance(obj, str): obj = String(obj)
            obj.features['discourseFunction'] = 'OBJECT'
            self.complement.insert(0, obj)

    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="VPPhraseSpec" %s>\n' % (element, features)
        return text


class PP(Phrase):
    def __init__(self, head=None, *compl):
        super().__init__(type='PREPOSITIONAL_PHRASE', vname='visit_pp')
        self.set_head(head)
        self.add_complement(*compl)
    
    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="PPPhraseSpec" %s>\n' % (element, features)
        return text


class AdvP(Phrase):
    def __init__(self, head=None, *compl):
        super().__init__(type='ADVERB_PHRASE', vname='visit_pp')
        self.set_head(head)
        self.add_complement(*compl)

    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="AdvPhraseSpec" %s>\n' % (element, features)
        return text


class AdjP(Phrase):
    def __init__(self, head=None, *compl):
        super().__init__(type='ADJECTIVE_PHRASE', vname='visit_pp')
        self.set_head(head)
        self.add_complement(*compl)
    
    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = '<%s xsi:type="AdjPhraseSpec" %s>\n' % (element, features)
        return text


class CC(Element):
    """ Coordinated clause with a conjunction. """

    def __init__(self, *coords, conj='and'):
        super().__init__(vname='visit_cc')
        self.coords = list()
        self.add_coordinate(*coords)
        self.add_feature('conj', conj)

    def __eq__(self, other):
        if (not isinstance(other, CC)):
            return False
        else:
            return (self.coords == other.coords and
                    super().__eq__(other))

    def __str__(self):
        if self.coords is None: return ''
        result = ''
        for i, x in enumerate(self.coords):
            if self.conj == 'and' and i < len(self.coords) - 2:
                result += ', '
            elif self.conj == 'and' and i == len(self.coords) - 1:
                result += ' and '
            else:
                result += ' ' + self.conj + ' '
            result += str(x)
        return result

    def to_xml(self, element):
        features = self.features_to_xml_attributes()
        text = ('<%s xsi:type="CoordinatedPhraseElement" %s>\n' %
                (element, features))
        return text

    def add_coordinate(self, *elts):
        """ Add one or more elements as a co-ordinate in the clause. """
        for e in self._strings_to_elements(*elts):
#            if e not in self.coords: self.coords.append(e)
            self.coords.append(e)

    def constituents(self):
        """ Return a generator to iterate through constituents. """
        if self.coords is not None:
            for c in self.coords:
                if hasattr(c, 'constituents'):
                    yield from c.constituents()
                else:
                    yield c

    def replace(self, one, another):
        """ Replace first occurance of one with another.
        Return True if successful.
        
        """
        for i, o in enumerate(self.coords):
            if o == one:
                if another is not None: self.coords[i] = another
                else: del self.coords[i]
                return True
        return False


# TODO: the visitor implementation is not right - look at Bruce Eckel's one
class IVisitor:
    def __init__(self):
        self.text = ''
        
    def visit_phrase(self, node, element=''):    
        if (node.has_feature('NEGATION') and 
            node.get_feature('NEGATION') == 'TRUE'):
            self.text += ' not'
            
        if node.front_modifier:
            for c in node.front_modifier:
                c.accept(self, 'frontMod')
        
        if node.pre_modifier:
            for c in node.pre_modifier:
                c.accept(self, 'preMod')
        
        if node.head:
            node.head.accept(self, 'head')

        if node.has_feature('COMPLEMENTISER'):
            self.text += ' ' + node.get_feature('COMPLEMENTISER')
                        
        if node.complement:
            for c in node.complement:
                c.accept(self, 'compl')

        if node.post_modifier:
            for c in node.post_modifier:
                c.accept(self, 'postMod')


class XmlVisitor(IVisitor):
    def __init__(self):
        self.header = '''
<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>

<Document cat="PARAGRAPH">
'''
        self.xml = ''
        self.footer = '''
</Document>
</nlg:Request>
</nlg:NLGSpec>
'''

    def visit_word(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
    
    def visit_string(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
    
    def visit_placeholder(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)

    def visit_clause(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
        if node.subj:
            node.subj.accept(self, 'subj')
        if node.vp:
            node.vp.accept(self, 'vp')
        self.xml += '\n</%s>\n' % element

    def visit_np(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
        if node.spec:
            node.spec.accept(self, 'spec')
        self.visit_phrase(node)
        self.xml += '\n</%s>\n' % element

    def visit_vp(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
        self.visit_phrase(node)
        self.xml += '\n</%s>\n' % element

    def visit_pp(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
        self.visit_phrase(node)
        self.xml += '\n</%s>\n' % element

    def visit_cc(self, node, element):
        if (node is not None):
            self.xml += node.to_xml(element)
        for c in node.coords:
            c.accept(self, 'coord')
        self.xml += '\n</%s>\n' % element

    def to_xml(self):
        return (self.header + self.xml + self.footer).strip()
    
    def clear(self):
        self.xml = ''

    def __repr__(self):
        return ('[ XmlVisitor:\n%s]' % (self.header + self.xml + self.footer))


class StrVisitor(IVisitor):

    def visit_element(self, node, element):
        # there is no text in Element
        pass
    
    def visit_word(self, node, element):
        if (node is not None):
            self.text += ' ' + node.to_str()
    
    def visit_string(self, node, element):
        if (node is not None):
            self.text += ' ' + node.to_str()
    
    def visit_placeholder(self, node, element):
        if (node is not None):
            self.text += ' ' + node.to_str()
    
    def visit_clause(self, node, element):
        if (node.has_feature('NEGATION') and 
            node.get_feature('NEGATION') == 'TRUE'):
            self.text += ' not'
#        for e in node.front_modifier: e.accept()
#        for e in node.pre_modifier: e.accept()
        if node.subj:
            node.subj.accept(self)
        if node.vp:
            node.vp.accept(self)
#        for e in node.complement: e.accept()
#        for e in node.post_modifier: e.accept()
    
    def visit_np(self, node, element):
        if node.spec:
            node.spec.accept(self)
        self.visit_phrase(node)
    
    def visit_vp(self, node, element):
        self.visit_phrase(node)
    
    def visit_pp(self, node, element):
        self.visit_phrase(node)
    
    def visit_cc(self, node, element):
        if len(node.coords) > 2:
            for c in node.coords[:-1]:
                c.accept(self)
                if node.conj == 'and':
                    self.text += ','
                else:
                    self.text += ' ' + node.conj
            self.text = self.text[:-1] # remove the last ", "
            self.text += ' ' + node.conj
            node.coords[-1].accept(self)
    
        elif len(node.coords) > 1:
            get_log().debug('visiting coord 1')
            node.coords[0].accept(self)
            self.text += ' ' + node.get_feature('conj')
            get_log().debug('visiting coord 2')
            node.coords[1].accept(self)

        elif len(node.coords) > 0:
            node.coords[0].accept(self)

    def to_str(self):
        return self.text.strip()
    
    def clear(self):
        self.text = ''
    
    def __repr__(self):
        return ('[ StrVisitor:\n%s]' % (self.text))


def sentence_iterator(sent):
    if isinstance(sent, Clause):
        for x in sentence_iterator(sent.vp):
            yield x
        yield sent.vp
        yield sent.subj
    
        return
    
    if isinstance(sent, Phrase):
        for o in reversed(sent.post_modifier):
            for x in sentence_iterator(o):
                yield x

        for o in reversed(sent.complement):
            for x in sentence_iterator(o):
                yield x

        if sent.head is not None:
            for x in sentence_iterator(sent.head):
                yield x

        for o in reversed(sent.pre_modifier):
            for x in sentence_iterator(o):
                yield x

        if isinstance(sent, NP):
            for x in sentence_iterator(sent.spec):
                yield x

        for o in reversed(sent.front_modifier):
            for x in sentence_iterator(o):
                yield x

    if isinstance(sent, CC):
        for x in sent.coords:
            yield x
        yield sent

    else:
        yield (sent)


def aggregation_sentence_iterator(sent):
    if isinstance(sent, Clause):
        for x in sentence_iterator(sent.vp):
            yield x
        return

    if isinstance(sent, Phrase):
        for o in reversed(sent.post_modifier):
            for x in sentence_iterator(o):
                yield x

    for o in reversed(sent.complement):
        for x in sentence_iterator(o):
            yield x

    for o in reversed(sent.pre_modifier):
        for x in sentence_iterator(o):
            yield x

    else:
        yield (sent)


def replace_element(sent, elt, replacement=None):
    if sent == elt:
        return True
    
    if isinstance(sent, Clause):
        if sent.subj == elt:
            sent.subj = replacement
            return True
        else:
            if replace_element(sent.subj, elt, replacement):
                return True;

        if sent.vp == elt:
            sent.vp = replacement
            return True

        else:
            if replace_element(sent.vp, elt, replacement):
                return True;

    if isinstance(sent, CC):
        for i, o in list(enumerate(sent.coords)):
            if (o == elt):
                if replacement is None:
                    del sent.coords[i]
                else:
                    sent.coords[i] = replacement
                return True

    if isinstance(sent, Phrase):
        res = False
        for i, o in reversed(list(enumerate(sent.post_modifier))):
            if (o == elt):
                if replacement is None:
                    del sent.post_modifier[i]
                else:
                    sent.post_modifier[i] = replacement
                return True
            else:
                if replace_element(o, elt, replacement):
                    return True
        for i, o in reversed(list(enumerate(sent.complement))):
            if (o == elt):
                if replacement is None:
                    del sent.complement[i]
                else:
                    sent.complement[i] = replacement
                return True
            else:
                if replace_element(o, elt, replacement):
                    return True
        if sent.head == elt:
            sent.head = replacement
            return True
        for i, o in reversed(list(enumerate(sent.pre_modifier))):
            if (o == elt):
                if replacement is None:
                    del sent.pre_modifier[i]
                else:
                    sent.pre_modifier[i] = replacement
                return True
            else:
                if replace_element(o, elt, replacement):
                    return True

        if isinstance(sent, NP):
            if sent.spec == elt:
                sent.spec = replacement
                return True

        for i, o in reversed(list(enumerate(sent.front_modifier))):
            if (o == elt):
                if replacement is None:
                    del sent.front_modifier[i]
                else:
                    sent.front_modifier[i] = replacement
                return True
            else:
                if replace_element(o, elt, replacement):
                    return True

    return False


class Tree:
    """ A class representing a syntax tree. """


