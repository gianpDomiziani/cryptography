import hashlib
import secrets
import time



     
aU = int.from_bytes(b"it is the constant a", byteorder='little')
bU = int.from_bytes(b"it is the constant b", byteorder='big')


# sample DSA parameters for 1024-bit key from RFC 6979

pDSA = 0x86F5CA03DCFEB225063FF830A0C769B9DD9D6153AD91D7CE27F787C43278B447E6533B86B18BED6E8A48B784A14C252C5BE0DBF60B86D6385BD2F12FB763ED8873ABFD3F5BA2E0A8C0A59082EAC056935E529DAF7C610467899C77ADEDFC846C881870B7B19B2B58F9BE0521A17002E3BDD6B86685EE90B3D9A1B02B782B1779

qDSA = 0x996F967F6C8E388D9E28D01E205FBA957A5698B1

gDSA = 0x07B0F92546150B62514BB771E2A0C0CE387F03BDA6C56B505209FF25FD3C133D89BBCD97E904E09114D9A7DEFDEADFC9078EA544D2E401AEECC40BB9FBBF78FD87995A10A1C27CB7789B594BA7EFB5C4326A9FE59A070E136DB77175464ADCA417BE5DCE2F40D10A46A3A3943F26AB7FD9C0398FF8C76EE0A56826A8A88F1DBD


def schnorr_definition(p=pDSA, q=qDSA, g=gDSA):

    print('Schnorr Definition')
    x = secrets.randbelow(q-1)  # private key
    y = pow(g, x, p)  # public key
    print(f'Done: sk: {x}, pk: {y} ')
    return x, y

def schnorr_signature(x, p=pDSA, q=qDSA, g=gDSA, msg=b'Digital signature using the Schnorr scheme'):
    """Compute a Schnorr digital signature of a message using SHA-256 as hash function.
    x: private key
    y: public key
    """

    print('Schnorr signature')
    k = secrets.randbelow(q-1)
    nbytes = (p.bit_length() + 7) // 8
    I = pow(g, k, p)
    #m = int.from_bytes(msg, byteorder='big')
    I = I.to_bytes(nbytes, byteorder='big')
    m = I + msg
    #r = hashlib.sha256(m.to_bytes(nbytes, byteorder='big')).digest()
    h = get_x_bytes_of_hash(m, 32)
    h_ = int.from_bytes(h, byteorder='big')
    r = h_ % q
    s = (k - r*x) % q
    print(f'Done: r: {r}, s: {s}')
    return r, s

def schnorr_verification(y, r, s, msg=b'Digital signature using the Schnorr scheme'):

    print(f'Schnorr verification. Message: {msg}')
    nbytes = (pDSA.bit_length() + 7) // 8
    g_ = pow(gDSA, s, pDSA)
    y_ = pow(y, r, pDSA)
    I = (g_*y_) % pDSA
    I = I.to_bytes(nbytes, byteorder='big')
    #m = int.from_bytes(msg, byteorder='big')
    M = I + msg
    h = get_x_bytes_of_hash(message=M, x=32)
    r_ = int.from_bytes(h, byteorder='big')
    v = r_ % qDSA
    assert r == v
    print("Verification done: Digital Signature approved.")
    print(f'r: {r}, r_: {v}')
    print('Done!')






