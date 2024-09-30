import numpy as np
from rocket_optimizer.costfunction import costfunction


def neadmead(simplex, price_values, j, tol=1e-6, max_iter=20):
    """
    Nelder-Mead optimization algorithm starting from a given simplex and function values.

    Parameters:
    - simplex: Nx(N+1) numpy array representing the initial simplex (N dimensions and N+1 vertices).
    - price_values: (N+1)-dimensional numpy array containing function values at each simplex vertex.
    - tol: Tolerance for termination.
    - max_iter: Maximum number of iterations.

    Imports:
    - price_per_payload: The objective function to minimize (R^N -> R).

    Returns:
    - sigma_best: The estimated minimizer (best point in the final simplex).
    - price_best: The minimum function value.
    """
    N = simplex.shape[0]  # Dimension of the problem
    alpha, gamma, beta, rho = 1, 2, 0.5, 0.5  # Reflection, expansion, contraction, shrink coefficients

    iteration = 0
    while iteration < max_iter:
        # Sort simplex based on function values
        # print(price_values)
        indices = np.argsort(price_values)
        print("price_values: ", price_values)
        print("indices: ", indices)
        # indices = price_values
        simplex = simplex[:, indices]
        price_values = np.array(price_values)
        price_values = price_values[indices]

        sigma_centroid = np.mean(simplex[:, :-1], axis=0)
        print("sigma_centroid: ", sigma_centroid)

        # Reflection
        sigma_reflect = sigma_centroid + alpha * (sigma_centroid - simplex[:, -1])
        print("sigma_reflect: ", sigma_reflect)
        price_reflect = costfunction(sigma_reflect, j)

        if price_values[0] <= price_reflect < price_values[-2]:
            simplex[:, -1] = sigma_reflect
            price_values[-1] = price_reflect
        elif price_reflect < price_values[0]:
            # Expansion
            sigma_expand = sigma_centroid + gamma * (sigma_reflect - sigma_centroid)
            price_expand = costfunction(sigma_expand, j)
            if price_expand < price_reflect:
                simplex[:, -1] = sigma_expand
                price_values[-1] = price_expand
            else:
                simplex[:, -1] = sigma_reflect
                price_values[-1] = price_reflect
        else:
            # Contraction
            if price_reflect < price_values[-1]:
                # Outside contraction (towards the reflected point)
                sigma_contract = sigma_centroid + beta * (sigma_reflect - sigma_centroid)
            else:
                # Inside contraction (towards the centroid)
                sigma_contract = sigma_centroid + beta * (simplex[:, -1] - sigma_centroid)

            price_contract = costfunction(sigma_contract, j)

            if price_contract < min(price_reflect, price_values[-1]):
                simplex[:, -1] = sigma_contract
                price_values[-1] = price_contract
            else:
                # Shrink the simplex towards the best point
                for i in range(1, N+1):
                    simplex[:, i] = simplex[:, 0] + rho * (simplex[:, i] - simplex[:, 0])
                    price_values[i] = costfunction(simplex[:, i], j)

        # Check for convergence (standard deviation of function values)
        if np.std(price_values) < tol:
            break

        iteration += 1

    # Best point in the simplex
    sigma_best = simplex[:, 0]
    price_best = price_values[0]

    print(f"'Converged' after {iteration} iterations.")
    print(f"Best point: {sigma_best}")
    print(f"Minimum function value: {price_best}")

    return sigma_best, price_best
