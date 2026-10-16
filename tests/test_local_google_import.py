import copy
import unittest
from scripts.import_local_google_export import convert

class ImportTests(unittest.TestCase):
    def meta(self):
        return {'as_of':'2026-10-16','target':{'entity_id':'fictional','branch_id':'one','place_id':'fictional-place','market':'CA'},'observation':{'id':'G1','source_url':'https://maps.example/place','captured_at':'2026-10-16','observed_at':'2026-10-16'}}
    def test_aggregate_not_sample(self):
        x=convert({'id':'fictional-place','rating':3.2,'userRatingCount':120,'reviews':[{'rating':5}]},self.meta(),'places')['observations'][0]
        self.assertEqual(x['google_reviews'],{'rating':3.2,'total_count':120,'visible_sample_count':1})
    def test_missing_not_zero(self):
        x=convert({'id':'fictional-place'},self.meta(),'places')['observations'][0]
        self.assertIsNone(x['google_reviews']['total_count'])
        self.assertIsNone(x['google_reviews']['visible_sample_count'])
    def test_wrong_place(self):
        with self.assertRaises(ValueError):convert({'id':'other'},self.meta(),'places')
    def test_operating_not_verified(self):
        x=convert({'id':'fictional-place','businessStatus':'OPERATIONAL'},self.meta(),'places')['observations'][0]
        self.assertEqual(x['operating_status'],'OPERATIONAL');self.assertNotIn('ownership_verification_status',x)
    def test_gbp_binding_required(self):
        with self.assertRaises(ValueError):convert({'totalReviewCount':0},self.meta(),'gbp')
    def test_gbp_pagination(self):
        m=self.meta();m['resource_name']='accounts/fictional/locations/one';m['target']['gbp_resource_name']=m['resource_name']
        x=convert({'averageRating':2.8,'totalReviewCount':30,'reviews':[],'nextPageToken':'fictional-token'},m,'gbp')['observations'][0]
        self.assertEqual(x['google_reviews']['total_count'],30);self.assertEqual(x['pagination'],'more_pages_available');self.assertNotIn('nextPageToken',x)
    def test_input_unchanged(self):
        m=self.meta();old=copy.deepcopy(m);convert({'id':'fictional-place'},m,'places');self.assertEqual(m,old)
