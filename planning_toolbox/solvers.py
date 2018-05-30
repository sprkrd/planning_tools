import re
import subprocess

from tempfile import NamedTemporaryFile


class CmdPlanner:

    def __init__(self, *args, **kwargs):
        self.parameters = parameters
        self.round_costs = round_costs

    def get_cmd(self, domain_file, problem_file):
        raise NotImplementedError()

    def _parse_out_(self, out):
        raise NotImplementedError()

    def run_planner(self, domain_file, problem_file, timeout=None):
        cmd = self.get_cmd(domain_file, problem_file)
        parameters = self.parameters
        timeout = None if self._supports_timeout_() else parameters.get('timeout', None)
        try:
            out = subprocess.check_output(cmd)
            out = out.decode('ascii')
            result = self._parse_out_(out)
            result['timeout'] = False
            result['out'] = out
        except subprocess.TimeoutExpired:
            result = {
                    'plan-found': False,
                    'timeout': True,
            }
        except subprocess.CalledProcessError as e:
            result = {
                    'plan-found': False,
                    'out': e.output.decode('ascii')
            }
        return result

    def __call__(self, problem):
        with NamedTemporaryFile(prefix="domain", suffix=".pddl") as fdomain,\
             NamedTemporaryFile(prefix="problem", suffix=".pddl") as fproblem:
            fdomain.write(str(problem.domain).encode("ascii"))
            fproblem.write(str(problem).encode("ascii"))
            result = self.run_planner(fdomain.name, fproblem.name)
        return result


FF_REGEX = re.compile(
r"""ff: found legal plan as follows
step\s*(?P<actions>(?:[0-9]+: [\sA-Z_0-9\-]*)*)
plan cost: (?P<cost>[0-9]+\.[0-9]*)""")

FF_ELAPSED = re.compile(r"(?P<elapsed>[0-9]+\.[0-9]+) seconds total time")

class FFPlanner(CmdPlanner):

    SUPPORTS_TIMEOUT = False

    def get_cmd(self, domain_file, problem_file):
        cmd = ["ff", "-o", domain_file, "-f", problem_file]
        cmd += list(self.args)
        for opt,val in self.kwargs.items():
            cmd += ["-"+opt, str(val)]
        return cmd

    @staticmethod
    def _process_actions_(actions):
        if not actions:
            return []
        actions_ = actions.lower().split('\n')
        plan = map(lambda a: tuple(a.split(':')[1].split()), actions_)
        return list(plan)

    def _parse_out_(self, out):
        result = dict()
        match_plan = FF_REGEX.search(out)
        match_elapsed = FF_ELAPSED.search(out)
        result['plan-found'] = match_plan is not None
        if match_plan:
            result['plan'] = FFPlanner._process_actions_(match_plan.group('actions'))
            result['total-cost'] = float(match_plan.group('cost'))
        if match_elapsed:
            result['elapsed'] = float(match_elapsed.group('elapsed'))
        return result


FD_REGEX = re.compile(
r"""Solution found!
Actual search time: (?P<elapsed>[0-9\.]+s) \[t=[0-9\.]+s\]
(?P<actions>(?:[ a-z_0-9\-]+ \([0-9]+\)
)+)Plan length: [0-9]+ step\(s\)\.
Plan cost: (?P<cost>[0-9]+)""")

class FDPlanner(CmdPlanner):

    SUPPORTS_TIMEOUT = True

    def get_cmd(self, domain_file, problem_file):
        cmd = ["fast-downward.py", domain_file, problem_file]
        parameters = self.parameters
        heuristic = parameters.get("h", "add")
        assert heuristic in ("hmax", "add", "ff", "cea", "cg", "lmcut", "lmcount", "ipdbs")
        timeout = self.parameters.get("timeout", None)
        if timeout:
            cmd += ["--search", "astar({}(), max_time={})".format(heuristic)]
            pass
        else:
            cmd += ["--search", "astar({}())".format(heuristic, timeout)]
        return cmd

    @staticmethod
    def _process_actions_(actions):
        splitted = actions.split("\n")[:-1]
        plan = list(map(lambda s: tuple(s.split())[:-1], splitted))
        return plan

    def _parse_out_(self, out):
        match = FD_REGEX.search(out)
        result = dict()
        result["plan-found"] = match is not None
        if match:
            result["plan"] = FDPlanner._process_actions_(match.group("actions"))
            result["total-cost"] = match.group("cost")
            result["elapsed"] = match.group("elapsed")
        return result

