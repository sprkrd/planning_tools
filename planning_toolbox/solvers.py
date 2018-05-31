import re
import subprocess
import time

from tempfile import NamedTemporaryFile


class CmdPlanner:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_cmd(self, domain_file, problem_file):
        raise NotImplementedError()

    def _parse_out_(self, out):
        raise NotImplementedError()

    def run_planner(self, domain_file, problem_file, timeout=None):
        cmd = self.get_cmd(domain_file, problem_file)
        start = time.time()
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=timeout)
            stdout = process.stdout.decode("ascii")
            stderr = process.stderr.decode("ascii")
            result = self._parse_out_(stdout)
            result["timeout"] = False
            result["stdout"] = stdout
            result["stderr"] = stderr
        except subprocess.TimeoutExpired:
            result = {
                    "plan-found": False,
                    "timeout": True,
            }
        except subprocess.CalledProcessError as e:
            # print(e)
            # print(e.stderr)
            result = {
                    "plan-found": False,
                    "timeout": False,
                    "stdout": e.stdout.decode("ascii"),
                    "stderr": e.stderr.decode("ascii"),
            }
        result["time-wall"] = time.time() - start
        return result

    def __call__(self, problem, timeout=None):
        with NamedTemporaryFile(prefix="domain_", suffix=".pddl", buffering=0) as fdomain,\
             NamedTemporaryFile(prefix="problem_", suffix=".pddl", buffering=0) as fproblem:
            fdomain.write(str(problem.domain).encode("ascii"))
            fproblem.write(str(problem).encode("ascii"))
            result = self.run_planner(fdomain.name, fproblem.name, timeout=timeout)
        return result


class FFPlanner(CmdPlanner):

    RE_ACTION = re.compile(r"(?:step|)\s*\d+: ([A-Z0-9_\- ]+)")
    RE_PLAN_COST = re.compile(r"plan cost: ([0-9\.]+)")
    RE_ELAPSED = re.compile(r"\s*([0-9\.]+) seconds total time")

    def get_cmd(self, domain_file, problem_file):
        cmd = ["ff", "-o", domain_file, "-f", problem_file]
        cmd += get_options(*self.args, **self.kwargs)
        return cmd

    def _parse_out_(self, out):
        result = {}
        lines = out.splitlines()
        total_cost = None
        total_elapsed = None
        actions = None
        try:
            idx_start_plan = lines.index("ff: found legal plan as follows")
            actions = []
            reading_actions = True
            for l in lines[idx_start_plan+1:]:
                if reading_actions:
                    mact = FFPlanner.RE_ACTION.match(l)
                    if mact:
                        action = tuple(mact.group(1).lower().split())
                        actions.append(action)
                    else:
                        reading_actions = False
                        mcost = FFPlanner.RE_PLAN_COST.match(l)
                        if mcost: total_cost = float(mcost.group(1))
                else:
                    melap = FFPlanner.RE_ELAPSED.match(l)
                    if melap:
                        total_elapsed = float(melap.group(1))
                        break   
            result["plan-found"] = True
        except ValueError:
            result["plan-found"] = False
        result["plan"] = actions
        if total_cost is None:
            result["total-cost"] = None if actions is None else len(actions)
        else:
            result["total-cost"] = total_cost
        result["total-elapsed"] = total_elapsed
        return result


class FDPlanner(CmdPlanner):

    RE_ACTION = re.compile(r"([A-Za-z0-9_\- ]+) \([0-9]+\)")
    RE_PLAN_COST = re.compile(r"Plan cost: ([0-9]+)")
    RE_ELAPSED = re.compile(r"Total time: ([0-9\.]+)s")

    def get_cmd(self, domain_file, problem_file):
        cmd = ["fast-downward.py", domain_file, problem_file]
        cmd += get_options(*self.args, **self.kwargs)
        return cmd

    def _parse_out_(self, out):
        result = {}
        lines = out.splitlines()
        total_cost = None
        total_elapsed = None
        actions = None
        try:
            idx_start_plan = lines.index("Solution found!")
            actions = []
            reading_actions = True
            reading_cost = False
            for l in lines[idx_start_plan+2:]:
                if reading_actions:
                    mact = FDPlanner.RE_ACTION.match(l)
                    if mact:
                        action = tuple(mact.group(1).split())
                        actions.append(action)
                    else:
                        reading_actions = False
                        reading_cost = True
                elif reading_cost:
                    mcost = FDPlanner.RE_PLAN_COST.match(l)
                    if mcost:
                        total_cost = int(mcost.group(1))
                        reading_cost = False
                else:
                    melap = FDPlanner.RE_ELAPSED.match(l)
                    if melap:
                        total_elapsed = float(melap.group(1))
                        break   
            result["plan-found"] = True
        except ValueError:
            result["plan-found"] = False
        result["plan"] = actions
        result["total-cost"] = total_cost
        result["total-elapsed"] = total_elapsed
        return result


#############
# UTILITIES #
#############

def get_options(*args, **kwargs):
    options = list(args)
    for opt,val in kwargs.items():
        prefixed_opt = ("--" if len(opt) > 1 else "-") + opt
        if isinstance(val, bool):
            if val: options.append(prefixed_opt)
        else:
            options += [prefixed_opt, str(val)]
    return options

