# -*- coding: utf-8 -*-

import random
import string


def random_str(n=20):
    return ''.join(random.sample(string.ascii_letters + string.digits, n))
