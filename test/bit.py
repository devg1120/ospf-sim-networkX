

#_DEBUG_FLAG_LIST =[1,2,3,4]
_DEBUG_FLAG_LIST =[1,2,4]

def debug_mode_make(flag_list):
    _debug_bit = 0b000000
    for flag in flag_list:
        tmp = 1<<(flag -1)
        _debug_bit = _debug_bit | tmp
    return _debug_bit

def debug_mode_check(flag):
    cbit = 1<<(flag-1)
    result = _DEBUG_ & cbit 
    if result > 0:
        return True
    else:
        return False

_DEBUG_ = debug_mode_make(_DEBUG_FLAG_LIST)

#print(bin(_DEBUG_))

print(debug_mode_check(1))
print(debug_mode_check(2))
print(debug_mode_check(3))
print(debug_mode_check(4))
print(debug_mode_check(5))
