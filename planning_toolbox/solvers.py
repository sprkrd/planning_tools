import re
import subprocess

from .pddl_utility import PddlDomainFile
from .pddl_utility import PddlProblemFile
from .pddl_utility import success_probability


class CmdPlanner:

    SUPPORTS_TIMEOUT = False

    def __init__(self, parameters={}, round_costs=0):
        self.parameters = parameters
        self.round_costs = round_costs

    def get_cmd(self, domain_file, problem_file):
        raise NotImplementedError()

    def _parse_out_(self, out):
        raise NotImplementedError()

    def _supports_timeout_(self):
        return self.SUPPORTS_TIMEOUT

    def run_planner(self, domain_file, problem_file):
        cmd = self.get_cmd(domain_file, problem_file)
        parameters = self.parameters
        timeout = None if self._supports_timeout_() else parameters.get('timeout', None)
        try:
            out = subprocess.check_output(cmd, timeout=timeout)
            out = out.decode('ascii')
            result = self._parse_out_(out)
            if 'timeout' not in result:
                result['timeout'] = False
            result['out'] = out
        except subprocess.TimeoutExpired:
            result = {
                    'plan-found': False,
                    'timeout': True,
                    'elapsed': timeout,
            }
        except subprocess.CalledProcessError as e:
            result = {
                    'plan-found': False,
                    'out': e.output.decode('ascii')
            }
        return result

    def __call__(self, domain, problem, stch_dom=None):
        with PddlDomainFile(domain, self.round_costs) as domain_f:
            with PddlProblemFile(problem) as problem_f:
                result = self.run_planner(domain_f.filename, problem_f.filename)
        if stch_dom and result['plan-found']:
            plan = result['plan']
            result['success-probability'] = success_probability(stch_dom, plan)
        return result


FF_REGEX = re.compile(
r"""ff: found legal plan as follows
step\s*(?P<actions>(?:[0-9]+: [\sA-Z_0-9\-]*)*)
plan cost: (?P<cost>[0-9]+\.[0-9]*)""")

FF_ELAPSED = re.compile(r"(?P<elapsed>[0-9]+\.[0-9]+) seconds total time")

class FFPlanner(CmdPlanner):

    SUPPORTS_TIMEOUT = False

    def get_cmd(self, domain_file, problem_file):
        parameters = self.parameters
        cmd = ['ff', '-o', domain_file, '-f', problem_file]
        if 's' in parameters:
            cmd += ['-s', str(parameters['s'])]
        if 'w' in parameters:
            cmd += ['-w', str(parameters['w'])]
        if parameters.get('C', False):
            cmd.append('-C')
        if 'b' in parameters:
            cmd += ['-b', str(parameters['-b'])]
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


# Solution found!
# Actual search time: 0.000454614s [t=0.00246033s]
# pick-up_o0 b1 b4 (0)
# put-on-block_o0 b1 b1 (11)
# pick-up_o0 b3 b2 (0)
# put-on-block_o0 b3 b3 (11)
# pick-up_o0 b4 b5 (0)
# put-down_o1 b4 (51)
# pick-up-from-table_o0 b2 (0)
# put-on-block_o0 b2 b4 (11)
# Plan length: 8 step(s).
# Plan cost: 84
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

