from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer, Car

MANUFACTURER_LIST_URL = reverse("taxi:manufacturer-list")
DRIVER_LIST_URL = reverse("taxi:driver-list")
DRIVER_CREATE_URL = reverse("taxi:driver-create")
CAR_LIST_URL = reverse("taxi:car-list")


class PublicManufacturerTests(TestCase):

    def test_login_required(self):
        res = self.client.get(MANUFACTURER_LIST_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivateManufacturerTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test1234"
        )
        self.client.force_login(self.user)
        Manufacturer.objects.create(name="Test Manufacturer 01")
        Manufacturer.objects.create(name="Test Manufacturer 02")
        Manufacturer.objects.create(name="Another Manufacturer")

    def test_retrieve_manufacturers(self):
        response = self.client.get(MANUFACTURER_LIST_URL)
        self.assertEqual(response.status_code, 200)
        manufacturers = Manufacturer.objects.all()
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    def test_searching_manufacturer_find_existing_and_relevant(self):
        response = self.client.get(MANUFACTURER_LIST_URL, {"name": "Test"})
        self.assertContains(response, "Test Manufacturer 01")
        self.assertContains(response, "Test Manufacturer 02")
        self.assertNotContains(response, "Another Manufacturer")

    def test_searching_manufacturer_doesnt_find_not_existing(self):
        response = self.client.get(MANUFACTURER_LIST_URL, {"name": "noname"})
        self.assertNotContains(response, "Test Manufacturer 01")
        self.assertNotContains(response, "Test Manufacturer 02")
        self.assertNotContains(response, "Another Manufacturer")

    def test_searching_manufacturer_find_all_if_name_empty(self):
        response = self.client.get(MANUFACTURER_LIST_URL, {"name": ""})
        self.assertContains(response, "Test Manufacturer 01")
        self.assertContains(response, "Test Manufacturer 02")
        self.assertContains(response, "Another Manufacturer")


class PublicDriverTests(TestCase):

    def test_login_required(self):
        res = self.client.get(DRIVER_LIST_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivateDriverTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123"
        )
        self.client.force_login(self.user)
        for i in range(1, 3):
            get_user_model().objects.create_user(
                username=f"test_0{i}",
                password="test123",
                license_number="TES" + f"{i}" * 5
            )
        get_user_model().objects.create_user(
            username="somebody",
            password="test123",
            license_number="SOM12345"
        )

    def test_create_driver(self):
        form_data = {
            "username": "new_user",
            "password1": "user1234test",
            "password2": "user1234test",
            "first_name": "Test first",
            "last_name": "Test last",
            "license_number": "TES12345"
        }
        self.client.post(DRIVER_CREATE_URL, data=form_data)
        new_user = get_user_model().objects.get(username=form_data["username"])
        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.last_name, form_data["last_name"])
        self.assertEqual(new_user.license_number, form_data["license_number"])

    def test_searching_driver_find_existing_and_relevant(self):
        response = self.client.get(DRIVER_LIST_URL, {"username": "test"})
        self.assertContains(response, "test_01")
        self.assertContains(response, "test_02")
        self.assertNotContains(response, "somebody")

    def test_searching_driver_doesnt_find_not_existing(self):
        response = self.client.get(DRIVER_LIST_URL, {"username": "noname"})
        self.assertNotContains(response, "test_01")
        self.assertNotContains(response, "test_02")
        self.assertNotContains(response, "somebody")

    def test_searching_manufacturer_find_all_if_name_empty(self):
        response = self.client.get(DRIVER_LIST_URL, {"username": ""})
        self.assertContains(response, "test_01")
        self.assertContains(response, "test_02")
        self.assertContains(response, "somebody")


class PublicCarrTests(TestCase):

    def test_login_required(self):
        res = self.client.get(CAR_LIST_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivateCarTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test1234"
        )
        self.client.force_login(self.user)
        manufacturer = Manufacturer.objects.create(name="Test Manufacturer 01")
        Car.objects.create(model="Test Car 01", manufacturer=manufacturer)
        Car.objects.create(model="Test Car 02", manufacturer=manufacturer)
        Car.objects.create(model="Another Car", manufacturer=manufacturer)

    def test_retrieve_car(self):
        response = self.client.get(CAR_LIST_URL)
        self.assertEqual(response.status_code, 200)
        cars = Car.objects.all()
        self.assertEqual(
            list(response.context["car_list"]),
            list(cars)
        )
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_searching_car_find_existing_and_relevant(self):
        response = self.client.get(CAR_LIST_URL, {"model": "Test"})
        self.assertContains(response, "Test Car 01")
        self.assertContains(response, "Test Car 02")
        self.assertNotContains(response, "Another Car")

    def test_searching_car_doesnt_find_not_existing(self):
        response = self.client.get(CAR_LIST_URL, {"model": "noname"})
        self.assertNotContains(response, "Test Car 01")
        self.assertNotContains(response, "Test Car 02")
        self.assertNotContains(response, "Another Car")

    def test_searching_car_find_all_if_name_empty(self):
        response = self.client.get(CAR_LIST_URL, {"model": ""})
        self.assertContains(response, "Test Car 01")
        self.assertContains(response, "Test Car 02")
        self.assertContains(response, "Another Car")
