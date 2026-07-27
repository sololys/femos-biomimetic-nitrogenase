import numpy as np

class AIEKF:
    """Adaptive Innovation-based EKF (Track B Core)"""
    def __init__(self, x_init):
        self.x_hat = x_init
        self.P = np.eye(2) * 0.1
        self.Q_base = np.eye(2) * 0.01
        self.R = np.array([[0.05]])
        self.H = np.eye(2)

    def update(self, y_meas, v_k):
        """Conditional update based on ECMG validity bit v_k"""
        e_k = y_meas - (self.H @ self.x_hat)
        
        # Adaptive Scaling
        alpha_k = max(1.0, np.trace(e_k @ e_k.T - self.R) / (np.trace(self.H @ self.P @ self.H.T) + 1e-9))
        
        # Kalman Gain modulated by v_k
        S = self.H @ self.P @ self.H.T + self.R
        K = v_k * (self.P @ self.H.T @ np.linalg.inv(S))
        
        self.x_hat = self.x_hat + K @ e_k
        self.P = (np.eye(2) - K @ self.H) @ self.P
        return self.x_hat, self.P, alpha_k
