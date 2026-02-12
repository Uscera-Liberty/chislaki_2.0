def gcd(a,b):
    while b !=0:
        a,b = b,a%b
    return a

def sum_digits(n):
    s = 0
    n = abs(n)
    while n > 0:
        s += n%10
        n //= 10
    return s

def product_digits(n):
    n = abs(n)
    if n==0: return 0
    p = 1
    while n > 0:
        p *= (n % 10)
        n //= 10
    return p

def divisors(n):
    div = []
    for i in range(1, abs(n) + 1):
        if n%i == 0:
            d.append(i)
    return d

def count_words(s):
    if s.strip() == "":
        return 0
    return len(s.split())

def zadacha1(n):
    c = 0
    for d in divisors(n):
        if d%3 != 0: c+=1
    return c

def zadacha2(n):
    n = abs(n)
    min_digit = 10
    while n > 0:
        d = n % 10
        if d % 2 == 1 and d < min_digit:
            min_digit = d
        n //= 10
    if min_digit == 10:
        return -1
    return min_digit

def zadacha3(n):
    s = sum_digits(n)
    p = product_digits(n)
    total = 0

    for d in divisors(n):
        if gcd(d,s) == 1 and gcd(d, p) != 1:
            total += d
    return total
#=====задание 2-4
def zadacha5_2(s):
    l = list(s)
    for i in range(len(l)):
        j = (i*11 + 7)%len(l)
        l[i], l[j] = l[j], l[i]
    return "".join(l)

def zadacha7(s):
    s1 = ""
    for ch in s:
        if  'A' <= ch <= 'Z':
            s1 += ch
    return s1 == s1[::-1]

def zadacha14(s):
    words = s.split()
    words.sort(key=len)
    return words
#========задание 5
def zadacha5(s):
    months = ["января","февраля","марта","апреля","мая","июня",
              "июля","августа","сентября","октября","ноября","декабря"]
    parts = s.split()
    res = []
    for i in range(len(parts) - 2):
        if parts[i].isdigit() and parts[i+2].isdigit():
            if parts[i+1] in months:
                res.append(parts[i] + " " + parts[i+1] + " " +parts[i+2])
    return res

#======задание 6-8

def zadacha5_6(s):
    mx = 0
    cur = 0
    for ch in s:
        if ('а' <= ch <= 'я') or ('А' <= ch <= 'Я') or ch == "ё" or ch == "Ё":
            cur += 1
            mx = max(cur, mx)
        else:
            cur = 0
    return mx

def zadacha7_7(s):
    return min(filter(lambda p: p.isdigit(), list(s)))
'''
def zadacha7_8(s):
    nums = []
    cur = ""
    for ch in s:
        if ch.isdigit():
            cur += ch
        else:
            if cur != "":
                nums.append(int(cur))
                cur = ""
    if cur != "":
        nums.append(int(cur))

    if not nums:
        return -1

    mn = nums[0]
    for x in nums:
        if x < mn:
            mn = x
    return mn
'''
def zadacha14_8(s):
    mx = 0
    cur = 0
    for ch in s:
        if ch.isdigit():
            cur += 1
            mx = max(cur, mx)
        else:
            cur = 0
    return mx

def zadacha9(l):
    return l.sort(key=len)
def zadacha10(l):
    l.sort(key=lambda x: len(x.split()))
    return l

'''
def zadacha10(l):
    for i in range(len(l)):
        for j in range(len(l)-1):
            if count_words(l[j]) > count_words(l[j+1]):
                l[j], l[j+1] = l[j+1], l[j]
    return l
'''

#==== задание 11-14
def average_ascii(s):
    if len(s) == 0: return 0
    total = 0
    for ch in s:
        total += ord(ch)
    return total/len(s)

def zadacha2_11(l):
    return l.sort(key=average_ascii)

def mediana_str(s):
    a = [ord(c) for c in s]
    a.sort()
    if len(a) == 0: return 0
    elif len(a)%2 == 1: return a[len(a)//2]

    return (a[len(a)//2 - 1] + a[len(a)//2 + 1])/2

def zadacha6_12(l):
    return l.sort(key=mediana_str)

#???
def metric_ascii9(s):
    if len(s) == 0:return 0
    max_ascii = ord(s[0])
    for ch in s:
        if ord(ch) > max_ascii: max_ascii = ord(ch)
    diff_sum = 0
    n = len(s)
    for i in range(n//2):
        diff_sum += abs(ord(s[i]) - ord(s[n - 1 -i]))
    d = max_ascii - diff_sum
    return pow(d, 2)

def zadacha9_13(l):
    return l.sort(key=metric_ascii)

def most_common_freq(s):
    if len(s) == 0:
        return 0
    mx = 0
    for ch in s:
        c = 0
        for x in s:
            if x == ch:
                c += 1
        if c > mx:
            mx = c
    return mx

def zadacha12_14(l):
    total_freq = 0
    for s in l:
        total_freq += most_common_freq(s)
    if len(l) == 0:
        avg = 0
    else:
        avg = total_freq / len(l)

    def dev(s):
        return (most_common_freq(s) - avg) ** 2

    return l.sort(key=dev)

#==== задания 15-19
def zadacha11_15(l):
    l.sort()
    if (l[0] != l[1]): return l[0]
    elif (l[-1] != l[-2]): return l[-1]

def zadacha23(l):
    return sorted(l)[0], sorted(l)[1]
def zadacha35(l, n):
    return sorted(l, lambda x: abs(x - n))[0] + n
'''
def closest_to_r(arr, R):
    if len(arr) == 0:
        return None
    best = arr[0]
    for x in arr:
        if abs(x - R) < abs(best - R):
            best = x
    return best
'''
def zadacha47(l):
    res = []
    for x in l:
        for d in range(1, x+1):
            if x%d == 0:
                if d not in res:
                    res.append(d)
    return res

def zadacha59(l):
    return [x**2 for x in l if x >= 0 and x < 100 and l.count(x) > 2]
    
def main():
    print(zadacha10(["mk fjkdf dfhdsf", "fdjkf" ,"jdfk df"]))
if __name__ == "__main__":
    main()