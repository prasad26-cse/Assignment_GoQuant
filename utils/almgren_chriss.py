import numpy as np

def temporary_impact(volume, alpha, eta):
    """
    Temporary impact function: eta * volume^alpha
    """
    return eta * volume ** alpha

def permanent_impact(volume, beta, gamma):
    """
    Permanent impact function: gamma * volume^beta
    """
    return gamma * volume ** beta

def hamiltonian(inventory, sell_amount, risk_aversion, alpha, beta, gamma, eta, volatility=0.3, time_step=0.5):
    """
    Hamiltonian function (objective to minimize):
    Considers permanent impact, temporary impact, and execution risk.
    """
    temp_impact = risk_aversion * sell_amount * permanent_impact(sell_amount / time_step, beta, gamma)
    perm_impact = risk_aversion * (inventory - sell_amount) * time_step * temporary_impact(sell_amount / time_step, alpha, eta)
    exec_risk = 0.5 * (risk_aversion ** 2) * (volatility ** 2) * time_step * ((inventory - sell_amount) ** 2)
    return temp_impact + perm_impact + exec_risk

def optimal_execution(time_steps, total_shares, risk_aversion, alpha, beta, gamma, eta, volatility=0.3):
    """
    Computes the optimal trading trajectory using dynamic programming based on the Almgren-Chriss model.

    Parameters:
    - time_steps: Number of time intervals
    - total_shares: Total number of shares to be liquidated
    - risk_aversion: Risk aversion parameter
    - alpha, beta: Exponents for temporary and permanent market impact
    - gamma, eta: Coefficients for permanent and temporary market impact
    - volatility: Market volatility

    Returns:
    - value_function: Cost matrix
    - best_moves: Best action at each state
    - inventory_path: Remaining shares over time
    - optimal_trajectory: Optimal share sell sequence
    """

    value_function = np.zeros((time_steps, total_shares + 1), dtype="float64")
    best_moves = np.zeros((time_steps, total_shares + 1), dtype="int")
    inventory_path = np.zeros((time_steps, 1), dtype="int")
    inventory_path[0] = total_shares
    optimal_trajectory = []
    time_step_size = 0.5

    # Helper to safely compute exp with clipping to avoid overflow
    def safe_exp(x):
        # Clip values between -700 and 700 to avoid overflow in numpy.exp
        return np.exp(np.clip(x, -700, 700))

    # Terminal condition
    for shares in range(total_shares + 1):
        val = shares * temporary_impact(shares / time_step_size, alpha, eta)
        value_function[time_steps - 1, shares] = safe_exp(val)
        best_moves[time_steps - 1, shares] = shares

    # Backward induction
    for t in range(time_steps - 2, -1, -1):
        for shares in range(total_shares + 1):
            best_value = value_function[t + 1, 0] * safe_exp(
                hamiltonian(shares, shares, risk_aversion, alpha, beta, gamma, eta, volatility, time_step_size)
            )
            best_share_amount = shares
            for n in range(shares):
                current_value = value_function[t + 1, shares - n] * safe_exp(
                    hamiltonian(shares, n, risk_aversion, alpha, beta, gamma, eta, volatility, time_step_size)
                )
                if current_value < best_value:
                    best_value = current_value
                    best_share_amount = n
            value_function[t, shares] = best_value
            best_moves[t, shares] = best_share_amount

    # Optimal trajectory
    for t in range(1, time_steps):
        inventory_path[t] = inventory_path[t - 1] - best_moves[t, inventory_path[t - 1]]
        optimal_trajectory.append(best_moves[t, inventory_path[t - 1]])

    optimal_trajectory = np.asarray(optimal_trajectory)

    return value_function, best_moves, inventory_path, optimal_trajectory
