def compute_process_time_exp(theta, alpha):
    return (theta*alpha)/(alpha-1)


def compute_interval_time_exp(t_0, q, y):
    return t_0 + (1-q)*y
