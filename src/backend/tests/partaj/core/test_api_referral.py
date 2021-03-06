from io import BytesIO
from unittest import mock

from django.test import TestCase

from rest_framework.authtoken.models import Token

from partaj.core import factories, models


@mock.patch("partaj.core.email.Mailer.send")
class ReferralApiTestCase(TestCase):
    """
    Test API routes and actions related to Referral endpoints.
    """

    # LIST TESTS
    def test_list_referrals_by_anonymous_user(self, _):
        """
        Anonymous users cannot make list requests on the referral endpoints.
        """
        response = self.client.get("/api/referrals/")
        self.assertEqual(response.status_code, 401)

    def test_list_referrals_by_random_logged_in_user(self, _):
        """
        Logged-in users cannot make list requests on the referral endpoints.
        """
        user = factories.UserFactory()
        response = self.client.get(
            "/api/referrals/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_list_referrals_by_admin_user(self, _):
        """
        Admin users cannot make list requests on the referral endpoints.
        """
        user = factories.UserFactory(is_staff=True)
        response = self.client.get(
            "/api/referrals/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    # RETRIEVE TESTS
    def test_retrieve_referral_by_anonymous_user(self, _):
        """
        Anonymous users cannot get a referral with the retrieve endpoint.
        """
        referral = factories.ReferralFactory()
        response = self.client.get(f"/api/referrals/{referral.id}/")
        self.assertEqual(response.status_code, 401)

    def test_retrieve_referral_by_random_logged_in_user(self, _):
        """
        Any random logged in user cannot get a referral with the retrieve endpoint.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory()
        response = self.client.get(
            f"/api/referrals/{referral.id}/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_retrieve_referral_by_admin_user(self, _):
        """
        Admins can retrieve any referral on the retrieve endpoint.
        """
        user = factories.UserFactory(is_staff=True)

        referral = factories.ReferralFactory()
        response = self.client.get(
            f"/api/referrals/{referral.id}/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], referral.id)

    def test_retrieve_referral_by_linked_user(self, _):
        """
        The user who created the referral can retrieve it on the retrieve endpoint.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory(user=user)
        response = self.client.get(
            f"/api/referrals/{referral.id}/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], referral.id)

    def test_retrieve_referral_by_linked_unit_member(self, _):
        """
        Members of the linked unit (through topic) can retrieve the referral.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory()
        referral.topic.unit.members.add(user)
        response = self.client.get(
            f"/api/referrals/{referral.id}/",
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], referral.id)

    # CREATE TESTS
    def test_create_referral_by_anonymous_user(self, _):
        """
        Anonymous users cannot create a referral.
        """
        topic = factories.TopicFactory()

        form_data = {
            "context": "le contexte",
            "prior_work": "le travail préalable",
            "question": "la question posée",
            "requester": "le demandeur ou la demandeuse",
            "topic": str(topic.id),
        }
        response = self.client.post("/api/referrals/", form_data,)
        self.assertEqual(response.status_code, 401)

    def test_create_referral_by_random_logged_in_user(self, _):
        """
        Any logged-in user can create a referral using the CREATE endpoint.
        """
        topic = factories.TopicFactory()
        urgency_level = factories.ReferralUrgencyFactory()
        user = factories.UserFactory()

        file1 = BytesIO(b"firstfile")
        file1.name = "the first file name"
        file2 = BytesIO(b"secondfile")
        file2.name = "the second file name"
        form_data = {
            "context": "le contexte",
            "files": (file1, file2),
            "prior_work": "le travail préalable",
            "question": "la question posée",
            "requester": "le demandeur ou la demandeuse",
            "topic": str(topic.id),
            "urgency_level": urgency_level.id,
            "urgency_explanation": "la justification de l'urgence",
        }
        response = self.client.post(
            "/api/referrals/",
            form_data,
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 201)

        referral = models.Referral.objects.get(id=response.json()["id"])
        # All simple fields match the incoming request
        self.assertEqual(referral.context, "le contexte")
        self.assertEqual(referral.prior_work, "le travail préalable")
        self.assertEqual(referral.question, "la question posée")
        self.assertEqual(referral.requester, "le demandeur ou la demandeuse")
        self.assertEqual(referral.urgency_level, urgency_level)
        self.assertEqual(referral.urgency_explanation, "la justification de l'urgence")
        # The correct foreign keys were added to the referral
        self.assertEqual(referral.topic, topic)
        self.assertEqual(referral.user, user)
        # The attachments for the referral were created and linked with it
        self.assertEqual(referral.attachments.count(), 2)
        self.assertEqual(referral.attachments.all()[0].file.read(), b"firstfile")
        self.assertEqual(referral.attachments.all()[0].name, "the first file name")
        self.assertEqual(referral.attachments.all()[1].file.read(), b"secondfile")
        self.assertEqual(referral.attachments.all()[1].name, "the second file name")
        # The "create" activity for the Referral is generated
        activities = models.ReferralActivity.objects.filter(referral__id=referral.id)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0].referral, referral)
        self.assertEqual(activities[0].actor, user)
        self.assertEqual(activities[0].verb, models.ReferralActivityVerb.CREATED)

    def test_create_referral_by_random_logged_in_user_with_invalid_form(self, _):
        """
        If the form is invalid (for example, missing a required field), referral creation
        should fail.
        """
        user = factories.UserFactory()
        topic = factories.TopicFactory()

        form_data = {
            "context": "le contexte",
            "prior_work": "le travail préalable",
            "requester": "le demandeur ou la demandeuse",
            "topic": str(topic.id),
            "urgency": models.Referral.URGENCY_2,
            "urgency_explanation": "la justification de l'urgence",
        }
        response = self.client.post(
            "/api/referrals/",
            form_data,
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"question": ["Ce champ est obligatoire."]},
        )

    def test_create_referral_by_admin_user(self, _):
        """
        Admin users can create referrals just like regular logged-in users.
        """
        topic = factories.TopicFactory()
        urgency_level = factories.ReferralUrgencyFactory()
        user = factories.UserFactory(is_staff=True, is_superuser=True)

        form_data = {
            "context": "le contexte",
            "prior_work": "le travail préalable",
            "question": "la question posée",
            "requester": "le demandeur ou la demandeuse",
            "topic": str(topic.id),
            "urgency_level": urgency_level.id,
            "urgency_explanation": "la justification de l'urgence",
        }
        response = self.client.post(
            "/api/referrals/",
            form_data,
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 201)

        referral = models.Referral.objects.get(id=response.json()["id"])
        # All simple fields match the incoming request
        self.assertEqual(referral.context, "le contexte")
        self.assertEqual(referral.prior_work, "le travail préalable")
        self.assertEqual(referral.question, "la question posée")
        self.assertEqual(referral.requester, "le demandeur ou la demandeuse")
        self.assertEqual(referral.urgency_level, urgency_level)
        self.assertEqual(referral.urgency_explanation, "la justification de l'urgence")
        # The correct foreign keys were added to the referral
        self.assertEqual(referral.topic, topic)
        self.assertEqual(referral.user, user)
        # The "create" activity for the Referral is generated
        activities = models.ReferralActivity.objects.filter(referral__id=referral.id)
        self.assertEqual(len(activities), 1)
        self.assertEqual(activities[0].referral, referral)
        self.assertEqual(activities[0].actor, user)
        self.assertEqual(activities[0].verb, models.ReferralActivityVerb.CREATED)

    # ANSWER TESTS
    def test_answer_referral_by_anonymous_user(self, _):
        """
        Anonymous users cannot answer a referral.
        """
        referral = factories.ReferralFactory()
        response = self.client.post(
            f"/api/referrals/{referral.id}/answer/", {"content": "answer content"}
        )
        self.assertEqual(response.status_code, 401)

    def test_answer_referral_by_random_logged_in_user(self, _):
        """
        Any random logged in user cannot answer a referral.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory()
        response = self.client.post(
            f"/api/referrals/{referral.id}/answer/",
            {"content": "answer content"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_answer_referral_by_admin_user(self, _):
        """
        Admin users can answer a referral.
        """
        user = factories.UserFactory(is_staff=True)

        referral = factories.ReferralFactory()
        response = self.client.post(
            f"/api/referrals/{referral.id}/answer/",
            {"content": "answer content"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ANSWERED)
        self.assertEqual(response.json()["answers"][0]["content"], "answer content")

    def test_answer_referral_by_linked_user(self, _):
        """
        The referral's creator cannot answer it themselves.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory(user=user)
        response = self.client.post(
            f"/api/referrals/{referral.id}/answer/",
            {"content": "answer content"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_answer_referral_by_linked_unit_member(self, _):
        """
        Members of the linked unit can answer a referral.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory()
        referral.topic.unit.members.add(user)
        response = self.client.post(
            f"/api/referrals/{referral.id}/answer/",
            {"content": "answer content"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ANSWERED)
        self.assertEqual(response.json()["answers"][0]["content"], "answer content")

    # ASSIGN TESTS
    def test_assign_referral_by_anonymous_user(self, _):
        """
        Anonymous users cannot perform actions, including assignments.
        """
        referral = factories.ReferralFactory()
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/", {"assignee_id": "42"}
        )
        self.assertEqual(response.status_code, 401)

    def test_assign_referral_by_random_logged_in_user(self, _):
        """
        Any random logged in user cannot assign a referral.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory()
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": "42"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_referral_by_admin_user(self, _):
        """
        Admin users can assign a referral.
        """
        user = factories.UserFactory(is_staff=True)

        referral = factories.ReferralFactory()
        assignee = factories.UserFactory()
        referral.topic.unit.members.add(assignee)
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ASSIGNED)
        self.assertEqual(response.json()["assignees"], [str(assignee.id)])

    def test_assign_referral_by_linked_user(self, _):
        """
        The referral's creator cannot assign it.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory(user=user)
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": "42"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_referral_by_linked_unit_member(self, _):
        """
        Regular members of the linked unit cannot assign a referral.
        """
        referral = factories.ReferralFactory()
        user = factories.UnitMembershipFactory(
            role=models.UnitMembershipRole.MEMBER, unit=referral.topic.unit
        ).user
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": "42"},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_referral_by_linked_unit_organizer(self, _):
        """
        Organizers of the linked unit can assign a referral.
        """
        referral = factories.ReferralFactory()
        user = factories.UnitMembershipFactory(
            role=models.UnitMembershipRole.OWNER, unit=referral.topic.unit
        ).user
        assignee = factories.UnitMembershipFactory(unit=referral.topic.unit).user

        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ASSIGNED)
        self.assertEqual(response.json()["assignees"], [str(assignee.id)])

    def test_assign_already_assigned_referral(self, _):
        """
        A referral which was assigned to one user can be assigned to an additional one,
        staying in the ASSIGNED state.
        """
        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        exsting_assignee = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit
        ).assignee
        user = factories.UnitMembershipFactory(
            role=models.UnitMembershipRole.OWNER, unit=referral.topic.unit
        ).user
        assignee = factories.UnitMembershipFactory(unit=referral.topic.unit).user

        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ASSIGNED)
        self.assertEqual(
            response.json()["assignees"], [str(exsting_assignee.id), str(assignee.id)]
        )

    # ASSIGN TESTS
    def test_unassign_referral_by_anonymous_user(self, _):
        """
        Anonymous users cannot perform actions, including assignment removals.
        """
        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignment = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit
        )
        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment.assignee.id},
        )
        self.assertEqual(response.status_code, 401)

    def test_unassign_referral_by_random_logged_in_user(self, _):
        """
        Any random logged in user cannot unassign an assignee from a referral.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignment = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit
        )
        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_unassign_referral_by_admin_user(self, _):
        """
        Admin users can unassign an assignee from a referral.
        """
        user = factories.UserFactory(is_staff=True)

        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignment = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit
        )
        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.RECEIVED)
        self.assertEqual(response.json()["assignees"], [])

    def test_unassign_referral_by_linked_user(self, _):
        """
        The referral's creator cannot unassign an assignee from it.
        """
        user = factories.UserFactory()

        referral = factories.ReferralFactory(
            state=models.ReferralState.ASSIGNED, user=user
        )
        assignment = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit
        )
        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=user)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_unassign_referral_by_linked_unit_member(self, _):
        """
        Regular members of the linked unit cannot unassign anyonce (incl. themselves)
        from a referral.
        """
        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignee = factories.UnitMembershipFactory(
            role=models.UnitMembershipRole.MEMBER
        ).user
        assignment = factories.ReferralAssignmentFactory(
            assignee=assignee, referral=referral, unit=referral.topic.unit,
        )
        response = self.client.post(
            f"/api/referrals/{referral.id}/assign/",
            {"assignee_id": assignment.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=assignment.assignee)[0]}",
        )
        self.assertEqual(response.status_code, 403)

    def test_unassign_referral_by_linked_unit_organizer(self, _):
        """
        Organizers of the linked unit can unassign a member from a referral.
        """
        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignment = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit,
        )

        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=assignment.created_by)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.RECEIVED)
        self.assertEqual(response.json()["assignees"], [])

    def test_unassign_referral_still_assigned_state(self, _):
        """
        When a member is unassigned from a referral which has other assignees, the
        referral remains in state ASSIGNED instead of moving to RECEIVED.
        """
        referral = factories.ReferralFactory(state=models.ReferralState.ASSIGNED)
        assignment_to_remove = factories.ReferralAssignmentFactory(
            referral=referral, unit=referral.topic.unit,
        )
        assignment_to_keep = factories.ReferralAssignmentFactory(referral=referral)

        response = self.client.post(
            f"/api/referrals/{referral.id}/unassign/",
            {"assignee_id": assignment_to_remove.assignee.id},
            HTTP_AUTHORIZATION=f"Token {Token.objects.get_or_create(user=assignment_to_remove.created_by)[0]}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], models.ReferralState.ASSIGNED)
        self.assertEqual(
            response.json()["assignees"], [str(assignment_to_keep.assignee.id)]
        )
