#!/usr/bin/env python3
import json
import time
import numpy as np
import scipy.linalg as la

class QCS_EMS_Sim:
    """
    AUDIT-GRADE SIMULATOR (NOT CHEMISTRY)
    Formål: teste estimator + interlock gates deterministisk.
    """

    def __init__(self, seed=1, dt=0.01):
        self.rng = np.random.default_rng(seed)
        self.dt = float(dt)

        # State: x = [delta, nu, rho11, rho12]^T  (units are mixed -> treat as abstract)
        self.x_true = np.array([[0.45],
                                [2020.0],
                                [0.90],
                                [0.05]], dtype=float)

        self.x_est = self.x_true.copy()

        self.A = np.array([
            [-0.01,  0.00,  0.05, 0.00],
            [ 0.00, -0.05,  0.00, 0.10],
            [-0.10,  0.00, -0.02, 0.00],
            [ 0.00, -0.01,  0.00, -0.08]
        ], dtype=float)

        self.B = np.array([
            [-0.05,  0.00],
            [-10.0, -5.00],
            [ 0.00,  0.10],
            [ 0.00,  0.20]
        ], dtype=float)

        self.G = np.eye(4) * 0.02

        self.C = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=float)

        # Discretize (Euler)
        self.F = np.eye(4) + self.A * self.dt
        self.Bd = self.B * self.dt
        self.Gd = self.G * self.dt

        # Cost (LQR) - used as stabilizing feedback (NOT H∞)
        Q = np.diag([100, 10, 500, 500]).astype(float)
        R = np.diag([1, 1]).astype(float)
        P = la.solve_discrete_are(self.F, self.Bd, Q, R)
        self.K = la.inv(R) @ self.Bd.T @ P

        # KF
        self.P = np.eye(4) * 1.0
        self.Qk = np.eye(4) * 0.001
        self.Rk = np.eye(2) * 0.05

        # Targets (abstract “nullpoint”)
        self.x_target = np.array([[0.40], [1944.0], [1.00], [0.00]], dtype=float)

        # Interlock thresholds (sim)
        self.pi_max = 2.5              # trace(P) limit
        self.tol_delta = 0.01          # mm/s (abstract)
        self.tol_nu = 10.0             # cm^-1 (abstract)
        self.u_max = np.array([[5.0],[5.0]])  # control saturation
        self.hold_steps_required = 300 # consecutive steps in-spec

        self.hold_counter = 0

    def _is_finite(self):
        return np.isfinite(self.x_est).all() and np.isfinite(self.P).all()

    def _hard_stop(self, reason, step, extra=None):
        out = {"pass": False, "state": "HARD_STOP", "reason": reason, "step": int(step)}
        if extra: out["extra"] = extra
        return out

    def kf_predict(self, u):
        self.x_est = self.F @ self.x_est + self.Bd @ u
        self.P = self.F @ self.P @ self.F.T + self.Qk

    def kf_update(self, z):
        H = self.C
        y = z - (H @ self.x_est)
        S = H @ self.P @ H.T + self.Rk
        K = self.P @ H.T @ la.inv(S)
        self.x_est = self.x_est + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P

    def step(self, k):
        # Control law (stabilize towards target)
        e = self.x_est - self.x_target
        u = -self.K @ e

        # Optional “-100 mV shift” is NOT physically meaningful here -> keep as a bounded bias
        u[0,0] += 0.10

        # Saturate (fail-closed against runaway)
        u = np.clip(u, -self.u_max, self.u_max)

        # Plant update with noise
        xi = self.rng.normal(0.0, 1.0, size=(4,1))
        self.x_true = self.F @ self.x_true + self.Bd @ u + self.Gd @ xi

        # Measurement
        v = self.rng.normal(0.0, np.sqrt(self.Rk[0,0]), size=(2,1))
        z = self.C @ self.x_true + v

        # KF
        self.kf_predict(u)
        self.kf_update(z)

        # Interlock metrics
        pi = float(np.trace(self.P))
        delta_ok = abs(float(self.x_est[0,0]) - 0.40) <= self.tol_delta
        nu_ok = abs(float(self.x_est[1,0]) - 1944.0) <= self.tol_nu
        spec_ok = delta_ok and nu_ok
        est_ok = (pi <= self.pi_max)

        if not self._is_finite():
            return self._hard_stop("NON_FINITE_STATE", k)

        if pi > self.pi_max:
            return self._hard_stop("ESTIMATOR_DIVERGENCE", k, {"pi": pi})

        # Hold logic (debounce)
        self.hold_counter = self.hold_counter + 1 if spec_ok else 0

        # Build audit log entry
        log = {
            "step": int(k),
            "u": [float(u[0,0]), float(u[1,0])],
            "z": [float(z[0,0]), float(z[1,0])],
            "x_est": [float(self.x_est[i,0]) for i in range(4)],
            "pi": pi,
            "spec_ok": bool(spec_ok),
            "est_ok": bool(est_ok),
            "hold_counter": int(self.hold_counter),
        }

        # Terminal condition
        if est_ok and spec_ok and self.hold_counter >= self.hold_steps_required:
            log["pass"] = True
            log["state"] = "LOCKED_OK"
            return log

        log["pass"] = None
        log["state"] = "RUNNING"
        return log

    def run(self, steps=1500, log_path="audit_log.jsonl", print_every=200):
        with open(log_path, "w", encoding="utf-8") as f:
            for k in range(1, steps+1):
                entry = self.step(k)
                f.write(json.dumps(entry) + "\n")
                if (k % print_every) == 0:
                    xe = entry.get("x_est", [None,None,None,None])
                    print(f"[{k:04d}] delta={xe[0]:.4f} nu={xe[1]:.1f} pi={entry.get('pi',None):.3f} hold={entry.get('hold_counter',0)} state={entry.get('state')}")
                if entry.get("state") in ("HARD_STOP","LOCKED_OK"):
                    return entry
        return {"pass": False, "state": "TIMEOUT"}

if __name__ == "__main__":
    sim = QCS_EMS_Sim(seed=1, dt=0.01)
    result = sim.run(steps=1500, log_path="audit_log.jsonl")
    print(json.dumps(result, indent=2))
