Operation
=========
|python-versions| |pypi-badge|

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/operation
   :target: https://img.shields.io/pypi/pyversions/operation
   :alt: Supported Python Versions
.. |pypi-badge| image:: https://img.shields.io/pypi/v/operation.svg
   :target: https://pypi.org/project/operation
   :alt: PYPI Version

[Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/) implementation for Python.

## Motivation
Handling events that trigger a sequence of operations and side-effects can be extremely elegant using the railway pattern.
This package can allow you to create a dedicated pipeline for each event, that will preform the tasks in an ordered fashion. 

## Basic Usage

1. Create a class that inherit from `Operation`, with `phases` method:
```python
from operation import Operation


class SomeOperation(Operation):
    def phases(self):
        return [
            'phase_one',
            'phase_two',
            'phase_three'
        ]

    def phase_one(self):
        self.options['option_for_second_phase'] = True

    def phase_two(self):
        if 'option_for_second_phase' in self.options:
            return 'an option got passed from first phase, cool!'

    def phase_three(self):
        self.options['reached_third_phase'] = True
```
2. in the operation manager, use `SomeOperation(options).run()`, where `options` are the input to the operation flow.

### Example
For example, if you create an operation that first connects to a database, then fetches the a document by an id, validates it, and finally send a post request of the entry's user_id, it can look like this:
```python
import requests
from pymongo import MongoClient

from operation import Operation


class RetrieveDataAndPost(Operation):
    def phases(self):
        return [
            'connect_to_mongo',
            'fetch_document',
            'validate_document',
            'post_results'
        ]

    def connect_to_mongo(self):
        self.options['albums_collection'] = MongoClient('<MongoDB_URL>').albums

    def fetch_document(self):
        album_id = self.options.get('album_id')
        self.options['album'] = self.options['albums_collection'].find_one({ 'id': album_id })

    def validate_document(self):
        if 'artist_name' not in self.options['album']:
            self.fail_operation()

    def post_results(self):
        selected_artist =  self.options.get('album').get('artist_name')
        requests.post('<Artists_Service_URL>', data={'selected_artist': selected_artist})
```

## Features
- `schema` - 
- `break_operation(message?)` - 
- `fail_operation(message?)` - 
