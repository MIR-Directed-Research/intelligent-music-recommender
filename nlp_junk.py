import spacy
#
#
# # Load the spacy model: nlp
# nlp = spacy.load('en')
#
# # Calculate the length of sentences
# n_sentences = len(sentences)
#
# # Calculate the dimensionality of nlp
# embedding_dim = nlp.vocab.vectors_length
#
# # Initialize the array with zeros: X
# X = np.zeros((n_sentences, embedding_dim))
#
# # Iterate over the sentences
# for idx, sentence in enumerate(sentences):
#     # Pass each each sentence to the nlp object to create a document
#     doc = nlp(sentence)
#     # Save the document's .vector attribute to the corresponding row in X
#     X[idx, :] = doc.vector
#
# ###
# # Import SVC
# from sklearn.svm import SVC
#
# # Create a support vector classifier
# clf = SVC(C=1)
#
# # Fit the classifier using the training data
# clf.fit(X_train, y_train)
#
# # Predict the labels of the test set
# y_pred = clf.predict(X_test)
#
# # Count the number of correct predictions
# n_correct = 0
# for i in range(len(y_test)):
#     if y_pred[i] == y_test[i]:
#         n_correct += 1

# print("Predicted {0} correctly out of {1} test examples".format(n_correct, len(y_test)))

###
"""
Parsing entities
https://campus.datacamp.com/courses/building-chatbots-in-python/understanding-natural-language?ex=10

Using spaCy's entity recogniser

In this exercise you'll use spaCy's built-in entity recognizer to extract 
names, dates, and organizations from search queries. The spaCy library has 
been imported for you, and it's English model has been loaded as nlp.

Your job is to define a function called extract_entities() which takes in a 
single argument message and returns a dictionary with the included entity types 
as keys, and the extracted entities as values. The included entity types are 
contained in a list called include_entities.


    Create a dictionary called ents to hold the entities by calling dict.fromkeys() with include_entities as the sole argument.
    Create a spacy document called doc by passing the message to the nlp object.
    Iterate over the entities in the document (doc.ents).
    Check whether the entity's .label_ is one we are interested in. If so, assign the entity's .text attribute to the corresponding key in the ents dictionary.

"""

# Load the spacy model: nlp
nlp = spacy.load('en')

# Define included entities
include_entities = ['DATE', 'ORG', 'PERSON']

# Define extract_entities()
def extract_entities(message):
    # Create a dict to hold the entities
    ents = dict.fromkeys(include_entities)
    # Create a spacy document
    doc = nlp(message)
    for ent in doc.ents:
        if ent.label_ in include_entities:
            # Save interesting entities
            ents[ent.label_] = ent.text
    return ents

print(extract_entities('friends called Mary who have worked at Google since 2010'))
print(extract_entities('people who graduated from MIT in 1999'))


"""
n this exercise you'll use Rasa NLU to create an interpreter, which parses incoming user messages and returns a set of entities. Your job is to train an interpreter using the MITIE entity recognition model in rasa NLU.
Instructions
0 XP
Instructions
0 XP

    Create a dictionary called args with a single key "pipeline" with value "spacy_sklearn".
    Create a config by calling RasaNLUConfig() with the single argument cmdline_args with value args.
    Create a trainer by calling Trainer() using the configuration as the argument.
    Create a interpreter by calling trainer.train() with the training_data.

"""
# Import necessary modules
from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer

# Create args dictionary
args = {"pipeline": "spacy_sklearn"}

# Create a configuration and trainer
config = RasaNLUConfig(cmdline_args=args)
trainer = Trainer(config)

# Load the training data
training_data = load_data("./training_data.json")

# Create an interpreter by training the model
interpreter = trainer.train(training_data)

# Try it out
print(interpreter.parse("I'm looking for a Mexican restaurant in the North of town"))

"""
Data-efficient entity recognition

Most systems for extracting entities from text are built to extract 'Universal' things like names, dates, and places. But you probably don't have enough training data for your bot to make these systems perform well!

In this exercise, you'll activate the MITIE entity recogniser inside rasa to extract restaurants-related entities using a very small amount of training data. A dictionary args has already been defined for you, along with a training_data object.
"""
from rasa_nlu.model import Trainer

pipeline = [
    "nlp_spacy",
    "tokenizer_spacy",
    "ner_crf"
]

# Create a config that uses this pipeline
config = RasaNLUConfig(cmdline_args={"pipeline": pipeline})

# Create a trainer that uses this config
trainer = Trainer(config)

# Create an interpreter by training the model
interpreter = trainer.train(training_data)

# Parse some messages
print(interpreter.parse("show me Chinese food in the centre of town"))
print(interpreter.parse("I want an Indian restaurant in the west"))
print(interpreter.parse("are there any good pizza places in the center?"))


