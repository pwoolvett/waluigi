# -*- coding: utf-8 -*-

"""Main module."""

import functools
import os

import luigi


def task_wraps(task_cls):
    """
    In order to make the behavior of a wrapper class nicer, we set the name of the new 
    class to the wrapped class, and copy over the docstring and module as well. This 
    makes it possible to pickle the wrapped class etc. Btw, this is a slight abuse of 
    functools.wraps. It's meant to be used only for functions, but it works for classes 
    too, if you pass updated=[]
    """
    return functools.wraps(task_cls, updated=[])


class multiple_inherits(object):
    """ Task inheritance.
     Usage:
     .. code-block:: python
         class TaskPathA(luigi.Task):
            a = luigi.IntParameter()
            # ...
         class TaskPathB(luigi.Task):
            b = luigi.IntParameter()
         @multiple_inherits(TaskPathA, TaskPathB):
        class MyTask(luigi.Task):
            def requires(self):
               return self.clone_parent()
             def run(self):
               print self.a # this will be defined
               print self.b # this will also be defined
               # ...
    """

    def __init__(self, *tasks_to_inherit):
        super(multiple_inherits, self).__init__()
        self.tasks_to_inherit = tasks_to_inherit

    def __call__(self, task_that_inherits):
        tasks_to_inherit = self.tasks_to_inherit
        for task_to_inherit in tasks_to_inherit:
            for param_name, param_obj in task_to_inherit.get_params():
                if not hasattr(task_that_inherits, param_name):
                    setattr(task_that_inherits, param_name, param_obj)

        # Modify task_that_inherits by subclassing it and adding methods
        @task_wraps(task_that_inherits)
        class Wrapped(task_that_inherits):
            def clone_parent(self, **args):
                task = self.clone(cls=tasks_to_inherit[0])
                for additional_task in tasks_to_inherit[1:]:
                    task = task.clone(cls=additional_task, **args)
                return task

        return Wrapped


class multiple_requires(object):
    """
    Same as @multiple_inherits, but also auto-defines the requires method.
    """

    def __init__(self, *tasks_to_require):
        super(multiple_requires, self).__init__()
        self.inherit_decorator = multiple_inherits(*tasks_to_require)
        self.tasks_to_require = tasks_to_require

    def __call__(self, task_that_requires):
        task_that_requires = self.inherit_decorator(task_that_requires)
        tasks_to_require = self.tasks_to_require

        # Modify task_that_requires by subclassing it and adding methods
        @task_wraps(task_that_requires)
        class Wrapped(task_that_requires):
            def requires(self):
                return (self.clone(x) for x in tasks_to_require)

        return Wrapped


# noinspection PyPep8Naming
class dct_requires(multiple_requires):
    def __init__(self, **tasks_to_require):
        self.inherit_decorator = multiple_inherits(*tasks_to_require.values())
        self.tasks_to_require = tasks_to_require

    def __call__(self, task_that_requires):
        task_that_requires = self.inherit_decorator(task_that_requires)
        tasks_to_require = self.tasks_to_require

        # Modify task_that_requires by subclassing it and adding methods
        @task_wraps(task_that_requires)
        class Wrapped(task_that_requires):
            def requires(self):
                return {k: self.clone(v) for k, v in tasks_to_require.items()}

        return Wrapped
