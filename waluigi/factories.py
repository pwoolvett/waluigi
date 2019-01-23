#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    
"""

from shutil import copy2 as copy
from typing import Callable, ClassVar

from luigi import util as luigi_util

from .utils import no_op, ensure_iterable
from .tasks import BaseTask, PipelineInput


def make_task(
    name: str,
    tasks_to_require: ClassVar[BaseTask],
    run_impl: Callable
) -> ClassVar[BaseTask]:
    """BaseTask factory

    :param tasks_to_require:
    :param run_impl:
    :return:
    """

    run_ = run_impl or no_op

    tasks_to_require = ensure_iterable(tasks_to_require)

    cls_ = type(name, (BaseTask,), {'run_impl': run_})

    if tasks_to_require:
        cls_ = luigi_util.requires(*tasks_to_require)(cls_)
        # @luigi_util.requires(*tasks_to_require)
        # class Atask(BaseTask):
        #     run_impl = run_
    # else:
    #     class Atask(BaseTask):
    #         run_impl = run_

    return cls_


def make_input(required):
    required = ensure_iterable(required)

    class PipeIn(PipelineInput):
        REQUIRED = required

    return PipeIn


def make_pipeline(
    parameter_task: ClassVar[PipelineInput],
    final_task: ClassVar[BaseTask],
) -> ClassVar[BaseTask]:
    """Creates a pipeline task."""

    @luigi_util.requires(parameter_task, final_task)
    class Pipeline(BaseTask):
        def run(self):
            copy(self.input()[1].path, self.output().path)

    return Pipeline
