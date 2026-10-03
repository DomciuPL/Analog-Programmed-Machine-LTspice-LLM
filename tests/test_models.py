"""Independent checks of state equations read from SPICE, not SPICE simulation."""
import ast
import math
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = (ROOT / "apm1_lib.txt").read_text(encoding="utf-8")


def spice_expression(expression):
    """Evaluate only the small arithmetic subset used by the tested equations."""
    expression = re.sub(r"V\((\w+),GDN\)", r"v('\1')", expression)
    expression = re.sub(r"\bif\(", "choose(", expression)
    expression = re.sub(r"\bln\(", "log(", expression)
    tree = ast.parse(expression, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Call,
               ast.Name, ast.Load, ast.Constant, ast.Add, ast.Sub, ast.Mult,
               ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Gt, ast.Lt,
               ast.GtE, ast.LtE, ast.Eq)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"Unsupported expression element: {type(node).__name__}")
        if isinstance(node, ast.Call) and (
                not isinstance(node.func, ast.Name) or
                node.func.id not in {"v", "choose", "limit", "log", "exp", "sqrt"}):
            raise ValueError("Unsupported function")
    code = compile(tree, "<SPICE expression subset>", "eval")

    def evaluate(voltages=None, **params):
        scope = {"v": lambda name: voltages[name],
                 "choose": lambda condition, yes, no: yes if condition else no,
                 "limit": lambda value, low, high: max(low, min(value, high)),
                 "log": math.log, "exp": math.exp, "sqrt": math.sqrt, **params}
        return eval(code, {"__builtins__": {}}, scope)
    return evaluate


def current(name):
    match = re.search(rf"^{name}\s+GDN\s+\w+\s+I\s*=\s*\{{(.+)\}}\s*$",
                      LIBRARY, re.M)
    if not match:
        raise ValueError(f"State equation missing: {name}")
    return spice_expression(match[1])


def integrate(function, initial, duration, maxstep=0.0002):
    """Classical RK4 independent of LTspice's integration method."""
    steps = max(1, math.ceil(duration / maxstep))
    step = duration / steps
    state = initial
    for index in range(steps):
        time = index * step
        k1 = function(time, state)
        k2 = function(time + step / 2, state + step * k1 / 2)
        k3 = function(time + step / 2, state + step * k2 / 2)
        k4 = function(time + step, state + step * k3)
        state += step * (k1 + 2*k2 + 2*k3 + k4) / 6
    return state


class StateEquations(unittest.TestCase):
    def test_leak_decays_actual_state(self):
        drive = current("B_INT_DRIVE")
        result = integrate(lambda t, x: drive({"u": 0, "x": x}, SIGN=1, leak=.5), 2, 1)
        self.assertAlmostEqual(result, 2 * math.exp(-.5), places=9)

    def test_integrator_sign_and_hold(self):
        drive = current("B_INT_DRIVE")
        for sign in (-1, 1):
            result = integrate(lambda t, x: drive({"u": 1, "x": x}, SIGN=sign, leak=0), 2, 1)
            self.assertAlmostEqual(result, 2 + sign, places=9)
        self.assertEqual(drive({"u": 0, "x": 3}, SIGN=-1, leak=0), 0)

    def test_limiter_recovers_after_long_overload(self):
        drive = current("B_INTV_DRIVE")
        def rate(input_value):
            return lambda t, x: drive({"u": input_value, "x": x},
                                     SIGN=1, leak=0, L=0, H=1, Taw=.02)
        overloaded = integrate(rate(4), 0, 2)
        self.assertAlmostEqual(overloaded, 1.08, places=8)
        recovered = integrate(rate(-1), overloaded, .5, maxstep=0.00005)
        self.assertAlmostEqual(recovered, .5 + .02*math.log(5), places=7)

    def test_reset_clears_memory_before_integration_resumes(self):
        drive = current("B_RSTINT_DRIVE")
        def rate(reset):
            return lambda t, x: drive({"u": 1, "x": x, "rst": reset},
                                     SIGN=1, leak=0, IC=.25, Tr=.01)
        before = integrate(rate(0), .25, 1)
        reset = integrate(rate(1), before, .3)
        resumed = integrate(rate(0), reset, .7)
        self.assertAlmostEqual(before, 1.25, places=8)
        self.assertAlmostEqual(reset, .25, places=8)
        self.assertAlmostEqual(resumed, .95, places=8)

    def test_schmitt_retains_state_in_hysteresis_band(self):
        drive = current("B_SCHMITT_DRIVE")
        def rate(input_value):
            return lambda t, state: drive({"u": input_value, "state": state},
                                         CEN=0, HYS=.2, Tmem=.001)
        high = integrate(rate(.2), 0, .03)
        held = integrate(rate(0), high, .05)
        cleared = integrate(rate(-.2), held, .03)
        self.assertAlmostEqual(high, 1, places=8)
        self.assertEqual(held, high)
        self.assertAlmostEqual(cleared, 0, places=8)

    def test_mono_reset_has_priority(self):
        drive = current("B_MONO_DRIVE")
        self.assertLess(drive({"r": 1, "s": 1, "state": .75}, Tmem=.001), 0)
        self.assertEqual(drive({"r": 0, "s": 0, "state": .75}, Tmem=.001), 0)

    def test_initial_conditions_exist_for_every_state(self):
        for capacitor, node in (("C_INT_STATE", "x"), ("C_INTV_STATE", "x"),
                                ("C_RSTINT_STATE", "x"), ("C_SCHMITT_STATE", "state"),
                                ("C_MONO_STATE", "state")):
            start = LIBRARY.index(capacitor)
            body = LIBRARY[start:LIBRARY.index(".ends", start)]
            self.assertRegex(body, rf"(?m)^\.ic V\({node}\)=")


