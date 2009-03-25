import sys


class Test:
    
    def test(self, param):
        
        self.test2()
        
    def test2(self):
        
        print sys._getframe(1).f_locals.get('param2')
        print "x"
        


t = Test()

t.test('hello')

