#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    
"""
import os
from luigi import Parameter
from luigi.parameter import ParameterException


class Folder(Parameter):
    """Folder parameter which validates the existence"""
    def parse(self, x):
        """Appends trailing slash to force folder description"""
        return x if x.endswith('/') else x+'/'

    def normalize(self, x):
        """Validates folder exist"""
        if not os.path.isdir(x):
            raise ParameterException(f"Folder parameter {x} can't be found")

        return x
