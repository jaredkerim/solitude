import json

from nose.tools import eq_, ok_

from lib.sellers.tests.utils import make_seller_paypal
from lib.transactions import constants
from lib.transactions.models import Transaction
from solitude.base import APITest


class TestSeller(APITest):

    def setUp(self):
        self.api_name = 'generic'
        self.uuid = 'sample:uid'
        self.list_url = self.get_list_url('transaction')
        self.seller, self.paypal, self.product = (
            make_seller_paypal('paypal:%s' % self.uuid))
        self.trans = Transaction.objects.create(amount=5,
                                            seller_product=self.product,
                                            provider=constants.SOURCE_PAYPAL,
                                            uuid=self.uuid)
        self.detail_url = self.get_detail_url('transaction', self.trans.pk)

    def test_list_allowed(self):
        self.allowed_verbs(self.list_url, ['get', 'post'])
        self.allowed_verbs(self.detail_url, ['get'])

    def test_list(self):
        res = self.client.get(self.list_url, data={'uuid': self.uuid})
        eq_(res.status_code, 200)
        eq_(json.loads(res.content)['objects'][0]['uuid'], self.uuid)

    def test_get(self):
        res = self.client.get(self.detail_url)
        eq_(res.status_code, 200)
        eq_(json.loads(res.content)['uuid'], self.uuid)

    def test_post_uuid(self):
        data = {'provider': constants.SOURCE_BANGO,
                'seller_product': '/generic/product/%s/' % self.product.pk}
        res = self.client.post(self.list_url, data=data)
        eq_(res.status_code, 201)
        ok_(json.loads(res.content)['uuid'])

    def test_provider(self):
        res = self.client.get(self.list_url, data={'provider':
                                                   constants.SOURCE_BANGO})
        eq_(res.status_code, 200)
        eq_(json.loads(res.content)['meta']['total_count'], 0, res.content)
