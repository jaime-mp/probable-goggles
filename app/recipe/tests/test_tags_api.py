"""
Tests for the tags API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)

from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@example.com", password="test123"):
    """Create and return an user."""

    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(path=TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name="Spanish")
        Tag.objects.create(user=self.user, name="Italian")
        res = self.client.get(path=TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        other_user = create_user(
            email="other@example.com",
        )
        Tag.objects.create(user=other_user, name="Hamburger")
        tag = Tag.objects.create(user=self.user, name="Pasta")
        res = self.client.get(path=TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], tag.id)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(
            user=self.user,
            name="Sample tag",
        )
        url = detail_url(tag_id=tag.id)
        payload = {"name": "Updated tag"}
        res = self.client.patch(path=url, data=payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(
            user=self.user,
            name="Sample tag",
        )
        url = detail_url(tag_id=tag.id)
        res = self.client.delete(path=url)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name="Breakfast")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        recipe = Recipe.objects.create(
            user=self.user,
            title="Green eggs on toast",
            time_minutes=10,
            price=Decimal("1.50"),
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = Tag.objects.create(user=self.user, name="Breakfast")
        Tag.objects.create(user=self.user, name="Lunch")

        recipe1 = Recipe.objects.create(
            title="Eggs with bacon",
            time_minutes=10,
            price="2.0",
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title="Green eggs on toast",
            time_minutes=10,
            price="5.0",
            user=self.user
        )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
