# dependency tree annotations are the worst right :/
# this file is meant to be command-line version of spaCy's prodigy.
# the end result is a combined intent + entity classifier that works well
# on zorb's event stream events. shout out to the spaCy devs for the original template
# ps: make sure to run events through ner first, before normalising for intent
from __future__ import unicode_literals, print_function

import json
import random
import requests
import spacy
from spacy.training import GoldParse
from spacy.language import EntityRecognizer
from spacy.util import minibatch, compounding
from spacy.training.example import Example


TRAIN_DATA = []


class Annotator:
    """Handles event annotations for zorb nlu."""
    
    def __init__(self):
        self._events = self._fetch_events()
        self._processed = []    # stores processed events. todo: use stack
        self._nlp = spacy.blank('en')
        
    def annotate(self):
        """"Interactively populate dependency heads and labels from user input."""
        for event in self._events:
            mapped_event = self._map_event(event)
            print(mapped_event)
            
            heads = []
            print('>>>>>>HEADS<<<<<<')
            for token in mapped_event.values:
                user_input = input(f'{token}: ')
                # todo: support skipping current event
                head = int(user_input)
                heads.append(head)
                
            deps = []
            print('>>>>>>DEPS<<<<<<')
            for token in mapped_event.values:
                user_input = input(f'{token}: ')
                deps.append(user_input.upper())
            
            TRAIN_DATA.append((event, { 'heads': heads, 'deps': deps }))         # save new train data
            self._processed.append(self._events.pop(self._events.index(event)))  # remove processed event
            self._train()                                                        # train model with new train data           
                        
    def _train(self, n_iter=15):
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

        self._test_model()
        
    def _test_model(self):
        texts = self._processed
        docs = self._nlp.pipe(texts)
        for doc in docs:
            print(doc.text)
            print([(t.text, t.dep_, t.head.text) for t in doc if t.dep_ != "-"])
        
    def _map_event(self, event):
        """Map event tokens to token indices."""
        tokenized_event = self._nlp(event)
        token_indices = [index for index in range(tokenized_event)]
        return { index: str(tokenized_event[index]) for index in token_indices }
    
    def _fetch_events(self):
        response = requests.get('https://localhost:8000/events')
        response.raise_for_status()
        response_data = response.json()
        
        self._events = [event['title'] for event in response_data['events']]

    def _load_events(self, file):
        """load events from file."""
        with open(file, 'r') as f:
            return f.readlines()
            
    def _save_events(self, file):
        """"Typically saves events after processed events have been popped."""
        with open(file, 'w') as f:
            f.writelines(self._events)
            
    def _save_train_data(self, data, train_data_file):
        """Called after a new training instance is successfully added to TRAIN_DATA."""
        with open(train_data_file, 'w') as f:
            f.write(json.dumps({ 'data': TRAIN_DATA }))
            

class NERCustomiser:
    """Adds custom entities to spaCy's NER."""
    
    def __init__(self):
        self._nlp = spacy.load('en', entity=False, parser=False)
        self._doc_list = []
        self._gold_list = []
        self._custom_entities = []
        
    def add(self, event):
        doc = self._nlp(event)
        self._doc_list.append(doc)
        labels = []
        for token in doc:
            label = input(f'{token}: ')
            labels.append(u'%s' % label)
        
        self._gold_list.append(GoldParse(doc, labels))
        entity_types = [label for label in labels if label != u'O']
        [
            self._custom_entites.append(entity) for entity in entity_types
            if entity not in self._custom_entities
        ]
        
    def update(self):
        """Update spaCy entities with our custom entities."""
        ner = EntityRecognizer(self._nlp.vocab, entity_types=self._entity_types)
        ner.update(self._doc_list, self._gold_list)
        
    def test(self, events):
        results = []
        for event in events:
            doc = self._nlp(event)
            entities = [{
                'entity': entity.label_,
                'value': entity.text,
                'start': entity.start_char,
                'end': entity.end_char
            } for entity in doc.ents]
            results.append({ 'text': event, 'entities': entities })
        return results    
        

if __name__ == "__main__":
    annotator = Annotator()
    annotator.annotate()
