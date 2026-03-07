import bcrypt

# Gera e imprime a hash para a senha '123'
hash = bcrypt.hashpw(b'123', bcrypt.gensalt())
print(hash.decode())
