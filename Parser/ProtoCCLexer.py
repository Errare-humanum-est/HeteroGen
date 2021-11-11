# $ANTLR 3.5.2 /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g 2021-04-30 02:55:45

import sys
from antlr3 import *



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
EOF=-1
T__99=99
T__100=100
T__101=101
T__102=102
T__103=103
T__104=104
T__105=105
T__106=106
T__107=107
T__108=108
T__109=109
T__110=110
T__111=111
T__112=112
T__113=113
T__114=114
T__115=115
T__116=116
T__117=117
T__118=118
T__119=119
T__120=120
ACCESS=4
ACCESS_=5
ARCH=6
ARCH_=7
ARRAY=8
ARRAY_=9
ASSIGN_=10
AWAIT=11
AWAIT_=12
BCAST_=13
BOOL=14
BOOLID=15
BOOL_=16
BREAK=17
BREAK_=18
CACHE=19
CACHE_=20
CBRACE=21
CCBRACE=22
CEBRACE=23
COMMA=24
COMMENT=25
COND_=26
CONSTANT=27
CONSTANT_=28
DATA=29
DATA_=30
DDOT=31
DIR=32
DIR_=33
DOT=34
ELEMENT_=35
ELSE=36
ENDIFELSE_=37
ENDIF_=38
ENDPROC_=39
ENDWHEN_=40
EQUALSIGN=41
EVENT_=42
EVENT_ACK_=43
EVICT=44
FIFO=45
FIFO_=46
GUARD_=47
ID=48
ID_=49
IF=50
IFELSE_=51
IF_=52
INITSTATE_=53
INITVAL_=54
INT=55
INTID=56
INT_=57
LINE_COMMENT=58
MACHN_=59
MCAST_=60
MEM=61
MEM_=62
MINUS=63
MSG=64
MSGCSTR_=65
MSG_=66
MULT=67
NCOND_=68
NEG=69
NETWORK=70
NETWORK_=71
NEXT=72
NEXT_=73
NID=74
OBJSET_=75
OBRACE=76
OCBRACE=77
OEBRACE=78
PLUS=79
PROC=80
PROC_=81
RANGE_=82
SEMICOLON=83
SEND_=84
SET=85
SETFUNC_=86
SET_=87
STABLE=88
STABLE_=89
STALL=90
STALL_=91
STATE=92
TRANS_=93
UNDEF=94
UNDEF_=95
WHEN=96
WHEN_=97
WS=98

# token names
tokenNamesMap = {
    0: "<invalid>", 1: "<EOR>", 2: "<DOWN>", 3: "<UP>",
    -1: "EOF", 99: "T__99", 100: "T__100", 101: "T__101", 102: "T__102", 
    103: "T__103", 104: "T__104", 105: "T__105", 106: "T__106", 107: "T__107", 
    108: "T__108", 109: "T__109", 110: "T__110", 111: "T__111", 112: "T__112", 
    113: "T__113", 114: "T__114", 115: "T__115", 116: "T__116", 117: "T__117", 
    118: "T__118", 119: "T__119", 120: "T__120", 4: "ACCESS", 5: "ACCESS_", 
    6: "ARCH", 7: "ARCH_", 8: "ARRAY", 9: "ARRAY_", 10: "ASSIGN_", 11: "AWAIT", 
    12: "AWAIT_", 13: "BCAST_", 14: "BOOL", 15: "BOOLID", 16: "BOOL_", 17: "BREAK", 
    18: "BREAK_", 19: "CACHE", 20: "CACHE_", 21: "CBRACE", 22: "CCBRACE", 
    23: "CEBRACE", 24: "COMMA", 25: "COMMENT", 26: "COND_", 27: "CONSTANT", 
    28: "CONSTANT_", 29: "DATA", 30: "DATA_", 31: "DDOT", 32: "DIR", 33: "DIR_", 
    34: "DOT", 35: "ELEMENT_", 36: "ELSE", 37: "ENDIFELSE_", 38: "ENDIF_", 
    39: "ENDPROC_", 40: "ENDWHEN_", 41: "EQUALSIGN", 42: "EVENT_", 43: "EVENT_ACK_", 
    44: "EVICT", 45: "FIFO", 46: "FIFO_", 47: "GUARD_", 48: "ID", 49: "ID_", 
    50: "IF", 51: "IFELSE_", 52: "IF_", 53: "INITSTATE_", 54: "INITVAL_", 
    55: "INT", 56: "INTID", 57: "INT_", 58: "LINE_COMMENT", 59: "MACHN_", 
    60: "MCAST_", 61: "MEM", 62: "MEM_", 63: "MINUS", 64: "MSG", 65: "MSGCSTR_", 
    66: "MSG_", 67: "MULT", 68: "NCOND_", 69: "NEG", 70: "NETWORK", 71: "NETWORK_", 
    72: "NEXT", 73: "NEXT_", 74: "NID", 75: "OBJSET_", 76: "OBRACE", 77: "OCBRACE", 
    78: "OEBRACE", 79: "PLUS", 80: "PROC", 81: "PROC_", 82: "RANGE_", 83: "SEMICOLON", 
    84: "SEND_", 85: "SET", 86: "SETFUNC_", 87: "SET_", 88: "STABLE", 89: "STABLE_", 
    90: "STALL", 91: "STALL_", 92: "STATE", 93: "TRANS_", 94: "UNDEF", 95: "UNDEF_", 
    96: "WHEN", 97: "WHEN_", 98: "WS"
}
Token.registerTokenNamesMap(tokenNamesMap)

