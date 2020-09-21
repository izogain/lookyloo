#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import argparse

from lookyloo.helpers import get_homedir


def validate_generic_config_file():
    with (get_homedir() / 'config' / 'generic.json').open() as f:
        generic_config = json.load(f)
    with (get_homedir() / 'config' / 'generic.json.sample').open() as f:
        generic_config_sample = json.load(f)
    # Check documentation
    for key in generic_config_sample.keys():
        if key == '_notes':
            continue
        if key not in generic_config_sample['_notes']:
            raise Exception(f'###### - Documentation missing for {key}')

    # Check all entries in the sample files are in the user file, and they have the same type
    for key in generic_config_sample.keys():
        if key == '_notes':
            continue
        if generic_config.get(key) is None:
            logger.warning(f'Entry missing in user config file: {key}. Will default to: {generic_config_sample[key]}')
            continue
        if not isinstance(generic_config[key], type(generic_config_sample[key])):
            raise Exception(f'Invalid type for {key}. Got: {type(generic_config[key])} ({generic_config[key]}), expected: {type(generic_config_sample[key])} ({generic_config_sample[key]})')

        if isinstance(generic_config[key], dict):
            # Check entries
            for sub_key in generic_config_sample[key].keys():
                if not isinstance(generic_config[key][sub_key], type(generic_config_sample[key][sub_key])):
                    raise Exception(f'Invalid type for {sub_key} in {key}. Got: {type(generic_config[key][sub_key])} ({generic_config[key][sub_key]}), expected: {type(generic_config_sample[key][sub_key])} ({generic_config_sample[key][sub_key]})')

    # Make sure the user config file doesn't have entries missing in the sample config
    for key in generic_config.keys():
        if key not in generic_config_sample:
            raise Exception(f'{key} is missing in the sample config file')


def validate_modules_config_file():
    with (get_homedir() / 'config' / 'modules.json').open() as f:
        modules_config = json.load(f)
    with (get_homedir() / 'config' / 'modules.json.sample').open() as f:
        modules_config_sample = json.load(f)

    for key in modules_config_sample.keys():
        if key == '_notes':
            continue
        if not modules_config.get(key):
            logger.warning(f'Entry missing in user config file: {key}. Will default to: {json.dumps(modules_config_sample[key], indent=2)}')
            continue


def update_user_configs():
    for file_name in ['generic', 'modules']:
        with (get_homedir() / 'config' / f'{file_name}.json').open() as f:
            try:
                generic_config = json.load(f)
            except Exception:
                generic_config = {}
        with (get_homedir() / 'config' / f'{file_name}.json.sample').open() as f:
            generic_config_sample = json.load(f)

        has_new_entry = False
        for key in generic_config_sample.keys():
            if key == '_notes':
                continue
            if generic_config.get(key) is None:
                print(f'{key} was missing in {file_name}, adding it.')
                generic_config[key] = generic_config_sample[key]
                has_new_entry = True
        if has_new_entry:
            with (get_homedir() / 'config' / f'{file_name}.json').open('w') as fw:
                json.dump(generic_config, fw, indent=2, sort_keys=True)


if __name__ == '__main__':
    logger = logging.getLogger('Lookyloo - Config validator')
    parser = argparse.ArgumentParser(description='Check the config files.')
    parser.add_argument('--check', default=False, action='store_true', help='Check if the sample config and the user config are in-line')
    parser.add_argument('--update', default=False, action='store_true', help='Update the user config with the entries from the sample config if entries are missing')
    args = parser.parse_args()

    if args.check:
        validate_generic_config_file()
        validate_modules_config_file()

    if args.update:
        update_user_configs()
