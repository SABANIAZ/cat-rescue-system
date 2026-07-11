from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import HomeBanner, Cat, RescueRequest, AdoptionRequest


class HomeBannerTests(TestCase):
    def test_home_page_shows_active_banners_in_slideshow(self):
        HomeBanner.objects.create(title='Rescue Drive', subtitle='Help us save more cats', is_active=True, order=1)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('home_slides', response.context)
        self.assertEqual(list(response.context['home_slides']), list(HomeBanner.objects.filter(is_active=True).order_by('order', 'id')))
        self.assertEqual(response.context['home_slides'][0].title, 'Rescue Drive')


class AboutPageStatsTests(TestCase):
    def test_about_page_uses_live_counts_for_rescue_and_adoption(self):
        Cat.objects.create(name='Milo', breed='Siamese', age='2', description='Friendly cat', status='Rescue')
        Cat.objects.create(name='Luna', breed='Persian', age='3', description='Gentle cat', status='Adopted')

        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rescued_cats_count'], 1)
        self.assertEqual(response.context['successful_adoptions_count'], 1)
        self.assertEqual(response.context['happy_families_count'], 1)
