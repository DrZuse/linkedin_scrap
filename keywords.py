import sqlite3
import spacy
from collections import Counter
from string import punctuation


import spacy
from spacy.matcher import PhraseMatcher

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Define the skill labels
skills_list = ["Python", "JavaScript", "React",  "Git"]

# Create a PhraseMatcher and add the skills to it
skill_patterns = list(nlp.pipe(skills_list))
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("SKILL", skill_patterns)

# Define the custom component for skill extraction
@spacy.Language.component("skill_component")
def skill_component(doc):
    matches = matcher(doc)
    spans = [spacy.tokens.Span(doc, start, end, label="SKILL") for match_id, start, end in matches]
    doc.ents = spans
    return doc

# Add the custom component to the pipeline
nlp.add_pipe("skill_component", after="ner")

# Process the job description and extract skills
job_description = """
We are looking for a Python developer with experience in web development.
The candidate should have strong skills in JavaScript and React.
Knowledge of SQL and Git is a plus.
"""



# DB
db_name = 'jobs.db'
db = sqlite3.connect(db_name)

def job_ids(req='jobID'):
    info = db.execute(f"SELECT {req},jobID FROM jobs WHERE language='en'").fetchall()
    print(info[0][1])
    result = [i[0] for i in info]
    return result


descriptions = job_ids('description')

#print(descriptions[0])

for job_description in descriptions:
    print(job_description)
    #text = "Natural language processing (NLP) is a subfield of artificial intelligence (AI)."
    #print(extract_keywords(r))
    doc = nlp(job_description)

    print("Skills required for the job:")
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            print(ent.text)
    break

db.close()