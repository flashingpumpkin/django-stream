from django import template
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from stream.registry import actor_map, target_map, action_object_map



DEFAULT_STREAM_VERBS = (
    ('default', _('Stream Item')),
)

STREAM_VERBS = getattr(settings, 'STREAM_VERBS', DEFAULT_STREAM_VERBS)

class ActionManager(models.Manager):
    def create(self, actor, verb, target=None, action_object=None, **kwargs):
        """ Create a new action object """
        action = Action(actor=actor, verb=verb, target=target,
            action_object=action_object, **kwargs)
        action.save()
        return action
    
    def get_or_create(self, actor, verb, target=None, action_object=None, **kwargs):
        result = self.filter(verb=verb) | self.get_for_actor(actor)
        if target:
            result = result | self.get_for_target(target)
        if action_object:
            result = result | self.get_for_action_object(action_object)
        
        result = result.filter(**kwargs)
        
        if result.count() == 0:
            return self.create(actor, verb, target, action_object, **kwargs), True
        if result.count() == 1:
            return result[0], False
        raise Action.MultipleObjectsReturned
    
    def get_for_actor(self, actor):
        """ Returns all objects involving `actor` """
        _, f_name = actor_map[actor.__class__]
        return self.filter(**{f_name:actor})
    
    def get_for_target(self, target):
        """ Returns all objects involving `target` """
        _, f_name = target_map[target.__class__]
        return self.filter(**{f_name: target})
    
    def get_for_action_object(self, obj):
        """ Returns all objects involving `obj` """
        _, f_name = action_object_map[obj.__class__]
        return self.filter(**{f_name: obj})

class Action(models.Model):
    """
    Base class for all actions. This model is dynamically extended through the
    register function in `stream.util` 
    
    All the actor, target and action object fields are implemented as indexed
    foreign keys to avoid having generic relations. They're really uncool.
     
    """
    datetime = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    verb = models.CharField(choices=STREAM_VERBS, max_length=255, db_index=True)

    objects = ActionManager()

    def __unicode__(self):
        return u'%s: %s - %s' % (self.verb, self.actor(), self.target())

    def _get(self, map):
        for _, fname in map.values():
            if getattr(self, fname): 
                return getattr(self, fname)
        return None
    
    def _set(self, obj, map):
        if obj is None:
            for _, fname in map.values():
                setattr(self, fname, None)
        else:
            _, fname = map[obj.__class__]
            setattr(self, fname, obj)

    def _get_actor(self):
        return self._get(actor_map)
    def _set_actor(self, obj):
        self._set(obj, actor_map)
    def _get_target(self):
        return self._get(target_map)
    def _set_target(self, obj):
        self._set(obj, target_map)    
    def _get_action_object(self):
        return self._get(action_object_map)
    def _set_action_object(self, obj):
        return self._set(obj, action_object_map)
    
    actor = property(fget=_get_actor, fset=_set_actor)
    target = property(fget=_get_target, fset=_set_target)
    action_object = property(fget=_get_action_object, fset=_set_action_object)
    
   
