#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    
"""

import os
from shutil import copy2 as copy
from typing import ClassVar, Union, Optional, Callable

import luigi
from luigi import util as luigi_util
from luigi.parameter import MissingParameterException

from waluigi.parameters import Folder
from .utils import load_object, save_object, no_op


class BaseTask(luigi.Task):
    initial = luigi.IntParameter(significant=False)
    """Filename persistence: initial number"""

    increment = luigi.IntParameter(significant=False)
    """The step to use when the task is part of a pipeline"""

    data_folder = Folder(significant=False)
    """Defines the location where the files will be stored"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        input_ = load_object(self.input().path)

        data_ = self.run_impl(input_)

        save_object(data_, self.output().path)

    def run_impl(self, *args, **kwargs):
        """Inheritors must implement this method instead of the run method"""
        raise NotImplementedError

    def output(self):
        try:
            input_ = self.input()
            if input_:
                while True:  # neccesary in if requiring a task with multi-outputs
                    try:
                        iter(input_)
                        input_ = input_[-1]
                    except TypeError:
                        break
                try:
                    last_number = int(os.path.basename(input_.path).split('_')[0])
                except ValueError:
                    last_number = self.initial

            else:
                last_number = self.initial
        except BaseException as e:
            print(e)
        return luigi.LocalTarget(
            "{}{}_{}.pickle".format(
                self.data_folder,
                last_number + self.increment,
                type(self).__name__
            )
        )


class PipelineInput(luigi.Task):
    input_location = luigi.Parameter()

    REQUIRED = {}

    def run(self):
        input_params_ = load_object(self.input_location)
        required_and_not_present = [
            param
            for param in self.REQUIRED
            if param not in input_params_
        ]
        if required_and_not_present:
            raise MissingParameterException(
                "{}: requires the '{}' parameter(s) to be set".format(
                    self.__class__.__name__,
                    required_and_not_present
                )
            )

    def output(self):
        return luigi.LocalTarget(self.input_location)

