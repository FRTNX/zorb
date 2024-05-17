from typing import Dict, List, Tuple, Literal

DependencyTree = Tuple[str, dict]

Label = Literal['PERSON', 'NORP', 'FAC', 'GPE', 'LOC', 'ORG', 'PRODUCT', 'WORK_OF_ART', 'LAW', 'LANGUAGE',
            'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', '-']
