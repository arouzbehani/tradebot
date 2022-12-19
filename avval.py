

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True



 
# Driver function
sum=0 
for n in range(3, 1000):
    x = is_prime(n)
    if(x):
        sum+=n
    
print(sum)