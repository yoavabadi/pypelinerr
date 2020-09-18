Pypelinerr
=========
[![python-versions](https://img.shields.io/badge/python-3.6-blue?logo=python)](https://img.shields.io/pypi/pyversions/pypelinerr)
[![pypi-badge](https://img.shields.io/pypi/v/pypelinerr.svg)](https://pypi.org/project/pypelinerr)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

[Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/) implementation for Python.

## Motivation
Handling events that trigger a sequence of commands or side-effects can be extremely elegant using the railway pattern.
This package can allow you to create a dedicated pipeline for each flow or event, that will preform the tasks in an ordered fashion. 

## Basic Usage

1. Create a class that inherit from `Pipeline`, with `phases` method:
```python
from pypelinerr import Pipeline


class SomeEventHandler(Pipeline):
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
2. in the pypeline manager, use `SomeEventHandler(options).run()`, where `options` are the input to the pipeline flow.

## Example
For example, if you create a pipeline that first connects to a database, then fetches the a document by an id, validates it, and finally send a post request of the entry's user_id, it can look like this:
```python
import requests
from pymongo import MongoClient

from pypelinerr import Pipeline


class RetrieveDataAndPost(Pipeline):
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


### Break operation
Calling the `break_operation(message?)` allows you to break from the pipeline's (event's handler) pipeline on an invalid result, without failing the whole pipeline.
An example for such a use-case is when checking in a DataBase if an entity not exists, and if so - not continuing the pipeline's flow.

In the bellow flow, we want to process a [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) event named `OrderCreated` of our online shop, 
where if the user details not present in our DB, we would not want to proceed, because only signed-up users can create an order:

```python
from pypelinerr import Pipeline


class OrderCreated(Pipeline):
    def phases(self):
        return [
            'validate_user_exists',
            'create_an_order',
            '...',
            '...'
        ]

    def validate_user_exists(self):
        user = db.user_collection.find_one({'id': self.options['user_id']})
        if not user:
            self.break_operation(message='user not in mongo collection')

    def create_an_order(self):
        ...

```


### Fail operation
By calling `fail_operation(message?)`, we can stop *and* fail the pipeline's operation.
This can be very useful in case of, for example, a momentarily network connection issue with another service or a remote DB,
when you will want to send the pipeline's operation result object to a failed-queue, for later processing of the event from the phase
it failed, and with the current options. 

We can also `raise` an Exception and it will count as a failed-operation, but in a case where we have a wrapper around the service call /
DB access which already catches the exception, this is very useful:

Other Module that handle mongo connection:
```python

from pymongo import MongoClient


class UserCollection:
    def init_connection(self):
        try:
            return MongoClient('<MongoDB_URL>').db.user_collection
        except Exception as e:
            return None
    ...
```

Our pypeline:
```python
from models.user import UserCollection
from pypelinerr import Pipeline


class OrderCreated(Pipeline):
    def phases(self):
        return [
            'validate_user_exists',
            'create_an_order',
            '...',
            '...'
        ]

    def validate_user_exists(self):
        user_collection =  UserCollection().init_connection()
        if not user_collection:
            self.fail_operation(message='mongo connection failure')

    def create_an_order(self):
        ...

```

### Schema
The Schema mechanism allows us to validate the messages (the event payload) been passed to the pipeline,
before the pipeline itself starts:
```python
schema = Schema({'user_id': int, 'logged_in': bool})
event_payload = {'user_id': 'not a number', 'logged_in': True}
OrderCreated(options=event_payload, schema=schema).run()
```
This run will result in a failure, with a fail message of:
```schema.SchemaUnexpectedTypeError: 'not a number' should be instance of 'int'```


### entry_phase
The entry phase allow us to use the pipeline from a specific phase, and skip it's previous phases.
The most common use-case for this is re-running the pipeline in a case of failure, or using only a small part of the
whole pipeline.
```python
event_payload = {'user_id': 123, 'logged_in': True}
OrderCreated(options=event_payload, entry_phase='create_an_order').run()
```
