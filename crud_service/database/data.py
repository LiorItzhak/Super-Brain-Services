from mongoengine import *
from datetime import datetime


class Person(Document):
    creation_timestamp = DateTimeField(default=datetime.now)
    modified_timestamp = DateTimeField(default=datetime.now)
    first_name = StringField(required=True, unique=False)
    user_id = StringField(required=True)
    last_name = StringField(required=True, unique=False)
    image_features = ListField(ListField(FloatField()), required=False)
    description = StringField(required=False, max_length=100)

    def save(self, *args, **kwargs):
        if self.id:
            self.creation_timestamp = Event.objects.get(id=self.id).creation_timestamp
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now()
        self.modified_timestamp = datetime.now()
        return super(Person, self).save(*args, **kwargs)

    def update(self, entity):
        entity.creation_timestamp = self.creation_timestamp
        entity.modified_timestamp = datetime.now()
        p_dict = dict(entity.to_mongo())
        del p_dict['_id']
        return super(Person, self).update(**p_dict)


class Event(Document):
    timestamp = DateTimeField()
    creation_timestamp = DateTimeField()
    modified_timestamp = DateTimeField(default=datetime.now)
    user_id = StringField(required=True)
    type = StringField()
    data = DictField(required=False)

    def save(self, *args, **kwargs):
        if self.id:
            self.creation_timestamp = Event.objects.get(id=self.id).creation_timestamp
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now()
        self.modified_timestamp = datetime.now()
        return super(Event, self).save(*args, **kwargs)


class User(Document):
    creation_timestamp = DateTimeField(default=datetime.now)
    modified_timestamp = DateTimeField(default=datetime.now)
    first_name = StringField(required=True, unique=False)
    last_name = StringField(required=True, unique=False)

    def save(self, *args, **kwargs):
        if self.id:
            self.creation_timestamp = Event.objects.get(id=self.id).creation_timestamp
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now()
        self.modified_timestamp = datetime.now()
        return super(User, self).save(*args, **kwargs)

    def update(self, entity):
        entity.creation_timestamp = self.creation_timestamp
        entity.modified_timestamp = datetime.now()
        p_dict = dict(entity.to_mongo())
        del p_dict['_id']
        return super(User, self).update(**p_dict)


class Notification(Document):
    timestamp = DateTimeField(default=None)
    creation_timestamp = DateTimeField()
    modified_timestamp = DateTimeField(default=datetime.now)
    user_id = StringField(required=True)
    type = StringField()
    data = DictField(required=False)
    is_active = BooleanField(default=True),
    notes = StringField(required=False)

    def save(self, *args, **kwargs):
        if self.id:
            self.creation_timestamp = Event.objects.get(id=self.id).creation_timestamp
        if not self.creation_timestamp:
            self.creation_timestamp = datetime.now()
        self.modified_timestamp = datetime.now()
        return super(Notification, self).save(*args, **kwargs)
