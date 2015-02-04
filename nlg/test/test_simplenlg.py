import unittest

import nlg.simplenlg as snlg


test_data = """<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
  xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
  <nlg:Request>

    <Document cat="PARAGRAPH">
      <child xsi:type="SPhraseSpec" FORM="IMPERATIVE" >
        <vp xsi:type="VPPhraseSpec" >
          <head xsi:type="WordElement" cat="VERB">
            <base>put</base>
          </head>
          <compl xsi:type="CoordinatedPhraseElement" conj="and" discourseFunction="OBJECT" >
            <coord xsi:type="NPPhraseSpec" >
              <spec xsi:type="WordElement" cat="DETERMINER">
                <base>the</base>
              </spec>
              <head xsi:type="WordElement" cat="NOUN">
                <base>piano</base>
              </head>

            </coord>
            <coord xsi:type="NPPhraseSpec" >
              <spec xsi:type="WordElement" cat="DETERMINER">
                <base>the</base>
              </spec>
              <head xsi:type="WordElement" cat="NOUN">
                <base>drum</base>
              </head>

            </coord>

          </compl>
          <compl xsi:type="PPPhraseSpec" >
            <head xsi:type="WordElement" cat="PREPOSITION">
              <base>into</base>
            </head>
            <compl xsi:type="NPPhraseSpec" >
              <spec xsi:type="WordElement" cat="DETERMINER">
                <base>the</base>
              </spec>
              <head xsi:type="WordElement" cat="NOUN">
                <base>truck</base>
              </head>

            </compl>

          </compl>

        </vp>

      </child>

    </Document>
  </nlg:Request>
</nlg:NLGSpec>
    """


test_data2="""<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>
<Document cat="PARAGRAPH">
<child xsi:type="SPhraseSpec">
    <subj xsi:type="NPPhraseSpec">
		<head xsi:type="WordElement" cat="NOUN">
			<base>transfusion of whole blood</base>
		</head>
    </subj>
    <vp xsi:type="VPPhraseSpec" PASSIVE="true" TENSE="PRESENT">
      <head cat="VERB">
      	<base>indicate</base>
	</head>
    </vp>
</child>
</Document>
</nlg:Request>
</nlg:NLGSpec>
"""


test_data3="""<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>
<Document cat="PARAGRAPH">
<child xsi:type="SPhraseSpec">
    <subj xsi:type="NPPhraseSpec">
		<head xsi:type="WordElement" cat="NOUN">
			<base>Roman</base>
		</head>
    </subj>
    <vp xsi:type="VPPhraseSpec" NEGATED="true">
        <head cat="VERB">
            <base>be</base>
        </head>
        <compl xsi:type="PPPhraseSpec" >
            <head xsi:type="WordElement" cat="PREPOSITION">
                <base>in</base>
            </head>
            <compl xsi:type="NPPhraseSpec" >
                <spec xsi:type="WordElement" cat="DETERMINER">
                    <base>the</base>
                </spec>
                <head xsi:type="WordElement" cat="NOUN">
                    <base>office</base>
                </head>
            </compl>
        </compl>
    </vp>
</child>
</Document>
</nlg:Request>
</nlg:NLGSpec>
"""


test_data4 = """\
<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>

<Document cat="PARAGRAPH">
<child xsi:type="SPhraseSpec" NEGATED="true">
  <subj xsi:type="StringElement">
    <val>Roman</val>
  </subj>
  <vp xsi:type="VPPhraseSpec">
    <head xsi:type="WordElement" cat="VERB">
      <base>be</base>
    </head>
    <compl xsi:type="PPPhraseSpec">
      <head xsi:type="WordElement" cat="PREPOSITION">
        <base>at</base>
      </head>
      <compl xsi:type="StringElement">
        <val>work</val>
      </compl>
    </compl>
  </vp>
</child>

</Document>
</nlg:Request>
</nlg:NLGSpec>
"""

test_data5 = """\
<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>

<Document cat="PARAGRAPH">
<child xsi:type="SPhraseSpec">
  <frontMod xsi:type="StringElement">
    <val>if</val>
  </frontMod>
  <subj xsi:type="StringElement">
    <val>p</val>
  </subj>
  <vp xsi:type="VPPhraseSpec">
    <head xsi:type="WordElement" cat="ADVERB">
      <base>then</base>
    </head>
    <compl xsi:type="StringElement">
      <val>q</val>
    </compl>
  </vp>
</child>

</Document>
</nlg:Request>
</nlg:NLGSpec>
"""

test_data6 ="""\
<?xml version="1.0" encoding="utf-8"?>
<nlg:NLGSpec xmlns="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:nlg="http://simplenlg.googlecode.com/svn/trunk/res/xml"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://simplenlg.googlecode.com/svn/trunk/res/xml ">
<nlg:Request>

<Document cat="PARAGRAPH">
<child xsi:type="SPhraseSpec">
  <subj xsi:type="NPPhraseSpec">
    <spec xsi:type="StringElement">
      <val>there+exists</val>
    </spec>
    <head xsi:type="StringElement">
      <val>x</val>
    </head>
    <postMod xsi:type="NPPhraseSpec" COMPLEMENTISER="such+that">
      <frontMod xsi:type="StringElement">
        <val>%28</val>
      </frontMod>
      <head xsi:type="StringElement">
        <val>At%28p%2C+y%29</val>
      </head>
      <postMod xsi:type="StringElement">
        <val>%29</val>
      </postMod>
    </postMod>
  </subj>
</child>

</Document>
</nlg:Request>
</nlg:NLGSpec>
"""



class TestSimplenlgClient(unittest.TestCase):

    @classmethod
    def setUpClass(obj):
        jp = 'nlg/resources/simplenlg.jar'
        port = '50007'
        obj.test_result = 'Put the piano and the drum into the truck.'
        obj.simplenlg_server = snlg.SimpleNLGServer(jp, port)
        obj.simplenlg_server.start()

    @classmethod
    def tearDownClass(obj):
        # signal that we would like to shut the server down
        obj.simplenlg_server.shutdown()

    def test_socket(self):
        mysocket = snlg.Socket('', 50007)
        with mysocket as sock:
            n = sock.send_string(test_data)
            self.assertEqual(n, len(test_data))
            msg = sock.recv_string()
            self.assertEqual(self.test_result, msg)

        with mysocket as sock:
            n = sock.send_string(test_data)
            self.assertEqual(n, len(test_data))
            msg = sock.recv_string()
            self.assertEqual(self.test_result, msg)

    def test_snlg(self):
        """ Preconditions: Settings file is located in 'simplenlg.settings'
            and the settings file contains entries for
            SimplenlgHost and SimplenlgPort.

        """
        host = 'localhost'
        port = 50007
        client = snlg.SimplenlgClient(host, port)
        realisation = client.xml_request(test_data)
        self.assertEqual(self.test_result, realisation)

        expected = 'Roman is not in the office.'
        realisation = client.xml_request(test_data3)
        self.assertEqual(expected, realisation)

        expected = 'Roman is not at work.'
        realisation = client.xml_request(test_data4)
        self.assertEqual(expected, realisation)
        
        expected = 'If p then q.'
        realisation = client.xml_request(test_data5)
        self.assertEqual(expected, realisation)
        
        expected = 'There exists x such that p.'
        realisation = client.xml_request(test_data6)
        self.assertEqual(expected, realisation)


# main
if __name__ == '__main__':
    unittest.main()
