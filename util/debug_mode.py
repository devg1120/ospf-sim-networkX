


class Singleton(object):
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

class DebugMode(Singleton):
    def __init__(self):
        self._DEBUG_ = 0

    def make(self,flag_list):
        _debug_bit = 0b000000
        for flag in flag_list:
            tmp = 1<<(flag -1)
            _debug_bit = _debug_bit | tmp
        self._DEBUG_ = _debug_bit
        #print("_DEBUG_%s:" % bin(self._DEBUG_))
    
    def check(self,flag):
        #print("debug_mode_check:%s" % str(flag))
        cbit = 1<<(flag-1)
        #print(bin(self._DEBUG_))
        #print(bin(cbit))
        result = self._DEBUG_ & cbit 
        #print(result)
        if result > 0:
            return True
        else:
            return False
    


if __name__ == '__main__':

    _DEBUG_FLAG_LIST =[1,2,4]

    _DEBUG= DebugMode()
    _DEBUG.make(_DEBUG_FLAG_LIST)
    
    print(_DEBUG.check(1))
    print(_DEBUG.check(2))
    print(_DEBUG.check(3))
    print(_DEBUG.check(4))
    print(_DEBUG.check(5))

#    _DEBUG_FLAG_LIST =[1,2,4]
#    
#    _DEBUG_ = debug_mode_make(_DEBUG_FLAG_LIST)
#    print(bin(_DEBUG_))
#
#    print(debug_mode_check(1))
#    print(debug_mode_check(2))
#    print(debug_mode_check(3))
#    print(debug_mode_check(4))
#    print(debug_mode_check(5))
