# !/usr/bin/env python3
# Copyright (C) 2017  Qrama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=c0111,c0301,c0325, r0903,w0406
import os
from subprocess import check_output, check_call, Popen
from sojobo_api import settings
from sojobo_api.api import w_errors as errors, w_datastore as datastore, w_juju as juju
from flask import abort
import yaml
import json


CRED_KEYS = ['access-key', 'secret-key']


def create_controller(name, region, credential, username, password):
    Popen(["python3", "{}/scripts/bootstrap_aws_controller.py".format(settings.SOJOBO_API_DIR),
           name, region, credential, username, password])


def get_supported_series():
    return ['trusty', 'xenial', 'yakkety']


def get_supported_regions():
    return ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
            'eu-west-1', 'eu-west-2', 'eu-central-1', 'ap-south-1', 'ap-southeast-1',
            'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2', 'sa-east-1']


def get_cred_keys():
    return CRED_KEYS


def check_valid_credentials(credentials):
    wrong_keys = []
    if len(CRED_KEYS) == len(list(credentials.keys())):
        for cred in CRED_KEYS:
            if cred not in list(credentials.keys()):
                wrong_keys.append(cred)
    if len(wrong_keys) > 0:
        error = errors.key_does_not_exist(wrong_keys)
        abort(error[0], error[1])


def generate_cred_file(name, credentials):
    print(credentials)
    result = {
        'type': 'access-key',
        'name': name,
        'key': str(json.dumps({'access-key': credentials['credential']['access-key'], 'secret-key': credentials['credential']['secret-key']}))
    }
    return result


def generate_update_cred_file(filepath):
    with open(filepath) as json_data:
        data = json.load(json_data)
    return data


def add_credential(user, juju_username, juju_password, credential):
    check_valid_credentials(credential['credential'])
    datastore.add_credential(user, credential)
    Popen(["python3", "{}/scripts/add_aws_credential.py".format(settings.SOJOBO_API_DIR),
           user, juju_username, juju_password, str(credential)])
    return 202, 'Credentials are being added for user {}'.format(user)
