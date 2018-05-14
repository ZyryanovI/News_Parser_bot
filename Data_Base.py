import peewee

data_base = peewee.SqliteDatabase("data_base.db")


class Topics(peewee.Model):
    name = peewee.CharField(unique=True, primary_key=True)
    URL = peewee.CharField()
    description = peewee.CharField()

    class Meta:
        database = data_base


class Documents(peewee.Model):
    topic_ = peewee.ForeignKeyField(Topics)
    URL = peewee.CharField()
    title = peewee.CharField()
    last_update = peewee.DateTimeField()
    text = peewee.CharField()

    class Meta:
        database = data_base


class Teg(peewee.Model):
    document_ = peewee.ForeignKeyField(Documents)
    name = peewee.CharField()

    class Meta:
        database = data_base


class DocumentStatistic(peewee.Model):
    document_ = peewee.ForeignKeyField(Documents)
    frequency_distribution = peewee.CharField()
    length_distribution = peewee.CharField()

    class Meta:
        database = data_base


class TopicStatistic(peewee.Model):
    topic_ = peewee.ForeignKeyField(Topics)
    documents_number = peewee.IntegerField()
    average_length = peewee.IntegerField()
    frequency_distribution = peewee.CharField()
    length_distribution = peewee.CharField()

    class Meta:
        database = data_base

