# dependency tree annotations are the worst right :/
# this file is meant to be command-line version of spaCy's prodigy.
# the end result is a combined intent + entity classifier that works well
# on zorb events.
# NOTE: make sure to run events through ner first, before normalising for intent
from __future__ import unicode_literals, print_function

import os
import json
import random
import requests
import spacy
# from spacy.training import GoldParse
# from spacy.language import EntityRecognizer
from spacy.util import minibatch, compounding
from spacy.training.example import Example


TRAIN_DATA = []


# to evolve into an intent classifier
class ZorbAnnotator:
    """Interactive interface for annotating zorb events. Updates and retrains per event."""
    
    def __init__(self):
        self._events = []                                        # might switch to stacks
        self._processed = []                                     # stores processed events
        self._nlp = spacy.blank('en')
        self._load_data()                                        # populate self._events (and self._processed)
        
    def annotate(self):
        """"Interactively populate dependency heads and labels from user input."""
        for event in self._events:
            tokenized_event = self._tokeinize(event)             # returns dict of indexed tokens
            print(tokenized_event)
            
            heads = []
            print(event)
            print('>>>>>>HEADS<<<<<<')
            for index in tokenized_event.keys():                 # keys indices, values tokens
                dep_head = input(f'{tokenized_event[index]} [{index}]: ')
                # todo: support skipping current event
                if dep_head == '':                               # token is independent
                    dep_head = index
                heads.append(int(dep_head))
                
            deps = []
            print(event)
            print('>>>>>>DEPS<<<<<<')
            for token in tokenized_event.values():
                label = input(f'{token} [-]: ')
                if label == '':
                    label = '-'                                   # no-relation label
                deps.append(label.upper())
            
            TRAIN_DATA.append((event, { 'heads': heads, 'deps': deps }))         # add to TRAIN_DATA
            self._processed.append(self._events.pop(self._events.index(event)))  # move event to processed list
            self._save_data()                                     # persist data, as of this iter
            self._train()                                         # train model with updated TRAIN_DATA           
         
    # thank you spaCy devs               
    def _train(self, n_iter: int=15):
        """Load the model, set up the pipeline and train the parser."""
        if "parser" in self._nlp.pipe_names:
            self._nlp.remove_pipe("parser")
        parser = self._nlp.add_pipe("parser")

        for text, annotations in TRAIN_DATA:
            for dep in annotations.get("deps", []):
                parser.add_label(dep)

        pipe_exceptions = ["parser", "trf_wordpiecer", "trf_tok2vec"]
        other_pipes = [pipe for pipe in self._nlp.pipe_names if pipe not in pipe_exceptions]
        with self._nlp.disable_pipes(*other_pipes):
            optimizer = self._nlp.begin_training()
            for itn in range(n_iter):
                random.shuffle(TRAIN_DATA)
                losses = {}
                batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    for text, annotations in batch:
                        doc = self._nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        self._nlp.update([example], sgd=optimizer, losses=losses)
                print("Losses", losses)

        self._test_model()                                                     # test updated model
        
    def _test_model(self):
        """Test current model."""
        test_events = self._processed     # ignore over-fitting for now, just confirm relationships
        docs = self._nlp.pipe(test_events)
        for doc in docs:
            print(doc.text)
            print([(t.text, t.dep_, t.head.text) for t in doc if t.dep_ != "-"])
        
    def _tokeinize(self, event: list) -> dict:
        """Return indexed event tokens."""
        tokenized_event = self._nlp(event)
        token_indices = [index for index in range(len(tokenized_event))]
        return { index: str(tokenized_event[index]) for index in token_indices }
    
    def _load_data(self):
        """Load data from previous session, if present."""
        if 'unlabeled_events.json' in os.listdir():  # load previously fetched events, if present
            with open('unlabeled_events.json', 'r') as f:
                self._events = json.loads(f.read())['events']
            
        if 'labeled_events.json' in os.listdir():    # load labeled events from prev session, if present
            with open('labeled_events.json') as f:
                self._processed = json.loads(f.read())['events']
            
        if len(self._events) == 0:                   # above statements did not run
            response = requests.get('http://localhost:8000/events')
            response.raise_for_status()
            response_data = response.json()
            
            with open('unlabeled_events.json', 'w') as f:
                f.write(json.dumps(response_data))
            self._events =[event['title'] for event in response_data['events']]
            
    def _save_data(self):
        """Persist current training data, self._events, and self._processed."""
        with open('zorb_training_data.json', 'w') as f:          # save current TRAIN_DATA
            f.write(json.dumps({ 'data': TRAIN_DATA }))
            
        with open('unlabeled_events.json', 'w') as f:            # save unprocessed events
            f.write(json.dumps({ 'events': self._events }))
            
        with open('labeled_events.json', 'w') as f:
            f.write(json.dumps({ 'events': self._processed }))   # save processed events
            

# to evolve into fully customised NER classifier
# class ZorbNer:
#     """Adds custom entities to spaCy's NER."""
    
#     def __init__(self):
#         self._nlp = spacy.load('en', entity=False, parser=False)
#         self._doc_list = []
#         self._gold_list = []
#         self._custom_entities = []
        
#     def add(self, event):
#         doc = self._nlp(event)
#         self._doc_list.append(doc)
#         labels = []
#         for token in doc:
#             label = input(f'{token}: ')
#             labels.append(u'%s' % label)
        
#         self._gold_list.append(GoldParse(doc, labels))
#         entity_types = [label for label in labels if label != u'O']
#         [
#             self._custom_entites.append(entity) for entity in entity_types
#             if entity not in self._custom_entities
#         ]
        
#     def update(self):
#         """Update spaCy entities with our custom entities."""
#         ner = EntityRecognizer(self._nlp.vocab, entity_types=self._entity_types)
#         ner.update(self._doc_list, self._gold_list)
        
#     def test(self, test_events):
#         test_results = []
#         for event in test_events:
#             doc = self._nlp(event)
#             entities = [{
#                 'entity': entity.label_,
#                 'value': entity.text,
#                 'start': entity.start_char,
#                 'end': entity.end_char
#             } for entity in doc.ents]
#             test_results.append({ 'text': event, 'entities': entities })
#         return test_results    
        

if __name__ == "__main__":
    annotator = ZorbAnnotator()
    annotator.annotate()
