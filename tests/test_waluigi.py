#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `waluigi` package."""
import re

import luigi
import pytest

from waluigi.factories import make_pipeline, make_task, PipelineInput, make_input
from waluigi.utils import save_object


@pytest.fixture
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


def detect_email(self,*a,**kw):

    dct = a[0]
    out = [
            *re.findall(r'.+@\.(?:.+)+', dct['input_data'].lower())
        ]

    dct['mails'] = out

    return dct

def test_pipeline(sample_data):
    """test Pipeline

                                                                               SamplePipeline
                                             +-------------------------------------------------------------------------------------+
                                             |                                                                                     |
                 {                           |                                                                                     |
                   'input_data': ...,        |                                                                                     |
                   'param1': ..              |                                                                                     |
                 }                           |    +----------+       +--------------+        +------------+                        |
              +------------------------------>    |  PipeIn  +-------> DetectEmails +-------->DetectColors+----------->            |
                                             |    +----------+       +--------------+        +------------+                        |
                                             |          |                    |                     |                               |
                                             |          v                    v                     v                               |
                                             |                                                                                     |
                                             |                                                                                     |
                                             |                                                                                     |
                                             +-------------------------------------------------------------------------------------+

    """


    PipeIn = make_input(required='input_data')

    DetectEmails = make_task(
        name='DetectEmails',
        tasks_to_require=PipeIn,
        run_impl=detect_email
    )

    DetectColors = make_task(
        name='DetectColors',
        tasks_to_require=DetectEmails,
        run_impl=lambda dct: {
            'color': [
                color
                for color in [
                    'blue',
                    'green',
                    'red',
                ]
                if color in dct['text'].lower()
            ]
        }
    )

    SamplePipeline = make_pipeline(
        parameter_task=PipeIn,
        # final_task=DetectColors,
        final_task=DetectEmails,
    )

    tasks = [
        SamplePipeline(
            input_location=sample_data,
            initial=10,
            increment=10,
            data_folder='./'
        )
    ]
    luigi.build(tasks, local_scheduler=True)

    print('a')
