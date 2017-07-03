import time
from functools import wraps

def retry(ExceptionToCheck, tries, delay, backoff, verbose=False):

    assert isinstance(tries, int)
    assert isinstance(delay, int) or isinstance(delay, float)
    assert isinstance(backoff, int) or isinstance(backoff, float)

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            try_count = 1
            mtries, mdelay = tries, delay
            while tries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    if verbose:
                        msg = 'Try {} Failed, Exception: {}, Retrying in {} seconds...'.format(try_count, e, mdelay)
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
                    try_count += 1
            return f(*args, *kwargs)

        return f_retry

    return deco_retry