class ProtoCCLexer(Lexer):

    grammarFileName = "/home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g"
    api_version = 1

    def __init__(self, input=None, state=None):
        if state is None:
            state = RecognizerSharedState()
        super().__init__(input, state)

        self.delegates = []

        self.dfa8 = self.DFA8(
            self, 8,
            eot = self.DFA8_eot,
            eof = self.DFA8_eof,
            min = self.DFA8_min,
            max = self.DFA8_max,
            accept = self.DFA8_accept,
            special = self.DFA8_special,
            transition = self.DFA8_transition
            )






    # $ANTLR start "ARCH"
    def mARCH(self, ):
        try:
            _type = ARCH
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:7:6: ( 'Architecture' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:7:8: 'Architecture'
            pass 
            self.match("Architecture")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "ARCH"



    # $ANTLR start "ARRAY"
    def mARRAY(self, ):
        try:
            _type = ARRAY
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:8:7: ( 'array' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:8:9: 'array'
            pass 
            self.match("array")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "ARRAY"



    # $ANTLR start "AWAIT"
    def mAWAIT(self, ):
        try:
            _type = AWAIT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:9:7: ( 'await' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:9:9: 'await'
            pass 
            self.match("await")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "AWAIT"



    # $ANTLR start "BOOLID"
    def mBOOLID(self, ):
        try:
            _type = BOOLID
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:10:8: ( 'bool' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:10:10: 'bool'
            pass 
            self.match("bool")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "BOOLID"



    # $ANTLR start "BREAK"
    def mBREAK(self, ):
        try:
            _type = BREAK
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:11:7: ( 'break' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:11:9: 'break'
            pass 
            self.match("break")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "BREAK"



    # $ANTLR start "CACHE"
    def mCACHE(self, ):
        try:
            _type = CACHE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:12:7: ( 'Cache' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:12:9: 'Cache'
            pass 
            self.match("Cache")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "CACHE"



    # $ANTLR start "CBRACE"
    def mCBRACE(self, ):
        try:
            _type = CBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:13:8: ( ')' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:13:10: ')'
            pass 
            self.match(41)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "CBRACE"



    # $ANTLR start "CCBRACE"
    def mCCBRACE(self, ):
        try:
            _type = CCBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:14:9: ( '}' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:14:11: '}'
            pass 
            self.match(125)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "CCBRACE"



    # $ANTLR start "CEBRACE"
    def mCEBRACE(self, ):
        try:
            _type = CEBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:15:9: ( ']' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:15:11: ']'
            pass 
            self.match(93)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "CEBRACE"



    # $ANTLR start "COMMA"
    def mCOMMA(self, ):
        try:
            _type = COMMA
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:16:7: ( ',' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:16:9: ','
            pass 
            self.match(44)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "COMMA"



    # $ANTLR start "CONSTANT"
    def mCONSTANT(self, ):
        try:
            _type = CONSTANT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:17:10: ( '#' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:17:12: '#'
            pass 
            self.match(35)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "CONSTANT"



    # $ANTLR start "DATA"
    def mDATA(self, ):
        try:
            _type = DATA
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:18:6: ( 'Data' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:18:8: 'Data'
            pass 
            self.match("Data")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "DATA"



    # $ANTLR start "DDOT"
    def mDDOT(self, ):
        try:
            _type = DDOT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:19:6: ( ':' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:19:8: ':'
            pass 
            self.match(58)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "DDOT"



    # $ANTLR start "DIR"
    def mDIR(self, ):
        try:
            _type = DIR
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:20:5: ( 'Directory' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:20:7: 'Directory'
            pass 
            self.match("Directory")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "DIR"



    # $ANTLR start "DOT"
    def mDOT(self, ):
        try:
            _type = DOT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:21:5: ( '.' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:21:7: '.'
            pass 
            self.match(46)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "DOT"



    # $ANTLR start "ELSE"
    def mELSE(self, ):
        try:
            _type = ELSE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:22:6: ( 'else' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:22:8: 'else'
            pass 
            self.match("else")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "ELSE"



    # $ANTLR start "EQUALSIGN"
    def mEQUALSIGN(self, ):
        try:
            _type = EQUALSIGN
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:23:11: ( '=' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:23:13: '='
            pass 
            self.match(61)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "EQUALSIGN"



    # $ANTLR start "FIFO"
    def mFIFO(self, ):
        try:
            _type = FIFO
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:24:6: ( 'FIFO' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:24:8: 'FIFO'
            pass 
            self.match("FIFO")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "FIFO"



    # $ANTLR start "IF"
    def mIF(self, ):
        try:
            _type = IF
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:25:4: ( 'if' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:25:6: 'if'
            pass 
            self.match("if")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "IF"



    # $ANTLR start "INTID"
    def mINTID(self, ):
        try:
            _type = INTID
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:26:7: ( 'int' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:26:9: 'int'
            pass 
            self.match("int")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "INTID"



    # $ANTLR start "MEM"
    def mMEM(self, ):
        try:
            _type = MEM
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:27:5: ( 'Memory' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:27:7: 'Memory'
            pass 
            self.match("Memory")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "MEM"



    # $ANTLR start "MINUS"
    def mMINUS(self, ):
        try:
            _type = MINUS
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:28:7: ( '-' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:28:9: '-'
            pass 
            self.match(45)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "MINUS"



    # $ANTLR start "MSG"
    def mMSG(self, ):
        try:
            _type = MSG
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:29:5: ( 'Message' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:29:7: 'Message'
            pass 
            self.match("Message")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "MSG"



    # $ANTLR start "MULT"
    def mMULT(self, ):
        try:
            _type = MULT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:30:6: ( '*' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:30:8: '*'
            pass 
            self.match(42)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "MULT"



    # $ANTLR start "NEG"
    def mNEG(self, ):
        try:
            _type = NEG
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:31:5: ( '!' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:31:7: '!'
            pass 
            self.match(33)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "NEG"



    # $ANTLR start "NETWORK"
    def mNETWORK(self, ):
        try:
            _type = NETWORK
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:32:9: ( 'Network' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:32:11: 'Network'
            pass 
            self.match("Network")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "NETWORK"



    # $ANTLR start "NEXT"
    def mNEXT(self, ):
        try:
            _type = NEXT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:33:6: ( 'next' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:33:8: 'next'
            pass 
            self.match("next")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "NEXT"



    # $ANTLR start "NID"
    def mNID(self, ):
        try:
            _type = NID
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:34:5: ( 'ID' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:34:7: 'ID'
            pass 
            self.match("ID")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "NID"



    # $ANTLR start "OBRACE"
    def mOBRACE(self, ):
        try:
            _type = OBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:35:8: ( '(' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:35:10: '('
            pass 
            self.match(40)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "OBRACE"



    # $ANTLR start "OCBRACE"
    def mOCBRACE(self, ):
        try:
            _type = OCBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:36:9: ( '{' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:36:11: '{'
            pass 
            self.match(123)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "OCBRACE"



    # $ANTLR start "OEBRACE"
    def mOEBRACE(self, ):
        try:
            _type = OEBRACE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:37:9: ( '[' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:37:11: '['
            pass 
            self.match(91)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "OEBRACE"



    # $ANTLR start "PLUS"
    def mPLUS(self, ):
        try:
            _type = PLUS
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:38:6: ( '+' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:38:8: '+'
            pass 
            self.match(43)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "PLUS"



    # $ANTLR start "PROC"
    def mPROC(self, ):
        try:
            _type = PROC
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:39:6: ( 'Process' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:39:8: 'Process'
            pass 
            self.match("Process")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "PROC"



    # $ANTLR start "SEMICOLON"
    def mSEMICOLON(self, ):
        try:
            _type = SEMICOLON
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:40:11: ( ';' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:40:13: ';'
            pass 
            self.match(59)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "SEMICOLON"



    # $ANTLR start "SET"
    def mSET(self, ):
        try:
            _type = SET
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:41:5: ( 'set' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:41:7: 'set'
            pass 
            self.match("set")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "SET"



    # $ANTLR start "STABLE"
    def mSTABLE(self, ):
        try:
            _type = STABLE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:42:8: ( 'Stable' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:42:10: 'Stable'
            pass 
            self.match("Stable")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "STABLE"



    # $ANTLR start "STALL"
    def mSTALL(self, ):
        try:
            _type = STALL
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:43:7: ( 'stall' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:43:9: 'stall'
            pass 
            self.match("stall")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "STALL"



    # $ANTLR start "STATE"
    def mSTATE(self, ):
        try:
            _type = STATE
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:44:7: ( 'State' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:44:9: 'State'
            pass 
            self.match("State")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "STATE"



    # $ANTLR start "UNDEF"
    def mUNDEF(self, ):
        try:
            _type = UNDEF
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:45:7: ( 'undefine' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:45:9: 'undefine'
            pass 
            self.match("undefine")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "UNDEF"



    # $ANTLR start "WHEN"
    def mWHEN(self, ):
        try:
            _type = WHEN
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:46:6: ( 'when' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:46:8: 'when'
            pass 
            self.match("when")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "WHEN"



    # $ANTLR start "T__99"
    def mT__99(self, ):
        try:
            _type = T__99
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:47:7: ( '!=' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:47:9: '!='
            pass 
            self.match("!=")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__99"



    # $ANTLR start "T__100"
    def mT__100(self, ):
        try:
            _type = T__100
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:48:8: ( '&' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:48:10: '&'
            pass 
            self.match(38)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__100"



    # $ANTLR start "T__101"
    def mT__101(self, ):
        try:
            _type = T__101
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:49:8: ( '<' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:49:10: '<'
            pass 
            self.match(60)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__101"



    # $ANTLR start "T__102"
    def mT__102(self, ):
        try:
            _type = T__102
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:50:8: ( '<=' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:50:10: '<='
            pass 
            self.match("<=")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__102"



    # $ANTLR start "T__103"
    def mT__103(self, ):
        try:
            _type = T__103
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:51:8: ( '==' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:51:10: '=='
            pass 
            self.match("==")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__103"



    # $ANTLR start "T__104"
    def mT__104(self, ):
        try:
            _type = T__104
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:52:8: ( '>' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:52:10: '>'
            pass 
            self.match(62)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__104"



    # $ANTLR start "T__105"
    def mT__105(self, ):
        try:
            _type = T__105
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:53:8: ( '>=' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:53:10: '>='
            pass 
            self.match(">=")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__105"



    # $ANTLR start "T__106"
    def mT__106(self, ):
        try:
            _type = T__106
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:54:8: ( 'Bcast' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:54:10: 'Bcast'
            pass 
            self.match("Bcast")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__106"



    # $ANTLR start "T__107"
    def mT__107(self, ):
        try:
            _type = T__107
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:55:8: ( 'Event' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:55:10: 'Event'
            pass 
            self.match("Event")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__107"



    # $ANTLR start "T__108"
    def mT__108(self, ):
        try:
            _type = T__108
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:56:8: ( 'Mcast' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:56:10: 'Mcast'
            pass 
            self.match("Mcast")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__108"



    # $ANTLR start "T__109"
    def mT__109(self, ):
        try:
            _type = T__109
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:57:8: ( 'Ordered' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:57:10: 'Ordered'
            pass 
            self.match("Ordered")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__109"



    # $ANTLR start "T__110"
    def mT__110(self, ):
        try:
            _type = T__110
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:58:8: ( 'Send' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:58:10: 'Send'
            pass 
            self.match("Send")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__110"



    # $ANTLR start "T__111"
    def mT__111(self, ):
        try:
            _type = T__111
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:59:8: ( 'Unordered' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:59:10: 'Unordered'
            pass 
            self.match("Unordered")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__111"



    # $ANTLR start "T__112"
    def mT__112(self, ):
        try:
            _type = T__112
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:60:8: ( 'add' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:60:10: 'add'
            pass 
            self.match("add")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__112"



    # $ANTLR start "T__113"
    def mT__113(self, ):
        try:
            _type = T__113
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:61:8: ( 'bcast' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:61:10: 'bcast'
            pass 
            self.match("bcast")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__113"



    # $ANTLR start "T__114"
    def mT__114(self, ):
        try:
            _type = T__114
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:62:8: ( 'clear' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:62:10: 'clear'
            pass 
            self.match("clear")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__114"



    # $ANTLR start "T__115"
    def mT__115(self, ):
        try:
            _type = T__115
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:63:8: ( 'contains' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:63:10: 'contains'
            pass 
            self.match("contains")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__115"



    # $ANTLR start "T__116"
    def mT__116(self, ):
        try:
            _type = T__116
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:64:8: ( 'count' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:64:10: 'count'
            pass 
            self.match("count")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__116"



    # $ANTLR start "T__117"
    def mT__117(self, ):
        try:
            _type = T__117
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:65:8: ( 'del' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:65:10: 'del'
            pass 
            self.match("del")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__117"



    # $ANTLR start "T__118"
    def mT__118(self, ):
        try:
            _type = T__118
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:66:8: ( 'mcast' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:66:10: 'mcast'
            pass 
            self.match("mcast")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__118"



    # $ANTLR start "T__119"
    def mT__119(self, ):
        try:
            _type = T__119
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:67:8: ( 'send' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:67:10: 'send'
            pass 
            self.match("send")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__119"



    # $ANTLR start "T__120"
    def mT__120(self, ):
        try:
            _type = T__120
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:68:8: ( '|' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:68:10: '|'
            pass 
            self.match(124)



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "T__120"



    # $ANTLR start "WS"
    def mWS(self, ):
        try:
            _type = WS
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:165:5: ( ( ' ' | '\\t' | '\\r' | '\\n' ) )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:165:9: ( ' ' | '\\t' | '\\r' | '\\n' )
            pass 
            if self.input.LA(1) in {9, 10, 13, 32}:
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse



            #action start
            _channel=HIDDEN;
            #action end




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "WS"



    # $ANTLR start "COMMENT"
    def mCOMMENT(self, ):
        try:
            _type = COMMENT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:173:5: ( '/*' ( options {greedy=false; } : . )* '*/' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:173:9: '/*' ( options {greedy=false; } : . )* '*/'
            pass 
            self.match("/*")


            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:173:14: ( options {greedy=false; } : . )*
            while True: #loop1
                alt1 = 2
                LA1_0 = self.input.LA(1)

                if (LA1_0 == 42) :
                    LA1_1 = self.input.LA(2)

                    if (LA1_1 == 47) :
                        alt1 = 2
                    elif ((0 <= LA1_1 <= 46) or (48 <= LA1_1 <= 65535) or LA1_1 in {}) :
                        alt1 = 1


                elif ((0 <= LA1_0 <= 41) or (43 <= LA1_0 <= 65535) or LA1_0 in {}) :
                    alt1 = 1


                if alt1 == 1:
                    # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:173:42: .
                    pass 
                    self.matchAny()


                else:
                    break #loop1


            self.match("*/")


            #action start
            _channel=HIDDEN;
            #action end




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "COMMENT"



    # $ANTLR start "LINE_COMMENT"
    def mLINE_COMMENT(self, ):
        try:
            _type = LINE_COMMENT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:177:5: ( '//' (~ ( '\\n' | '\\r' ) )* ( '\\r' )? '\\n' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:177:7: '//' (~ ( '\\n' | '\\r' ) )* ( '\\r' )? '\\n'
            pass 
            self.match("//")


            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:177:12: (~ ( '\\n' | '\\r' ) )*
            while True: #loop2
                alt2 = 2
                LA2_0 = self.input.LA(1)

                if ((0 <= LA2_0 <= 9) or (14 <= LA2_0 <= 65535) or LA2_0 in {11, 12}) :
                    alt2 = 1


                if alt2 == 1:
                    # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:
                    pass 
                    if (0 <= self.input.LA(1) <= 9) or (14 <= self.input.LA(1) <= 65535) or self.input.LA(1) in {11, 12}:
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse




                else:
                    break #loop2


            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:177:26: ( '\\r' )?
            alt3 = 2
            LA3_0 = self.input.LA(1)

            if (LA3_0 == 13) :
                alt3 = 1
            if alt3 == 1:
                # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:177:26: '\\r'
                pass 
                self.match(13)




            self.match(10)

            #action start
            _channel=HIDDEN;
            #action end




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "LINE_COMMENT"



    # $ANTLR start "BOOL"
    def mBOOL(self, ):
        try:
            _type = BOOL
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:182:5: ( 'true' | 'false' )
            alt4 = 2
            LA4_0 = self.input.LA(1)

            if (LA4_0 == 116) :
                alt4 = 1
            elif (LA4_0 == 102) :
                alt4 = 2
            else:
                nvae = NoViableAltException("", 4, 0, self.input)

                raise nvae


            if alt4 == 1:
                # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:182:9: 'true'
                pass 
                self.match("true")



            elif alt4 == 2:
                # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:182:18: 'false'
                pass 
                self.match("false")



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "BOOL"



    # $ANTLR start "INT"
    def mINT(self, ):
        try:
            _type = INT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:183:5: ( ( '0' .. '9' )+ )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:183:7: ( '0' .. '9' )+
            pass 
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:183:7: ( '0' .. '9' )+
            cnt5 = 0
            while True: #loop5
                alt5 = 2
                LA5_0 = self.input.LA(1)

                if ((48 <= LA5_0 <= 57) or LA5_0 in {}) :
                    alt5 = 1


                if alt5 == 1:
                    # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:
                    pass 
                    if (48 <= self.input.LA(1) <= 57) or self.input.LA(1) in {}:
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse




                else:
                    if cnt5 >= 1:
                        break #loop5

                    eee = EarlyExitException(5, self.input)
                    raise eee

                cnt5 += 1




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "INT"



    # $ANTLR start "ACCESS"
    def mACCESS(self, ):
        try:
            _type = ACCESS
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:185:7: ( 'load' | 'store' )
            alt6 = 2
            LA6_0 = self.input.LA(1)

            if (LA6_0 == 108) :
                alt6 = 1
            elif (LA6_0 == 115) :
                alt6 = 2
            else:
                nvae = NoViableAltException("", 6, 0, self.input)

                raise nvae


            if alt6 == 1:
                # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:185:9: 'load'
                pass 
                self.match("load")



            elif alt6 == 2:
                # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:185:18: 'store'
                pass 
                self.match("store")



            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "ACCESS"



    # $ANTLR start "EVICT"
    def mEVICT(self, ):
        try:
            _type = EVICT
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:186:6: ( 'evict' )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:186:8: 'evict'
            pass 
            self.match("evict")




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "EVICT"



    # $ANTLR start "ID"
    def mID(self, ):
        try:
            _type = ID
            _channel = DEFAULT_CHANNEL

            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:188:5: ( ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )* )
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:188:7: ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            pass 
            if (65 <= self.input.LA(1) <= 90) or (97 <= self.input.LA(1) <= 122) or self.input.LA(1) in {95}:
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse



            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:188:31: ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            while True: #loop7
                alt7 = 2
                LA7_0 = self.input.LA(1)

                if ((48 <= LA7_0 <= 57) or (65 <= LA7_0 <= 90) or (97 <= LA7_0 <= 122) or LA7_0 in {95}) :
                    alt7 = 1


                if alt7 == 1:
                    # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:
                    pass 
                    if (48 <= self.input.LA(1) <= 57) or (65 <= self.input.LA(1) <= 90) or (97 <= self.input.LA(1) <= 122) or self.input.LA(1) in {95}:
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse




                else:
                    break #loop7




            self._state.type = _type
            self._state.channel = _channel
        finally:
            pass

    # $ANTLR end "ID"



    def mTokens(self):
        # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:8: ( ARCH | ARRAY | AWAIT | BOOLID | BREAK | CACHE | CBRACE | CCBRACE | CEBRACE | COMMA | CONSTANT | DATA | DDOT | DIR | DOT | ELSE | EQUALSIGN | FIFO | IF | INTID | MEM | MINUS | MSG | MULT | NEG | NETWORK | NEXT | NID | OBRACE | OCBRACE | OEBRACE | PLUS | PROC | SEMICOLON | SET | STABLE | STALL | STATE | UNDEF | WHEN | T__99 | T__100 | T__101 | T__102 | T__103 | T__104 | T__105 | T__106 | T__107 | T__108 | T__109 | T__110 | T__111 | T__112 | T__113 | T__114 | T__115 | T__116 | T__117 | T__118 | T__119 | T__120 | WS | COMMENT | LINE_COMMENT | BOOL | INT | ACCESS | EVICT | ID )
        alt8 = 70
        alt8 = self.dfa8.predict(self.input)
        if alt8 == 1:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:10: ARCH
            pass 
            self.mARCH()



        elif alt8 == 2:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:15: ARRAY
            pass 
            self.mARRAY()



        elif alt8 == 3:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:21: AWAIT
            pass 
            self.mAWAIT()



        elif alt8 == 4:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:27: BOOLID
            pass 
            self.mBOOLID()



        elif alt8 == 5:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:34: BREAK
            pass 
            self.mBREAK()



        elif alt8 == 6:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:40: CACHE
            pass 
            self.mCACHE()



        elif alt8 == 7:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:46: CBRACE
            pass 
            self.mCBRACE()



        elif alt8 == 8:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:53: CCBRACE
            pass 
            self.mCCBRACE()



        elif alt8 == 9:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:61: CEBRACE
            pass 
            self.mCEBRACE()



        elif alt8 == 10:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:69: COMMA
            pass 
            self.mCOMMA()



        elif alt8 == 11:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:75: CONSTANT
            pass 
            self.mCONSTANT()



        elif alt8 == 12:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:84: DATA
            pass 
            self.mDATA()



        elif alt8 == 13:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:89: DDOT
            pass 
            self.mDDOT()



        elif alt8 == 14:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:94: DIR
            pass 
            self.mDIR()



        elif alt8 == 15:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:98: DOT
            pass 
            self.mDOT()



        elif alt8 == 16:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:102: ELSE
            pass 
            self.mELSE()



        elif alt8 == 17:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:107: EQUALSIGN
            pass 
            self.mEQUALSIGN()



        elif alt8 == 18:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:117: FIFO
            pass 
            self.mFIFO()



        elif alt8 == 19:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:122: IF
            pass 
            self.mIF()



        elif alt8 == 20:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:125: INTID
            pass 
            self.mINTID()



        elif alt8 == 21:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:131: MEM
            pass 
            self.mMEM()



        elif alt8 == 22:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:135: MINUS
            pass 
            self.mMINUS()



        elif alt8 == 23:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:141: MSG
            pass 
            self.mMSG()



        elif alt8 == 24:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:145: MULT
            pass 
            self.mMULT()



        elif alt8 == 25:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:150: NEG
            pass 
            self.mNEG()



        elif alt8 == 26:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:154: NETWORK
            pass 
            self.mNETWORK()



        elif alt8 == 27:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:162: NEXT
            pass 
            self.mNEXT()



        elif alt8 == 28:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:167: NID
            pass 
            self.mNID()



        elif alt8 == 29:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:171: OBRACE
            pass 
            self.mOBRACE()



        elif alt8 == 30:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:178: OCBRACE
            pass 
            self.mOCBRACE()



        elif alt8 == 31:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:186: OEBRACE
            pass 
            self.mOEBRACE()



        elif alt8 == 32:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:194: PLUS
            pass 
            self.mPLUS()



        elif alt8 == 33:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:199: PROC
            pass 
            self.mPROC()



        elif alt8 == 34:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:204: SEMICOLON
            pass 
            self.mSEMICOLON()



        elif alt8 == 35:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:214: SET
            pass 
            self.mSET()



        elif alt8 == 36:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:218: STABLE
            pass 
            self.mSTABLE()



        elif alt8 == 37:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:225: STALL
            pass 
            self.mSTALL()



        elif alt8 == 38:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:231: STATE
            pass 
            self.mSTATE()



        elif alt8 == 39:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:237: UNDEF
            pass 
            self.mUNDEF()



        elif alt8 == 40:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:243: WHEN
            pass 
            self.mWHEN()



        elif alt8 == 41:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:248: T__99
            pass 
            self.mT__99()



        elif alt8 == 42:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:254: T__100
            pass 
            self.mT__100()



        elif alt8 == 43:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:261: T__101
            pass 
            self.mT__101()



        elif alt8 == 44:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:268: T__102
            pass 
            self.mT__102()



        elif alt8 == 45:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:275: T__103
            pass 
            self.mT__103()



        elif alt8 == 46:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:282: T__104
            pass 
            self.mT__104()



        elif alt8 == 47:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:289: T__105
            pass 
            self.mT__105()



        elif alt8 == 48:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:296: T__106
            pass 
            self.mT__106()



        elif alt8 == 49:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:303: T__107
            pass 
            self.mT__107()



        elif alt8 == 50:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:310: T__108
            pass 
            self.mT__108()



        elif alt8 == 51:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:317: T__109
            pass 
            self.mT__109()



        elif alt8 == 52:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:324: T__110
            pass 
            self.mT__110()



        elif alt8 == 53:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:331: T__111
            pass 
            self.mT__111()



        elif alt8 == 54:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:338: T__112
            pass 
            self.mT__112()



        elif alt8 == 55:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:345: T__113
            pass 
            self.mT__113()



        elif alt8 == 56:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:352: T__114
            pass 
            self.mT__114()



        elif alt8 == 57:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:359: T__115
            pass 
            self.mT__115()



        elif alt8 == 58:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:366: T__116
            pass 
            self.mT__116()



        elif alt8 == 59:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:373: T__117
            pass 
            self.mT__117()



        elif alt8 == 60:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:380: T__118
            pass 
            self.mT__118()



        elif alt8 == 61:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:387: T__119
            pass 
            self.mT__119()



        elif alt8 == 62:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:394: T__120
            pass 
            self.mT__120()



        elif alt8 == 63:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:401: WS
            pass 
            self.mWS()



        elif alt8 == 64:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:404: COMMENT
            pass 
            self.mCOMMENT()



        elif alt8 == 65:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:412: LINE_COMMENT
            pass 
            self.mLINE_COMMENT()



        elif alt8 == 66:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:425: BOOL
            pass 
            self.mBOOL()



        elif alt8 == 67:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:430: INT
            pass 
            self.mINT()



        elif alt8 == 68:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:434: ACCESS
            pass 
            self.mACCESS()



        elif alt8 == 69:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:441: EVICT
            pass 
            self.mEVICT()



        elif alt8 == 70:
            # /home/tux/PycharmProjects/ProtoCCv2/Parser/ProtoCC.g:1:447: ID
            pass 
            self.mID()








    # lookup tables for DFA #8

    DFA8_eot = DFA.unpack(
        "\1\uffff\4\63\5\uffff\1\63\2\uffff\1\63\1\101\3\63\2\uffff\1\110"
        "\3\63\4\uffff\1\63\1\uffff\4\63\1\uffff\1\124\1\126\7\63\3\uffff"
        "\2\63\1\uffff\1\63\1\uffff\14\63\2\uffff\1\63\1\161\3\63\2\uffff"
        "\2\63\1\170\7\63\4\uffff\10\63\2\uffff\6\63\1\u0091\11\63\1\uffff"
        "\1\u009b\5\63\1\uffff\1\63\1\u00a2\16\63\1\u00b2\7\63\1\uffff\1"
        "\u00ba\3\63\1\u00be\1\63\1\u00c0\1\63\1\u00c2\1\uffff\4\63\1\u00c7"
        "\1\63\1\uffff\1\u00c9\4\63\1\u00ce\1\63\1\u00d0\7\63\1\uffff\1\63"
        "\1\u00d9\1\63\1\u00db\1\63\1\u00dd\1\u00de\1\uffff\1\u00df\1\u00e0"
        "\1\u00e1\1\uffff\1\63\1\uffff\1\u00e3\1\uffff\2\63\1\u00e6\1\63"
        "\1\uffff\1\63\1\uffff\1\u00e9\1\u00db\1\63\1\u00eb\1\uffff\1\63"
        "\1\uffff\1\u00ed\1\u00ee\2\63\1\u00f1\1\63\1\u00f3\1\u00f4\1\uffff"
        "\1\u00d9\1\uffff\1\63\5\uffff\1\63\1\uffff\1\u00f7\1\63\1\uffff"
        "\2\63\1\uffff\1\u00fb\1\uffff\1\63\2\uffff\2\63\1\uffff\1\63\2\uffff"
        "\2\63\1\uffff\1\u0102\1\u0103\1\u0104\1\uffff\1\63\1\u0106\4\63"
        "\3\uffff\1\u010b\1\uffff\1\63\1\u010d\1\63\1\u010f\1\uffff\1\u0110"
        "\1\uffff\1\63\2\uffff\1\63\1\u0113\1\uffff"
        )

    DFA8_eof = DFA.unpack(
        "\u0114\uffff"
        )

    DFA8_min = DFA.unpack(
        "\1\11\1\162\1\144\1\143\1\141\5\uffff\1\141\2\uffff\1\154\1\75\1"
        "\111\1\146\1\143\2\uffff\1\75\2\145\1\104\4\uffff\1\162\1\uffff"
        "\2\145\1\156\1\150\1\uffff\2\75\1\143\1\166\1\162\1\156\1\154\1"
        "\145\1\143\2\uffff\1\52\1\162\1\141\1\uffff\1\157\1\uffff\1\143"
        "\1\162\1\141\1\144\1\157\1\145\1\141\1\143\1\164\1\162\1\163\1\151"
        "\2\uffff\1\106\1\60\1\164\1\155\1\141\2\uffff\1\164\1\170\1\60\1"
        "\157\1\156\2\141\1\156\1\144\1\145\4\uffff\1\141\1\145\1\144\1\157"
        "\1\145\1\156\1\154\1\141\2\uffff\1\165\1\154\1\141\1\150\1\141\1"
        "\151\1\60\1\154\1\141\1\163\1\150\1\141\2\145\1\143\1\117\1\uffff"
        "\1\60\1\157\2\163\1\167\1\164\1\uffff\1\143\1\60\1\144\1\154\1\162"
        "\1\142\1\144\1\145\1\156\1\163\1\156\1\145\1\162\1\141\1\164\1\156"
        "\1\60\1\163\1\145\1\163\1\144\1\151\1\171\1\164\1\uffff\1\60\1\153"
        "\1\164\1\145\1\60\1\143\1\60\1\164\1\60\1\uffff\1\162\1\141\1\164"
        "\1\157\1\60\1\145\1\uffff\1\60\1\154\1\145\1\154\1\145\1\60\1\146"
        "\1\60\2\164\1\162\1\144\1\162\1\141\1\164\1\uffff\1\164\1\60\1\145"
        "\1\60\1\164\2\60\1\uffff\3\60\1\uffff\1\164\1\uffff\1\60\1\uffff"
        "\1\171\1\147\1\60\1\162\1\uffff\1\163\1\uffff\2\60\1\145\1\60\1"
        "\uffff\1\151\1\uffff\2\60\2\145\1\60\1\151\2\60\1\uffff\1\60\1\uffff"
        "\1\145\5\uffff\1\157\1\uffff\1\60\1\145\1\uffff\1\153\1\163\1\uffff"
        "\1\60\1\uffff\1\156\2\uffff\1\144\1\162\1\uffff\1\156\2\uffff\1"
        "\143\1\162\1\uffff\3\60\1\uffff\1\145\1\60\1\145\1\163\1\164\1\171"
        "\3\uffff\1\60\1\uffff\1\144\1\60\1\165\1\60\1\uffff\1\60\1\uffff"
        "\1\162\2\uffff\1\145\1\60\1\uffff"
        )

    DFA8_max = DFA.unpack(
        "\1\175\1\162\1\167\1\162\1\141\5\uffff\1\151\2\uffff\1\166\1\75"
        "\1\111\1\156\1\145\2\uffff\1\75\2\145\1\104\4\uffff\1\162\1\uffff"
        "\2\164\1\156\1\150\1\uffff\2\75\1\143\1\166\1\162\1\156\1\157\1"
        "\145\1\143\2\uffff\1\57\1\162\1\141\1\uffff\1\157\1\uffff\1\143"
        "\1\162\1\141\1\144\1\157\1\145\1\141\1\143\1\164\1\162\1\163\1\151"
        "\2\uffff\1\106\1\172\1\164\1\163\1\141\2\uffff\1\164\1\170\1\172"
        "\1\157\1\164\1\157\1\141\1\156\1\144\1\145\4\uffff\1\141\1\145\1"
        "\144\1\157\1\145\1\165\1\154\1\141\2\uffff\1\165\1\154\1\141\1\150"
        "\1\141\1\151\1\172\1\154\1\141\1\163\1\150\1\141\2\145\1\143\1\117"
        "\1\uffff\1\172\1\157\2\163\1\167\1\164\1\uffff\1\143\1\172\1\144"
        "\1\154\1\162\1\164\1\144\1\145\1\156\1\163\1\156\1\145\1\162\1\141"
        "\1\164\1\156\1\172\1\163\1\145\1\163\1\144\1\151\1\171\1\164\1\uffff"
        "\1\172\1\153\1\164\1\145\1\172\1\143\1\172\1\164\1\172\1\uffff\1"
        "\162\1\141\1\164\1\157\1\172\1\145\1\uffff\1\172\1\154\1\145\1\154"
        "\1\145\1\172\1\146\1\172\2\164\1\162\1\144\1\162\1\141\1\164\1\uffff"
        "\1\164\1\172\1\145\1\172\1\164\2\172\1\uffff\3\172\1\uffff\1\164"
        "\1\uffff\1\172\1\uffff\1\171\1\147\1\172\1\162\1\uffff\1\163\1\uffff"
        "\2\172\1\145\1\172\1\uffff\1\151\1\uffff\2\172\2\145\1\172\1\151"
        "\2\172\1\uffff\1\172\1\uffff\1\145\5\uffff\1\157\1\uffff\1\172\1"
        "\145\1\uffff\1\153\1\163\1\uffff\1\172\1\uffff\1\156\2\uffff\1\144"
        "\1\162\1\uffff\1\156\2\uffff\1\143\1\162\1\uffff\3\172\1\uffff\1"
        "\145\1\172\1\145\1\163\1\164\1\171\3\uffff\1\172\1\uffff\1\144\1"
        "\172\1\165\1\172\1\uffff\1\172\1\uffff\1\162\2\uffff\1\145\1\172"
        "\1\uffff"
        )

    DFA8_accept = DFA.unpack(
        "\5\uffff\1\7\1\10\1\11\1\12\1\13\1\uffff\1\15\1\17\5\uffff\1\26"
        "\1\30\4\uffff\1\35\1\36\1\37\1\40\1\uffff\1\42\4\uffff\1\52\11\uffff"
        "\1\76\1\77\3\uffff\1\103\1\uffff\1\106\14\uffff\1\55\1\21\5\uffff"
        "\1\51\1\31\12\uffff\1\54\1\53\1\57\1\56\10\uffff\1\100\1\101\20"
        "\uffff\1\23\6\uffff\1\34\30\uffff\1\66\11\uffff\1\24\6\uffff\1\43"
        "\17\uffff\1\73\7\uffff\1\4\3\uffff\1\14\1\uffff\1\20\1\uffff\1\22"
        "\4\uffff\1\33\1\uffff\1\75\4\uffff\1\64\1\uffff\1\50\10\uffff\1"
        "\102\1\uffff\1\104\1\uffff\1\2\1\3\1\5\1\67\1\6\1\uffff\1\105\2"
        "\uffff\1\62\2\uffff\1\45\1\uffff\1\46\1\uffff\1\60\1\61\2\uffff"
        "\1\70\1\uffff\1\72\1\74\2\uffff\1\25\3\uffff\1\44\6\uffff\1\27\1"
        "\32\1\41\1\uffff\1\63\4\uffff\1\47\1\uffff\1\71\1\uffff\1\16\1\65"
        "\2\uffff\1\1"
        )

    DFA8_special = DFA.unpack(
        "\u0114\uffff"
        )


    DFA8_transition = [
        DFA.unpack("\2\55\2\uffff\1\55\22\uffff\1\55\1\24\1\uffff\1\11\2"
        "\uffff\1\42\1\uffff\1\30\1\5\1\23\1\33\1\10\1\22\1\14\1\56\12\61"
        "\1\13\1\35\1\43\1\16\1\44\2\uffff\1\1\1\45\1\4\1\12\1\46\1\17\2"
        "\63\1\27\3\63\1\21\1\25\1\47\1\34\2\63\1\37\1\63\1\50\5\63\1\32"
        "\1\uffff\1\7\1\uffff\1\63\1\uffff\1\2\1\3\1\51\1\52\1\15\1\60\2"
        "\63\1\20\2\63\1\62\1\53\1\26\4\63\1\36\1\57\1\40\1\63\1\41\3\63"
        "\1\31\1\54\1\6"),
        DFA.unpack("\1\64"),
        DFA.unpack("\1\67\15\uffff\1\65\4\uffff\1\66"),
        DFA.unpack("\1\72\13\uffff\1\70\2\uffff\1\71"),
        DFA.unpack("\1\73"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\74\7\uffff\1\75"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\76\11\uffff\1\77"),
        DFA.unpack("\1\100"),
        DFA.unpack("\1\102"),
        DFA.unpack("\1\103\7\uffff\1\104"),
        DFA.unpack("\1\106\1\uffff\1\105"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\107"),
        DFA.unpack("\1\111"),
        DFA.unpack("\1\112"),
        DFA.unpack("\1\113"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\114"),
        DFA.unpack(""),
        DFA.unpack("\1\115\16\uffff\1\116"),
        DFA.unpack("\1\120\16\uffff\1\117"),
        DFA.unpack("\1\121"),
        DFA.unpack("\1\122"),
        DFA.unpack(""),
        DFA.unpack("\1\123"),
        DFA.unpack("\1\125"),
        DFA.unpack("\1\127"),
        DFA.unpack("\1\130"),
        DFA.unpack("\1\131"),
        DFA.unpack("\1\132"),
        DFA.unpack("\1\133\2\uffff\1\134"),
        DFA.unpack("\1\135"),
        DFA.unpack("\1\136"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\137\4\uffff\1\140"),
        DFA.unpack("\1\141"),
        DFA.unpack("\1\142"),
        DFA.unpack(""),
        DFA.unpack("\1\143"),
        DFA.unpack(""),
        DFA.unpack("\1\144"),
        DFA.unpack("\1\145"),
        DFA.unpack("\1\146"),
        DFA.unpack("\1\147"),
        DFA.unpack("\1\150"),
        DFA.unpack("\1\151"),
        DFA.unpack("\1\152"),
        DFA.unpack("\1\153"),
        DFA.unpack("\1\154"),
        DFA.unpack("\1\155"),
        DFA.unpack("\1\156"),
        DFA.unpack("\1\157"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\160"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\162"),
        DFA.unpack("\1\163\5\uffff\1\164"),
        DFA.unpack("\1\165"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\166"),
        DFA.unpack("\1\167"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\171"),
        DFA.unpack("\1\173\5\uffff\1\172"),
        DFA.unpack("\1\174\15\uffff\1\175"),
        DFA.unpack("\1\176"),
        DFA.unpack("\1\177"),
        DFA.unpack("\1\u0080"),
        DFA.unpack("\1\u0081"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u0082"),
        DFA.unpack("\1\u0083"),
        DFA.unpack("\1\u0084"),
        DFA.unpack("\1\u0085"),
        DFA.unpack("\1\u0086"),
        DFA.unpack("\1\u0087\6\uffff\1\u0088"),
        DFA.unpack("\1\u0089"),
        DFA.unpack("\1\u008a"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u008b"),
        DFA.unpack("\1\u008c"),
        DFA.unpack("\1\u008d"),
        DFA.unpack("\1\u008e"),
        DFA.unpack("\1\u008f"),
        DFA.unpack("\1\u0090"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u0092"),
        DFA.unpack("\1\u0093"),
        DFA.unpack("\1\u0094"),
        DFA.unpack("\1\u0095"),
        DFA.unpack("\1\u0096"),
        DFA.unpack("\1\u0097"),
        DFA.unpack("\1\u0098"),
        DFA.unpack("\1\u0099"),
        DFA.unpack("\1\u009a"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u009c"),
        DFA.unpack("\1\u009d"),
        DFA.unpack("\1\u009e"),
        DFA.unpack("\1\u009f"),
        DFA.unpack("\1\u00a0"),
        DFA.unpack(""),
        DFA.unpack("\1\u00a1"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00a3"),
        DFA.unpack("\1\u00a4"),
        DFA.unpack("\1\u00a5"),
        DFA.unpack("\1\u00a6\21\uffff\1\u00a7"),
        DFA.unpack("\1\u00a8"),
        DFA.unpack("\1\u00a9"),
        DFA.unpack("\1\u00aa"),
        DFA.unpack("\1\u00ab"),
        DFA.unpack("\1\u00ac"),
        DFA.unpack("\1\u00ad"),
        DFA.unpack("\1\u00ae"),
        DFA.unpack("\1\u00af"),
        DFA.unpack("\1\u00b0"),
        DFA.unpack("\1\u00b1"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00b3"),
        DFA.unpack("\1\u00b4"),
        DFA.unpack("\1\u00b5"),
        DFA.unpack("\1\u00b6"),
        DFA.unpack("\1\u00b7"),
        DFA.unpack("\1\u00b8"),
        DFA.unpack("\1\u00b9"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00bb"),
        DFA.unpack("\1\u00bc"),
        DFA.unpack("\1\u00bd"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00bf"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00c1"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00c3"),
        DFA.unpack("\1\u00c4"),
        DFA.unpack("\1\u00c5"),
        DFA.unpack("\1\u00c6"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00c8"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00ca"),
        DFA.unpack("\1\u00cb"),
        DFA.unpack("\1\u00cc"),
        DFA.unpack("\1\u00cd"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00cf"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00d1"),
        DFA.unpack("\1\u00d2"),
        DFA.unpack("\1\u00d3"),
        DFA.unpack("\1\u00d4"),
        DFA.unpack("\1\u00d5"),
        DFA.unpack("\1\u00d6"),
        DFA.unpack("\1\u00d7"),
        DFA.unpack(""),
        DFA.unpack("\1\u00d8"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00da"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00dc"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00e2"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00e4"),
        DFA.unpack("\1\u00e5"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00e7"),
        DFA.unpack(""),
        DFA.unpack("\1\u00e8"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00ea"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00ec"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00ef"),
        DFA.unpack("\1\u00f0"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00f2"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00f5"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u00f6"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u00f8"),
        DFA.unpack(""),
        DFA.unpack("\1\u00f9"),
        DFA.unpack("\1\u00fa"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u00fc"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u00fd"),
        DFA.unpack("\1\u00fe"),
        DFA.unpack(""),
        DFA.unpack("\1\u00ff"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u0100"),
        DFA.unpack("\1\u0101"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u0105"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u0107"),
        DFA.unpack("\1\u0108"),
        DFA.unpack("\1\u0109"),
        DFA.unpack("\1\u010a"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u010c"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("\1\u010e"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack(""),
        DFA.unpack("\1\u0111"),
        DFA.unpack(""),
        DFA.unpack(""),
        DFA.unpack("\1\u0112"),
        DFA.unpack("\12\63\7\uffff\32\63\4\uffff\1\63\1\uffff\32\63"),
        DFA.unpack("")
    ]

    # class definition for DFA #8

    class DFA8(DFA):
        pass


 



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import LexerMain
    main = LexerMain(ProtoCCLexer)

    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)



if __name__ == '__main__':
    main(sys.argv)