class ExampleScaling(unittest.TestCase):
    def test_gee_velocity_and_time_units_match_declared_scales(self):
        text = (ROOT / "examples/APM1_GEE_DEMO.cir").read_text(encoding="utf-8")
        params = {}
        for match in re.finditer(r"^\.param\s+(\w+)\s*=\s*(\{[^}]+\}|[^\s;]+)", text, re.M):
            expression = match[2].strip("{} ")
            params[match[1]] = spice_expression(expression)(**params)
        speed = 3600 * math.hypot(params["Vx_phys"], params["Vy_phys"])
        self.assertAlmostEqual(speed, params["V_kmh"], places=10)
        self.assertAlmostEqual(params["GEE_T_us"] * params["c_km_s"] / 1e6,
                               params["GEE_d_km"], places=10)
        self.assertAlmostEqual(params["x0"] + params["vx_sim"]*params["T_end"],
                               -2.97872774442438, places=10)
        self.assertAlmostEqual(params["y0"] + params["vy_sim"]*params["T_end"],
                               -2.5623118904675914, places=10)


class D12Equation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = (ROOT / "examples/integral_equation_d12.cir").read_text(encoding="utf-8")
        cls.a = float(re.search(r"\bacoef=([\d.]+)", text)[1])
        cls.b = float(re.search(r"\bbcoef=([\d.]+)", text)[1])
        expression = re.search(r"^\.func Phi\(z\) \{(.+)\}$", text, re.M)[1]
        cls.phi = staticmethod(spice_expression(expression))

    def integral(self, y):
        return self.phi(z=y, acoef=self.a, bcoef=self.b)

    def test_separated_integral_matches_implemented_ode(self):
        for y in (.3, .5, .8, .99):
            numerical = (self.integral(y+1e-5)-self.integral(y-1e-5))/(2e-5)
            expected = (1-y)/(y*(1+self.a*y)*(1+self.b*y))
            self.assertAlmostEqual(numerical, expected, places=8)

    def test_boundary_parameter_and_safe_endpoint(self):
        boundary = 1-math.exp(-(self.integral(1)-self.integral(.25)))
        self.assertAlmostEqual(boundary, .4469659268482674, places=12)
        for A in (.3, .2927, .2571, .2563):
            stop = (1-math.exp(-(self.integral(.99)-self.integral(.25))))/A
            rhs = lambda x, y: A*y*(1+self.a*y)*(1+self.b*y)/((1-y)*(1-A*x))
            end = integrate(rhs, .25, stop, maxstep=1e-5)
            self.assertAlmostEqual(end, .99, places=5)
            self.assertGreater(stop, 1)
            self.assertLess(stop, 1/A)


if __name__ == "__main__":
    unittest.main()
