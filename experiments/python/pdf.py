import io
import pymupdf

path = '/Users/ngrislain/Downloads/WINDERMERE_ELSA_AGENDA_GENERAL ASSEMBLY MEETING_FINAL.pdf'
input = io.BytesIO()
output = io.BytesIO()

with open(path, 'rb') as f:
    for b in f:
        input.write(b)

doc = pymupdf.Document(stream=input)

for page in doc:
    output.write(page.get_text(sort=True).encode('utf8'))

output.seek(0)
print(output.read().decode())