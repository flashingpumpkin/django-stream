# django-stream

[![Build Status](https://travis-ci.org/caffeinehit/django-stream.png?branch=master)](https://travis-ci.org/caffeinehit/django-stream)

django-stream provides activity streams for Django applications. 

It differs from 
[django-activity-stream](https://github.com/justquick/django-activity-stream) in that it does not use generic relations and does not provide a `Follow` object, but it can be used together with [django-follow](https://github.com/caffeinehit/django-follow). 

The motivation to not use generic relations is for simplicity reasons.


## Installation

```bash
pip install django-stream
```

## Configuration

* In your `settings.py` add stream types:

```python
INSTALLED_APPS += ('stream', )

STREAM_VERBS = (
	('default', 'Stream Item'),
    ('edit', 'Object edited'),
    ('created','Object created'),
    ('deleted','Object deleted'),
    ('followed', 'Object followed'))
``` 


* Register the models you want to be able to tag in your streams:

```python
from django.db import models
from stream import utils

class MyModel(models.Model):
field = models.CharField(max_length = 255)

utils.register_actor(MyModel)
utils.register_target(MyModel)
utils.register_action_object(MyModel)
```

## Testing

Run tox.

```bash
$ git clone https://github.com/caffeinehit/django-stream.git && cd django-stream && tox
[...]
```

## Example

The repository contains an example project and application making use
of `django-stream` in the `test/` folder. 


## API

### Manager

* `ActionManager.create(actor, verb, target=None, action_object=None, **kwargs)`:  
  Create a new action object

* `ActionManager.get_or_create(actor, verb, target=None, action_object=None, **kwargs)`:  
  Returns a tuple `(Action, bool)`

* `ActionManager.get_for_actor(actor)`:  
  Returns all the `Action` objects involving `actor`

* `ActionManager.get_for_actors(actors)`:  
  Similar to above, but acts on a list of actors

* `ActionManager.get_for_target(target)`:  
  Returns all the `Action` objects involving `target`

* `ActionManager.get_for_targets(targets)`:  
  Similar to above, but acts on a list of targets

* `ActionManager.get_for_action_object(obj)`:   
  Returns all the `Action` objects involving `obj`

* `ActionManager.get_for_action_objects(objects)`:  
  Similar to above, but acts on a list of action objects.

#### Hint

The generated fields on the `Action` model follow a simple pattern:

```python
"%(field_prefix)s_%(model_name)s"
```

Meaning, if you've registered the `User` model as actor target and as
action object, you could run custom queries like this:

```python
Action.objects.filter(actor_user = User.objects.filter(username__startswith = 'a'))
Action.objects.filter(target_user = User.objects.filter(username__startswith = 'b'))
Action.objects.filter(action_object_user = User.objects.filter(username__startswith = 'c'))
```


### Utils

* `stream.utils.register_actor(Model)`:  
  Make `Model` a possible actor

* `stream.utils.register_target(Model)`:  
  Make `Model` a possible target

* `stream.utils.register_acction_object(Model)`:  
  Make `Model` a possible action_object

* `stream.utils.action.send(actor, verb, target=None, action_object=None, description=None)`:  
  Create a new action object

### Template Tags

There is one template tag that attempts to render a given action:

```django
{% load stream_tags %}
{% render_action action %}
``` 

The template tag will try to find `stream/<action.verb>.html` and if it fails render the default template `stream/action.html`.

### Signals

There is one signal that is fired when new actions are created:

```python
stream.signals.action(instance)
```





