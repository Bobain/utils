import sys
import datetime
import time
from functools import wraps

def syscmd_with_stdout(cmd):
    import subprocess
    import sys
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for c in iter(lambda: process.stdout.read(1), ''):
        sys.stdout.write(c)

class TimestampedPrint():
    def __enter__(self):
        self.old_f = sys.stdout
        class F:
            old_f = sys.stdout
            def write(self, x):
                # x.replace("\n", " \t[%s]\n" % str(datetime.datetime.now()))
                self.old_f.write(x if x== "\n" else
                            "[%s] %s" %(str(datetime.datetime.now()),
                                        x.replace("\n", "\n %s  " % (" "*len(str(datetime.datetime.now())))
                                                  )
                                        )
                            )
        sys.stdout = F()
        return sys.stdout
    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_f

class ExtraIndentPrint():
    def __enter__(self):
        self.old_f = sys.stdout
        class F:
            old_f = sys.stdout
            def write(self, x):
                self.old_f.write(x if x== "\n" else "\t%s" % x)
        sys.stdout = F()
        return sys.stdout
    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_f


def verbose_func(fn, msg=None, with_extra_indent=True):
    if msg is None:
        msg = '%s running' % str(fn)

    @wraps(fn)
    def with_blahblah(*args, **kwargs):
        start_time = time.time()
        print(msg)
        if with_extra_indent:
            with ExtraIndentPrint():
                ret = fn(*args, **kwargs)
        else:
            ret = fn(*args, **kwargs)
        print("\t%s ended. it took : %.2f" % (msg, time.time() - start_time))
        return ret

    return with_blahblah