from datetime import timedelta
from random import randrange

from django.contrib.auth import get_user_model

import factory

from . import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    title = factory.Faker("prefix")
    unit_name = factory.Faker("company")
    username = factory.Faker("email")


class UnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Unit

    name = factory.Faker("company")


class UnitMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UnitMembership

    role = factory.Faker("word", ext_word_list=models.UnitMembershipRole.values)
    user = factory.SubFactory(UserFactory)
    unit = factory.SubFactory(UnitFactory)


class UnitMemberFactory(UserFactory):
    class Meta:
        model = get_user_model()

    membership = factory.RelatedFactory(UnitMembershipFactory, "user")


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic

    name = factory.Faker("text", max_nb_chars=models.Topic.name.field.max_length)
    unit = factory.SubFactory(UnitFactory)


class ReferralUrgencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ReferralUrgency

    name = factory.Faker(
        "text", max_nb_chars=models.ReferralUrgency.name.field.max_length
    )
    is_default = factory.Faker("boolean")
    requires_justification = factory.Faker("boolean")

    @factory.lazy_attribute
    def duration(self):
        """
        Generate a random duration for the urgency level.
        """
        return timedelta(days=randrange(2, 30))


class ReferralFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Referral

    context = factory.Faker("text", max_nb_chars=500)
    prior_work = factory.Faker("text", max_nb_chars=500)
    question = factory.Faker("text", max_nb_chars=500)
    requester = factory.Faker("name")
    topic = factory.SubFactory(TopicFactory)
    urgency_level = factory.SubFactory(ReferralUrgencyFactory)
    user = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def urgency_explanation(self):
        """
        Only generate an explanation if the urgency level requires it.
        """
        return (
            factory.Faker("text", max_nb_chars=500).generate()
            if self.urgency_level.requires_justification
            else ""
        )


class ReferralAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ReferralAssignment

    referral = factory.SubFactory(ReferralFactory)
    created_by = factory.SubFactory(UserFactory)
    unit = factory.SubFactory(UnitFactory)

    @factory.lazy_attribute
    def assignee(self):
        """
        Generate a membership to the unit with a brand new user and make this new user
        the assignee.
        """
        membership = UnitMembershipFactory(unit=self.unit)
        return membership.user

    @factory.lazy_attribute
    def created_by(self):
        """
        Generate a membership to the unit with a brand new user and have this news user
        be the the assignment creator.
        """
        membership = UnitMembershipFactory(
            unit=self.unit, role=models.UnitMembershipRole.OWNER
        )
        return membership.user
