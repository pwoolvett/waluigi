#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `waluigi` package."""
import re

import luigi
from luigi import util as luigi_util

from waluigi.tasks import PipelineInput, BaseTask
from waluigi.factories import make_pipeline, make_task
from waluigi.utils import save_object, load_object


def sample_data():
    sample_data_location = 'sample_data.pickle'

    input_data = 'rdw NEOIEROEO RKNE CNFDÑOFOOF ÓFFFFN ' + \
                 'red 20/09/1993 a.c. 18 w 30k $55544 ds sdjnsndsds blue carpa viva ' + \
                 'loco@jona.com +56 994541139 ' + \
                 ''

    input_params_ = {
        'input_data': input_data,
    }

    save_object(input_params_, sample_data_location)

    return sample_data_location


def att_pipeline(sample_data):
    """test Pipeline"""

    class PipeIn(PipelineInput):
        REQUIRED = {'input_data'}

    @luigi_util.requires(PipeIn)
    class DetectEmails(BaseTask):
        def run_impl(self, data):
            print(data)
            data.update(**{
                'mails': [
                    *re.findall(
                        r"\w+\@\w+\.(?:\w+)+",
                        data['input_data'].lower()
                    )
                ]
            })
            return data

    @luigi_util.requires(DetectEmails)
    class DetectColors(BaseTask):
        def run_impl(self, data):
            print(data)
            data.update(**{
                'color': [
                    color
                    for color in [
                        'blue',
                        'green',
                        'red',
                    ]
                    if color in data['input_data'].lower()
                ]
            })
            return data

    SamplePipeline = make_pipeline(
        parameter_task=PipeIn,
        final_task=DetectColors,
    )

    tasks = [
        SamplePipeline(
            input_location=sample_data,
            initial=10,
            increment=10,
            data_folder='/home/pwoolvett/codes/waluigi'
        )
    ]
    luigi.build(tasks, local_scheduler=True)

    print('a')


def working():
    from shutil import copy2 as copy

    import luigi
    from luigi.parameter import MissingParameterException
    from luigi.util import requires

    class InputAttributeProcessor(luigi.Task):
        attribute_processor_input = luigi.Parameter()

        def run(self):
            input_params_ = load_object(self.attribute_processor_input)
            required_and_not_present = [
                param
                for param in [
                    'input_data',
                ]
                if param not in input_params_
            ]
            if required_and_not_present:
                raise MissingParameterException(
                    f"{self.__class__.__name__}: requires the '{required_and_not_present}' parameter(s) to be set"
                )

        def output(self):
            return luigi.LocalTarget(self.attribute_processor_input)

    @requires(InputAttributeProcessor)
    class DetectEmails(BaseTask):
        def run_impl(self, data):
            out = re.findall(
                r"\w+\@\w+\.(?:\w+)+",
                data['input_data'].lower()
            )
            data['mails'] = out
            return data

    @requires(DetectEmails)
    class DetectColors(BaseTask):
        def run_impl(self, input_data):
            out = [
                color
                for color in [
                    'blue',
                    'green',
                    'red',
                ]
                if color in input_data['input_data'].lower()
            ]
            input_data['colors'] = out
            return input_data

    @requires(InputAttributeProcessor, DetectColors)
    class AttributeProcessor(BaseTask):
        def run(self):
            copy(self.input()[1].path, self.output().path)

    def gen_attribute_processor_sample_data():
        # input_data = load_object(r'luigi_test/preprocessors/400_SplitDataset_x.pickle')
        input_data = 'rdw NEOIEROEO RKNE CNFDÑOFOOF ÓFFFFN RED 20/09/1993 a.c. ' \
                     '18 w 30k $55544 ds blue sdjnsndsds carpa viva ' \
                     '18.312.826-4  +56 994541139 Blue' \
                     ' loco@juna.com '

        input_params_ = {
            'input_data': input_data,
        }
        return input_params_

    delta = 10 ** 0
    data_folder = '/home/pwoolvett/codes/waluigi/'
    attribute_processor_input = data_folder + f'{delta}_attribute_processor_input.pickle'
    input_params = gen_attribute_processor_sample_data()
    save_object(input_params, attribute_processor_input)

    tasks = [
        AttributeProcessor(
            attribute_processor_input=attribute_processor_input,
            initial=delta,
            increment=delta,
            data_folder=data_folder
        )
    ]
    luigi.build(tasks, local_scheduler=True)


if __name__ == '__main__':
    # loc = sample_data()
    # att_pipeline(loc)
    working()
    pass
