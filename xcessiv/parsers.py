"""The functions in this module parse JSON inputs from an Xcessiv notebook"""
from __future__ import absolute_import, print_function, division, unicode_literals
from sklearn.model_selection import train_test_split
from xcessiv.functions import import_object_from_string_code
from xcessiv import exceptions
import numpy as np


def return_main_data_from_json(input_json):
    """Returns main data set from input JSON

    Args:
        input_json (dict): "Extraction" dictionary

    Returns:
        X (numpy.ndarray): Features

        y (numpy.ndarray): Labels
    """
    if not input_json['main_dataset']['source']:
        raise exceptions.UserError('Source is empty')

    extraction_code = "".join(input_json['main_dataset']["source"])
    extraction_function = import_object_from_string_code(extraction_code,
                                                         "extract_main_dataset")

    try:
        X, y = extraction_function()
    except Exception as e:
        raise exceptions.UserError('User code exception', exception_message=str(e))

    X, y = np.array(X), np.array(y)

    return X, y


def return_train_data_from_json(input_json):
    """Returns train data set from input JSON

    Args:
        input_json (dict): "Extraction" dictionary

    Returns:
        X (numpy.ndarray): Features

        y (numpy.ndarray): Labels
    """
    X, y = return_main_data_from_json(input_json)

    if input_json['test_dataset']['method'] == 'split_from_main':
        X, X_test, y, y_test = train_test_split(
            X,
            y,
            test_size=input_json['test_dataset']['split_ratio'],
            random_state=input_json['test_dataset']['split_seed'],
            stratify=y
        )

    if input_json['meta_feature_generation']['method'] == 'holdout_split':
        X, X_test, y, y_test = train_test_split(
            X,
            y,
            test_size=input_json['meta_feature_generation']['split_ratio'],
            random_state=input_json['meta_feature_generation']['seed'],
            stratify=y
        )

    return X, y


def return_test_data_from_json(input_json):
    """Returns test data set from input JSON

    Args:
        input_json (dict): "Extraction" dictionary

    Returns:
        X (numpy.ndarray): Features

        y (numpy.ndarray): Labels
    """
    if input_json['test_dataset']['method'] == 'split_from_main':
        X, y = return_main_data_from_json(input_json)
        X, X_test, y, y_test = train_test_split(
            X,
            y,
            test_size=input_json['test_dataset']['split_ratio'],
            random_state=input_json['test_dataset']['split_seed'],
            stratify=y
        )

        return X_test, y_test

    if input_json['test_dataset']['method'] == 'source':
        if 'source' not in input_json['test_dataset'] or \
                not input_json['test_dataset']['source']:
            raise exceptions.UserError('Source is empty')

        extraction_code = "".join(input_json['test_dataset']["source"])
        extraction_function = import_object_from_string_code(extraction_code,
                                                             "extract_test_dataset")
        X_test, y_test = extraction_function()

        return np.array(X_test), np.array(y_test)


def return_holdout_data_from_json(input_json):
    """Returns holdout data set from input JSON

    Args:
        input_json (dict): "Extraction" dictionary

    Returns:
        X (numpy.ndarray): Features

        y (numpy.ndarray): Labels
    """
    if input_json['meta_feature_generation']['method'] == 'holdout_split':
        X, y = return_main_data_from_json(input_json)

        if input_json['test_dataset']['method'] == 'split_from_main':
            X, X_test, y, y_test = train_test_split(
                X,
                y,
                test_size=input_json['test_dataset']['split_ratio'],
                random_state=input_json['test_dataset']['split_seed'],
                stratify=y
            )

        X, X_holdout, y, y_holdout = train_test_split(
            X,
            y,
            test_size=input_json['meta_feature_generation']['split_ratio'],
            random_state=input_json['meta_feature_generation']['seed'],
            stratify=y
        )

        return X_holdout, y_holdout

    if input_json['meta_feature_generation']['method'] == 'holdout_source':
        if 'source' not in input_json['meta_feature_generation'] or \
                not input_json['meta_feature_generation']['source']:
            raise exceptions.UserError('Source is empty')

        extraction_code = "".join(input_json['meta_feature_generation']["source"])
        extraction_function = import_object_from_string_code(extraction_code,
                                                             "extract_holdout_dataset")
        X_holdout, y_holdout = extraction_function()

        return np.array(X_holdout), np.array(y_holdout)


def return_estimator_from_json(input_json):
    """Returns estimator from base learner origin

    Args:
        input_json (dict): "Extraction" dictionary

    Returns:
        est (estimator): Estimator object
    """
    extraction_code = "".join(input_json['source'])
    estimator = import_object_from_string_code(extraction_code, "base_learner")
    return estimator