import os
from random import randint, sample, choice
from pydantic import BaseModel
import pymupdf
from faker import Faker

fake = Faker()

class Person(BaseModel):
    name: str
    age: int
    interests: list[str]

def random_person() -> Person:
    interest_items = ['sport', 'science', 'litterature', 'travel', 'music', 'cooking', 'cinema', 'history']
    return Person(
        name=fake.first_name(),
        age=randint(0, 80),
        interests=[interest for interest in sample(interest_items, randint(0, len(interest_items)))],
    )

def random_description(person: Person) -> str:
    interests = ', '.join(person.interests[:-1]) + ' and ' + person.interests[-1] if len(person.interests)>1 else person.interests[0] if len(person.interests)>0 else 'nothing'
    interests_list = '['+', '.join(person.interests) + ']'
    return choice([
        f"Hi I'm {person.name}, I'm {person.age} years old and I like {interests}.",
        f"Let me introduce myself: {person.name}.\nI'm {person.age} and I ame passionate about {interests}.",
        f"Name: {person.name}\nAge: {person.age}\nInterests: {interests_list}.",
    ])

def random_pdf_json(name: str):
    person = random_person()
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), random_description(person))
    os.makedirs('generated/random_pdf_json', exist_ok=True)
    doc.save(f'generated/random_pdf_json/{name}.pdf')
    doc.close()
    with open(f'generated/random_pdf_json/{name}.json', 'w') as f:
        f.write(person.model_dump_json())


if __name__ == "__main__":
    for i in range(10):
        random_pdf_json(f"person_{i}")
