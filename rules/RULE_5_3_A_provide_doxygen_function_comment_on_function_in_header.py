"""
Provide the function doxygen comment.
It detects if there is doxygen sytle comments in front of each functions in the header.
It only checks public, protected as well as private funcions.

== Violation ==

 = a.h =
    void FunctionA();  <== Violation. No doxygen comment.

    /*        <== Violation. It's not a doxygen comment
     *
     */
    void FunctionB();

    class A {
        private :
            void FunctionC(); <== Violation. doxygen comment still required in private function.
    }

    class A {
        public :
            ///
            void FunctionC(); <== Violation. doxygen comment in C++ style is not accepted.
    }

== Good ==

   = a.h =
    /**
     * blar blar
     */
    void FunctionA(); <== OK

    /**
     * blar
     */
    void FunctionB() {  <== OK.
    }

  = a.c =
     void FunctionD(); <== Don't care. it's defined in c file.
"""

from nsiqcppstyle_rulehelper import  *
from nsiqcppstyle_rulemanager import *


def RunRule(lexer, fullName, decl, contextStack, context) :
    ext = lexer.filename[lexer.filename.rfind("."):]
    if ext == ".h" :
        upperBlock = contextStack.SigPeek()

        t = lexer.GetCurToken()

        lexer.PushTokenIndex()
        t2 = lexer.GetPrevTokenInType("COMMENT")
        lexer.PopTokenIndex()
        lexer.PushTokenIndex()
        t3 = lexer.GetPrevTokenInTypeList(["SEMI", "PREPROCESSOR"], False, True)
        lexer.PopTokenIndex()
        if t2 != None and t2.additional == "DOXYGEN" :
            if t3 == None or t2.lexpos > t3.lexpos :
                return
        nsiqcppstyle_reporter.Error(t, __name__,
              "Doxygen Comment should be provided in front of function (%s) in header." % fullName)
ruleManager.AddFunctionNameRule(RunRule)


def RunTypeScopeRule(lexer, contextStack) :
    t = lexer.GetCurToken()
    if t.type in ["PUBLIC", "PRIVATE", "PROTECTED"] :
        curContext = contextStack.SigPeek()
        if curContext.type in ["CLASS_BLOCK", "STRUCT_BLOCK"]:
            curContext.additional = t.type

ruleManager.AddTypeScopeRule(RunTypeScopeRule)




###########################################################################################
# Unit Test
###########################################################################################

from nsiqunittest.nsiqcppstyle_unittestbase import *
class testRule(nct):
    def setUpRule(self):
        ruleManager.AddFunctionNameRule(RunRule)
        ruleManager.AddTypeScopeRule(RunTypeScopeRule)
    def test1(self):
        self.Analyze("thisfile.h",
"""
void FunctionA();
""")
        assert CheckErrorContent(__name__)
    def test2(self):
        self.Analyze("thisfile.h",
"""
/*
 *
 */
extern void FunctionB();
""")
        assert CheckErrorContent(__name__)
    def test3(self):
        self.Analyze("thisfile.h",
"""
class A {
public:
    void ~A();
}
""")
        assert CheckErrorContent(__name__)
    def test4(self):
        self.Analyze("thisfile.h",
"""
class J {
public :
    /** HELLO */
    A();
}
""")
        assert not CheckErrorContent(__name__)
    def test5(self):
        self.Analyze("thisfile.h",
"""
/*
 *
 */
 void FunctionB() {
}
""")
        assert CheckErrorContent(__name__)

    def test6(self):
        self.Analyze("thisfile.h",
"""
int a;
 void FunctionB();
""")
        assert CheckErrorContent(__name__)

    def test7(self):
        self.Analyze("thisfile.h",
"""
/**
 *
 */
extern void FunctionB();
""")
        assert not CheckErrorContent(__name__)

    def test8(self):
        self.Analyze("thisfile.h",
"""
class J {
protected :
    /** HELLO */
    A();
private :
    B();
    C() {
    }
}
""")
        assert CheckErrorContent(__name__)

    def test9(self):
        self.Analyze("thisfile.h",
"""
///
extern void FunctionB();
""")
        assert CheckErrorContent(__name__)

    def test10(self):
        self.Analyze("thisfile.h",
"""
class J {
public :
    /// HELLO
    A();
}
""")
        assert CheckErrorContent(__name__)

    def test11(self):
        self.Analyze("thisfile.h",
"""
extern void FunctionB();  ///< HELLO
""")
        assert CheckErrorContent(__name__)

    def test12(self):
        self.Analyze("thisfile.h",
"""
class J {
public :
    A();  ///< HELLO
}
""")
        assert CheckErrorContent(__name__)

    def test13(self):
        self.Analyze("thisfile.c",
"""
void FunctionA();
""")
        assert not CheckErrorContent(__name__)

    def test14(self):
        self.Analyze("thisfile.h",
"""
class J {
protected :
    /** HELLO */
    A();
}
""")
        assert not CheckErrorContent(__name__)

    def test15(self):
        self.Analyze("thisfile.h",
"""
class J {
private :
    /** HELLO */
    A();
}
""")
        assert not CheckErrorContent(__name__)

    def test14(self):
        self.Analyze("thisfile.h",
"""
class J {
protected :
    A();
}
""")
        assert CheckErrorContent(__name__)

    def test15(self):
        self.Analyze("thisfile.h",
"""
class J {
private :
    A();
}
""")
        assert CheckErrorContent(__name__)