def egcd(a, b):
    """computes g, x, y such that g = GCD(a, b) and x*a + y*b = g"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, x, y = egcd(b % a, a)
        return (g, y - (b // a) * x, x)

def modinv(a, m):
    """computes a^(-1) mod m"""
    g, x, y = egcd(a % m, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def get_x_bytes_of_hash(message, x):

    return hashlib.sha256(message).digest()[:x]

def get_bytesArray_from_int(n_bits, x):

    n_byte = int(n_bits/8) + 1
    return x.to_bytes(n_byte, byteorder='big')



def check_collision(n, k):
    # n is the number of bit length of the input msg

    # counters
    C_1 = C_2 = {}
    uC_1 = uC_2 = {}

    m0 = None
    m1 = None

    # initial string
    x = secrets.randbits(n + 8)




    for z in range(k):
        C_1[z+1] = 0
        C_2[z+1] = 0
        uC_1[z+1] = 0
        uC_2[z+1] = 0

        x_0 = get_bytesArray_from_int(n, x)
        print(f'bytearray of x: {x_0} \n x len bit: {x.bit_length()}')

        # get 4 bytes of hash x_0 and x_1
        x_1 = get_x_bytes_of_hash(x_0, z+1)
        x_2 = get_x_bytes_of_hash(x_1, z+1)
        ux_1 = universal_hash(msg=x_0, digest_length=z+1)
        ux_2 = universal_hash(msg=ux_1, digest_length=z+1)

        # loop until our hashes are equal
        while x_1 != x_2:
            x_1 = get_x_bytes_of_hash(x_1, z+1)
            x_2 = get_x_bytes_of_hash(get_x_bytes_of_hash(x_2, z+1), z+1)
            C_1[z+1] += 1

        while ux_1 != ux_2:
            ux_1 = universal_hash(msg=ux_1, digest_length=z+1)
            ux_2 = universal_hash(msg=universal_hash(msg=ux_2, digest_length=z+1), digest_length=z+1)
            uC_1[z+1] += 1
        # Now H^i(x_0) == H^{2i}(x_0)
        print(f'H^i(x_0): {x_1}, H^(2i)(x_0) = {x_2}')
        print(f'found collision in {z+1} bytes string after: {C_1[z+1]} tries')
        print(f'UHash: found collision in {z + 1} bytes string after: {uC_1[z + 1]} tries')

        # Now H^i(x_0) == H^{2i}(x_0)
        x_1 = x_0
        ux_1 = x_0
        # Loop until they match again ...
        x_1 = get_x_bytes_of_hash(x_1, z+1)
        x_2 = get_x_bytes_of_hash(x_2, z+1)
        ux_1 = universal_hash(msg=ux_1, digest_length=z+1)
        ux_2 = universal_hash(msg=ux_2, digest_length=z+1)
        while x_1 != x_2:
            m0 = x_1
            x_1 = get_x_bytes_of_hash(x_1, z+1)
            x_2 = get_x_bytes_of_hash(x_2, z+1)
            C_2[z+1] += 1
        print(f'the first {z+1} bytes of the sha256 hash of {m0} are equal to {x_2}')


        while ux_1 != ux_2:
            ux_1 = universal_hash(msg=ux_1, digest_length=z+1)
            ux_2 = universal_hash(msg=ux_2, digest_length=z+1)
            uC_2[z+1] += 1

        print(f'found collision in {z + 1} bytes string after: {C_2[z + 1]} tries')
        print(f'UHash: found collision in {z + 1} bytes string after: {uC_2[z + 1]} tries')


        #x_2 = get_x_bytes_of_hash(x_1, z+1)
        #while x_1 != x_2:
        #    m1 = x_2
        #    x_2 = get_x_bytes_of_hash(x_2, z+1)
        #print(f'the first {z+1} bytes of the sha256 hash of {m1} are equal to {x_2}')
        #x_1 = get_x_bytes_of_hash(x_0, z+1)
        #x_2 = get_x_bytes_of_hash(x_1, z+1)

    print(f'm0: {m0}, m1: {m1}, C0: {C_1}, C1: {C_2}')

    return C_1, C_2, m0, m1, uC_1, uC_2


def universal_hash(a=aU, b=bU, q=qDSA, msg=b'SHA-256 is a cryptographic hash function', digest_length=2):


    m = int.from_bytes(msg, byteorder='big')

    h = (a*m + b) % q
    assert h.bit_length() <= q.bit_length()
    hash = h.to_bytes(int(q.bit_length()/8), byteorder='big')
    return hash[:digest_length]





    

def main():
    print('(p-1) mod q:', (pDSA - 1) % qDSA)
    print('g^q mod p:', pow(gDSA, qDSA, pDSA))
    
    message = b"SHA-256 is a cryptographic hash function"
    m = hashlib.sha256()
    m.update(message)
    hash = m.digest()

    m.update(b"Ciaone")
    hash_1 = m.digest()
    
    print(f'hash of {message} is {hash}, instead hash_2: {hash_1}')
    print('32 bit hash is:', hash[:4])
    print('64 bit hash is:', hash[:8])

    start = time.time()
    c0, c1, m0, m1, uC1, uC2 = check_collision(n=4*32, k=4)
    elapsed = time.time() - start
    print(f'c0= {c0}, c1= {c1}; elapsed time: {elapsed} \n uc1={uC1}, uc2={uC2}')
    return c0, c1, m0, m1, uC1, uC2
    
   
    

if __name__ == '__main__':
    uh = universal_hash()
    print(f'Universal hash digest: {uh}')
    #c0, c1, m0, m1, uC1, uC2 = main()
    x, y = schnorr_definition()
    r, s = schnorr_signature(x=x)
    schnorr_verification(y=y, r=r, s=s)

    yp = 42276637486569720268071647368550139276503521977640661888834825275517477780979914414339836061961635727800848465170706694019279805873893995587354694642526839889426158621140802827015533730771103146644607587713359225607432856473853326971226628964711099095487586928079612107255097386799478803704960241864601625828
    msg1 = b'first message'
    (r1, s1) = (299969984114895304388954029424480730263471439206, 192417049713099740312922361446986628497439105550)
    schnorr_verification(y=yp, r=r1, s=s1, msg=msg1)

    msg2 = b'second message'
    (r2, s2) = (719970963765961216949252326232207427282652913363, 107425968460827725118970802806887322358870342520)

    schnorr_verification(y=yp, r=r2, s=s2, msg=msg2)
