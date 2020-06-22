from cryptography.fernet import Fernet

KEY = b'm55kgxcbhzRN8IXdec9lLE9_qd2bEVzCIwAmbCBRBvY='

def encrypt(data):
    f = Fernet(KEY)
    encoded = data.encode()
    encrypted = f.encrypt(encoded)
    return encrypted

def decrypt(encryptedData):
    f = Fernet(KEY)
    decrypted = f.decrypt(encryptedData)
    decoded = decrypted.decode()
    return decoded