#-*- coding: utf-8 -*-
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
#
# This file is part of HyperKitty.
#
# HyperKitty is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# HyperKitty is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# HyperKitty.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Peter Markou <markoupetr@gmail.com>
# 

from django.core.validators import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase

from hyperkitty.views.forms import RegistrationForm, isValidUsername


class RegistrationFormTestCase(TestCase):
    """
    Test the registration forms for proper behavior.

    """

    def test_init(self):
        # Test successful init without data.
        form = RegistrationForm()
        self.assertIsInstance(form, RegistrationForm)

    def test_registration_form_valid_data(self):
        # Valid informations.
        form = RegistrationForm(data={'username': 'peter',
                                      'email': 'peter@example.com',
                                      'password1': '37ertGH79',
                                      'password2': '37ertGH79'})

        # Check that form validation returns True with valid data.
        self.assertTrue(form.is_valid())

    def test_registration_form_mismatched_passwords(self):
        # Mismatched passwords. 
        form = RegistrationForm(data={'username': 'peter',
                                      'email': 'peter@example.com',
                                      'password1': 'dummy_password',
                                      'password2': 'a_different_password'})

        # Check that error message in form.errors is the expected.
        self.assertEqual(form.errors['password2'],
                         [u'Passwords do not match.'])

    def test_registration_form_username_exists(self):
        username = 'dave'
        # Create a user so we can verify that duplicate usernames
        # aren't permitted.
        User.objects.create_user(username, 'dave@example.com', '37ertGH79')

        # Already-existing username.
        form = RegistrationForm(data={'username': username,
                                      'email': 'dave@example.com',
                                      'password1': '37ertGH79',
                                      'password2': '37ertGH79'})

        # Ensure that ValidationError arises for isValidUsername(username),
        # given that username already exists.
        self.assertRaises(ValidationError, isValidUsername,
                          username)
