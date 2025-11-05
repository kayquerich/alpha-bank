from django.test import TestCase, Client as TestClient
from django.urls import reverse
from decimal import Decimal

from alphapayapp.models.User import User as AppUser
from alphapayapp.models.Client import Client as ClientModel
from alphapayapp.models.Transfer import Transfer


class ViewsTests(TestCase):
	def setUp(self):
		# test client used to simulate requests
		self.client = TestClient()

	def create_app_user(self, first_name='Test', last_name='User', email='user@example.com', password='pass1234', cpf='00011122233'):
		"""Helper: create an application user (this also creates Django user and Client via signals)."""
		user = AppUser.objects.create(
			first_name=first_name,
			last_name=last_name,
			email=email,
			password=password,
			cpf=cpf,
		)

		account = ClientModel.objects.get(user=user)
		return user, account, password

	def test_test_view_renders(self):
		resp = self.client.get(reverse('test'))
		self.assertEqual(resp.status_code, 200)
		# template should be used and contain the message
		self.assertTemplateUsed(resp, 'test.html')
		self.assertContains(resp, 'This is a test view')

	def test_cadastro_creates_user_and_redirects(self):
		data = {
			'first_name': 'New',
			'last_name': 'Person',
			'email': 'newperson@example.com',
			'password': 'newpass123',
			'cpf': '98765432100',
		}
		resp = self.client.post(reverse('cadastro'), data)
		# should redirect to login on success
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(AppUser.objects.filter(email=data['email']).exists())

	def test_login_authenticates_and_redirects(self):
		email = 'loginuser@example.com'
		pwd = 'secretpw'
		user, account, raw_pwd = self.create_app_user(email=email, password=pwd, cpf='11122233344')

		resp = self.client.post(reverse('login'), {'email': email, 'password': pwd})
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(resp.url, reverse('dashboard'))

	def test_dashboard_requires_login(self):
		resp = self.client.get(reverse('dashboard'))
		# should redirect to login with next param
		self.assertEqual(resp.status_code, 302)
		expected = f"{reverse('login')}?next={reverse('dashboard')}"
		self.assertIn(reverse('login'), resp.url)

	def test_transfer_success_and_balance_updates(self):
		# create sender and receiver
		sender_user, sender_account, sender_pwd = self.create_app_user(email='sender@example.com', password='pw1', cpf='22233344455')
		receiver_user, receiver_account, receiver_pwd = self.create_app_user(email='receiver@example.com', password='pw2', cpf='33344455566')

		# ensure balances
		sender_account.balance = Decimal('100.00')
		receiver_account.balance = Decimal('10.00')
		sender_account.save()
		receiver_account.save()

		# login as sender
		self.client.post(reverse('login'), {'email': sender_user.email, 'password': sender_pwd})

		amount = '25.50'
		resp = self.client.post(reverse('transfer'), {
			'reciver_account_number': receiver_account.account_number,
			'amount': amount,
			'description': 'Test payment',
		})

		# should redirect to success (302)
		self.assertEqual(resp.status_code, 302)

		# a transfer should exist and balances updated
		transfer = Transfer.objects.filter(sender=sender_account, receiver=receiver_account).first()
		self.assertIsNotNone(transfer)
		sender_account.refresh_from_db()
		receiver_account.refresh_from_db()
		self.assertEqual(sender_account.balance, Decimal('74.50'))
		self.assertEqual(receiver_account.balance, Decimal('35.50'))

	def test_transfer_insufficient_balance_shows_error(self):
		sender_user, sender_account, sender_pwd = self.create_app_user(email='lowbal@example.com', password='pw3', cpf='44455566677')
		receiver_user, receiver_account, receiver_pwd = self.create_app_user(email='rcv2@example.com', password='pw4', cpf='55566677788')

		sender_account.balance = Decimal('5.00')
		sender_account.save()

		self.client.post(reverse('login'), {'email': sender_user.email, 'password': sender_pwd})

		resp = self.client.post(reverse('transfer'), {
			'reciver_account_number': receiver_account.account_number,
			'amount': '10.00',
			'description': 'Too big',
		})

		# should render transfer.html with error message
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Dados inválidos')

	def test_profile_and_logout(self):
		user, account, pwd = self.create_app_user(email='prof@example.com', password='profpw', cpf='66677788899')
		# login
		self.client.post(reverse('login'), {'email': user.email, 'password': pwd})

		resp = self.client.get(reverse('profile'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, user.first_name)

		# logout should redirect to login
		resp2 = self.client.get(reverse('logout'))
		self.assertEqual(resp2.status_code, 302)
		self.assertEqual(resp2.url, reverse('login'))

