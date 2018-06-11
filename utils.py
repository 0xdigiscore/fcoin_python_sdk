def trunc(f, n):
    if not str(f):
        return '0'   
    sarr = str(f).split('.')    
    if len(sarr) == 2:
        s1, s2 = str(f).split('.')
    else:
        s1 = str(f)
        s2 = '0'    
    if n == 0:
        return s1
    if n <= len(s2):
        return s1 + '.' + s2[:n]
    return s1 + '.' + s2 + '0' * (n - len(s2))