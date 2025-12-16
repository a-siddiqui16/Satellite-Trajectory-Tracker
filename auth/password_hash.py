# import bcrypt

# #Function to hash password
# def hash_password(password):

#     password_bytes = password.encode('utf-8')
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(password_bytes, salt)
#     return hashed.decode('utf-8')

# #Verify a password against a hash
# def verify_password(password, hashed_password):

#     password_bytes = password.encode('utf-8')
#     hashed_bytes = hashed_password.encode('utf-8')
#     return bcrypt.checkpw(password_bytes, hashed_bytes)

#Reference: https://github.com/keanemind/python-sha-256/blob/master/sha256.py


#Constants

K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]

def sha256(message):

    if isinstance(message, str):
        message = bytearray(message, "utf-8")
    elif isinstance(message, bytes):
        message = bytearray(message)
    elif not isinstance(message, bytearray):
        print("Invalid message type")

    #Padding

    original_length = len(message) * 8

    message.append(0x80)

    while (len(message) * 8 + 64) % 512 != 0:
        message.append(0x00)

    message += original_length.to_bytes(8, "big")

    #Hash values (sqaure roots of first 8 primes)
    
    h0 = 0x6a09e667
    h1 = 0xbb67ae85
    h2 = 0x3c6ef372
    h3 = 0xa54ff53a
    h4 = 0x510e527f
    h5 = 0x9b05688c
    h6 = 0x1f83d9ab
    h7 = 0x5be0cd19

    for i in range(0, len(message), 64):
        block = message[i:i + 64]

        schedule_array = []

        #First 16 words

        for t in range(16):
            schedule_array.append(int.from_bytes(block[t * 4:(t+1) * 4], "big"))

        for t in range(16, 64):
            s0 = _sigma0(schedule_array[t-15])
            s1 = _sigma1(schedule_array[t-2])
            schedule_array.append((schedule_array[t-16] + s0 + schedule_array[t-7] + s1) & 0xFFFFFFFF)

        #Variables

        a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7

        #Compression loop

        for t in range(64):
            T1 = (h + _capsigma1(e) + _ch(e, f, g) + K[t] + schedule_array[t]) & 0xFFFFFFFF
            T2 = (_capsigma0(a) + _maj(a, b, c)) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + T1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (T1 + T2) & 0xFFFFFFFF


        #Add the compressed part to the hash value

        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF
        h4 = (h4 + e) & 0xFFFFFFFF
        h5 = (h5 + f) & 0xFFFFFFFF
        h6 = (h6 + g) & 0xFFFFFFFF
        h7 = (h7 + h) & 0xFFFFFFFF

        #Combine final hash values into a 256-bit result

    return (
        h0.to_bytes(4, "big") +
        h1.to_bytes(4, "big") +
        h2.to_bytes(4, "big") +
        h3.to_bytes(4, "big") +
        h4.to_bytes(4, "big") +
        h5.to_bytes(4, "big") +
        h6.to_bytes(4, "big") +
        h7.to_bytes(4, "big")
    )

#Helpers

#Rotates a 32-bit ine
def _rotate_right(value, shift, size=32):
    return ((value >> shift) | (value << (size - shift))) & 0xFFFFFFFF


def _sigma0(x):
    return _rotate_right(x, 7) ^ _rotate_right(x, 18) ^ (x >> 3)


def _sigma1(x):
    return _rotate_right(x, 17) ^ _rotate_right(x, 19) ^ (x >> 10)


def _capsigma0(x):
    return _rotate_right(x, 2) ^ _rotate_right(x, 13) ^ _rotate_right(x, 22)


def _capsigma1(x):
    return _rotate_right(x, 6) ^ _rotate_right(x, 11) ^ _rotate_right(x, 25)


def _ch(x, y, z):
    return (x & y) ^ (~x & z)


def _maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)



#Checks if the users input measures the hash

def verify_password(password, stored_hash):
    password_hash = sha256(password)

    if isinstance(stored_hash, str):
        stored_hash_bytes = bytes.fromhex(stored_hash)
    else:
        stored_hash_bytes = stored_hash

    return password_hash == stored_hash_bytes
