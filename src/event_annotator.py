# dependency tree annotations are the worst right :/
# this file is meant to be command-line version of spaCy's prodigy.
# the end result is a combined intent + entity classifier that works well
# on zorb events.
# NOTE: make sure to run events through ner first, before normalising for intent
from __future__ import unicode_literals, print_function
from typing import Dict, List, Tuple, Literal
from zorb_types import DependencyTree, Label

import os
import json
import random
import requests
from pathlib import Path
import spacy
# from spacy.training import GoldParse
# from spacy.language import EntityRecognizer
from spacy import displacy
from spacy.util import minibatch, compounding
from spacy.training.example import Example


LABELS = ['PERSON', 'NORP', 'FAC', 'GPE', 'LOC', 'ORG', 'PRODUCT', 'WORK_OF_ART', 'LAW', 'LANGUAGE',
            'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', '-']

TRAIN_DATA: List[DependencyTree] = []


# to evolve into an intent classifier
class ZorbAnnotator:
    """Interactive interface for annotating zorb events. Updates and retrains per event."""

    def __init__(self):
        self._events: List[str] = []                              # might switch to stacks
        self._processed: List[str] = []                           # stores processed events
        self._nlp = None
        self._output_dir = 'data'
        self._model_dir = f'{self._output_dir}/model'
        self._load_data()                                         # load model, populate self._events (and self._processed)

    def annotate(self) -> None:
        """Interactively populate dependency heads and labels from user input."""
        index = 0
        while index <= len(self._events) - 1:
            try:
                event: str = self._events[index]
                tokenized_event: dict = self._tokeinize(event)    # returns dict of indexed tokens
                heads: List[int] = self._dep_heads(event, tokenized_event)
                deps: List[Label] = self._label(event, tokenized_event)
                # verified = self._visualize_dependencies((event, {'heads': heads, 'deps': deps }))
                # if verified:
                #     TRAIN_DATA.append((event, { 'heads': heads, 'deps': deps }))         # add to TRAIN_DATA
                # else:
                #     continue                                    # retry current event
                TRAIN_DATA.append((event, { 'heads': heads, 'deps': deps }))         # add to TRAIN_DATA
                self._processed.append(self._events.pop(self._events.index(event)))  # move event to processed list
                self._save_data()                                 # persist data, as of this iter
                self._train()                                     # train model with updated TRAIN_DATA
                index += 1                                        # process next event
            except AnnotationError:
                continue                                          # skip this event
            
    def _dep_heads(self, event: str, tokenized: dict) -> List[int]:
        """Interactively populate dependency heads."""
        print(tokenized)                                          # helps user map tokens
        print(event)
        print('>>>>>>DEPENDENCY HEADS<<<<<<')
        heads: list[int] = []
        index = 0
        while index <= len(tokenized) - 1:                        # while loop allows us to redo an iteration
            dep_head: str = input(f'{tokenized[index]} [{index}]: ')
            if dep_head == 'skip' or dep_head == 's':
                raise AnnotationError('Skipping this event...')
            if dep_head == '':                                    # token is independent
                dep_head = index
            try:
                heads.append(int(dep_head))
            except ValueError:                                    # user input non-numerical
                continue                                          # index not incremented; retry
            index += 1                                            # on to the next, if in range
        return heads
    
    def _label(self, event: str, tokenized: dict) -> List[Label]:
        """Interactively label tokens."""
        print('Supported labels:', LABELS)
        print(event)
        print('>>>>>>LABELS<<<<<<')
        deps = []
        index: int = 0
        while index <= len(tokenized) - 1:
            label: Label = input(f'{tokenized[index]} [-]: ')
            if label == '':
                label = '-'                                       # no-relation label
            if label.upper() not in LABELS:
                print(f'Unsupported label: {label}. Please try again.')
                continue                                          # index not incremented; try again
            deps.append(label.upper())
            index += 1
        return deps
    
    def _visualize_dependencies(self, dep_tree: DependencyTree) -> bool:
        """Visualise dependency tree."""
        text, annotations = dep_tree
        doc = self._nlp.make_doc(text)
        # example = Example.from_dict(doc, annotations)
        displacy.serve(doc, style='dep')
        
        result: Literal['y', 'n'] = input('Confirmed? [Y/n]: ')
        return True if result.lower() in ['', 'y'] else False

    # thank you spaCy devs
    def _train(self, n_iter: int=15):
        """Load the model, set up the pipeline and train the parser."""
        if 'parser' in self._nlp.pipe_names:
            self._nlp.remove_pipe('parser')
        parser = self._nlp.add_pipe('parser')

        for text, annotations in TRAIN_DATA:
            for dep in annotations.get('deps', []):
                parser.add_label(dep)

        pipe_exceptions = ['parser', 'trf_wordpiecer', 'trf_tok2vec']
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
                print('Losses', losses)

        self._test_model()                    # test updated model

    def _test_model(self):
        """Test current model."""
        test_event = self._processed[-1]      # ignore over-fitting for now, just confirm relationships
        docs = self._nlp.pipe([test_event])
        for doc in docs:
            print(doc.text)
            print(json.dumps(
                obj=[(token.text, token.dep_, token.head.text) for token in doc if token.dep_ != '-']))
            
    def _tokeinize(self, event: list) -> dict:
        """Return dict where values are tokens and keys are their indices."""
        tokenized_event = self._nlp(event)
        token_indices = [index for index in range(len(tokenized_event))]
        return { index: str(tokenized_event[index]) for index in token_indices }

    def _load_data(self):
        """Load model and data from previous session, if present."""
        # create required directories, if not exist
        Path(f'{self._output_dir}/model').mkdir(parents=True, exist_ok=True)

        if 'meta.json' in os.listdir(self._model_dir):
            self._nlp = spacy.load(self._model_dir)    # load existing model
        else:
            self._nlp = spacy.load('en_core_web_sm')  # start from pretrained

        data_files = os.listdir(self._output_dir)

        if 'zorb_training_data.json' in data_files:    # load existing training data
            with open(f'{self._output_dir}/zorb_training_data.json', 'r') as f:
                TRAIN_DATA = json.loads(f.read())['data']

        if 'unlabeled_events.json' in data_files:      # load previously fetched events, if present
            with open(f'{self._output_dir}/unlabeled_events.json', 'r') as f:
                self._events = json.loads(f.read())['events']

        if 'labeled_events.json' in data_files:        # load labeled events from prev session, if present
            with open(f'{self._output_dir}/labeled_events.json') as f:
                self._processed = json.loads(f.read())['events']

        if len(self._events) == 0:                     # no events found from previous session
            response = requests.get('http://localhost:8000/events')
            response.raise_for_status()
            response_data = response.json()
            events = [event['title'] for event in response_data['events']]
            with open(f'{self._output_dir}/unlabeled_events.json', 'w') as f:
                f.write(json.dumps({ 'events': events }))  # next initialisation will read from file
            self._events = events

    def _save_data(self):
        """Persist current training data, self._events, and self._processed."""
        self._nlp.to_disk(self._model_dir)           # save current model

        with open(f'{self._output_dir}/zorb_training_data.json', 'w') as f:          # save current TRAIN_DATA
            f.write(json.dumps({ 'data': TRAIN_DATA }))

        with open(f'{self._output_dir}/unlabeled_events.json', 'w') as f:            # save unprocessed events
            f.write(json.dumps({ 'events': self._events }))

        with open(f'{self._output_dir}/labeled_events.json', 'w') as f:
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

class AnnotationError(Exception):
    """Program or user  triggered error during event annotation."""
    pass

if __name__ == "__main__":
    annotator = ZorbAnnotator()
    annotator.annotate()
