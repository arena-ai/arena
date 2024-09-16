import io

buff = io.BytesIO()

buff.write('A simple test string 🐭'.encode())
buff.seek(0)
print(buff.read())
buff.seek(0)
print(buff.read().decode())