# -*- coding: utf-8 -*-

import time


def get_current_time_as_str():
    """
    Returns current time as a string
    :return:
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
