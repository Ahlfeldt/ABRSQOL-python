from numpy import (
    exp as _np_exp, 
    array as _np_array, 
    ones as _np_ones
  )

def invert_quality_of_life(
  df,
  w = 'w',
  p_H = 'p_H',
  P_t = 'P_t',
  p_n = 'p_n',
  L = 'L',
  L_b = 'L_b',
  alpha:float = 0.7,
  beta:float = 0.5,
  gamma:float = 3,
  xi:float = 5.5,
  conv:float = 0.5,
  tolerance:float = 1e-10,
  maxiter:int = 10000,
)->_np_array:
    """ABRSQOL numerical solution algorithm to invert a quality of life measure

    This toolkit implements a numerical solution algorithm
    to invert a quality of life (QoL) from observed data
    in various programming languages. The QoL measure is
    based on Ahlfeldt, Bald, Roth, Seidel (2024):
    Measuring quality of life under spatial frictions.
    Unlike the traditional Rosen-Roback measure, this measure
    accounts for mobility frictions—generated by idiosyncratic
    tastes and local ties—and trade frictions—generated by
    trade costs and non-tradable services, thereby reducing
    non-classical measurement error. 
    
    Notice that quality of life is identified up to a constant.
    Therefore, the inverted QoL measures measure has a relative
    interpretation only. We normalize the QoL relative to the first
    observation in the data set. It is straightforward to rescale
    the QoL measure to any other location or any other value (such
    as the mean or median in the distribution of QoL across locations).
    When using this programme or the toolkit in your work, please cite the paper.

    Args:
      df (pandas.DataFrame | matrix):
        input data containing variables (refenced by following arguments)
      w (str | int | list):
        wage index variable name(s) or column index(es) (default is 'w')
      p_H (str | int):
        floor_space_price variable name or column index (default is 'p_H')
      P_t (str | int):
        tradable_goods_price variable name or column index (default is 'P_t')
      p_n (str | int):
        local_services_price variable name or column index (default is 'p_n')
      L (str | int | list):
        residence_population variable name(s) or column index(es) (default is 'L')
      L_b (str | int | list):
        hometown_population variable name(s) or column index(es) (default is 'L_b')
      alpha (float):
        Income share on non-housing consumtpion (default is 0.7)
      beta (float):
        Share of tradable goods in non-housing consumption (default is 0.5)
      gamma (float):
        Idiosyncratic taste dispersion (inverse labour supply elasticity) (default is 3)
      xi (float):
        Valuation of local ties (default is 5)
      conv (float):
        Convergence parameter (Hgher value increases spead of, convergence and risk of bouncing) (default is 0.5)
      tolerance (float):
        Value used in stopping rule (The mean absolute error (MAE). Smaller values imply greater precision and longer convergence) (default is 1e-10)
      maxiter (int):
        Maximum number of iterations after which the algorithm is forced to stop (default is 10000)
    
    Returns:
      vector (numpy.array): 
        inverted quality of life measure (identified up to a constant). Shape=(n,1)
    """
    # Extract key variables from input dataframe/matrix
    # shape is JxTheta:
    L_b = df[[L_b] if type(L_b) not in [list, _np_array] else L_b].values
    L = df[[L] if type(L) not in [list, _np_array] else L].values
    w = df[[w] if type(w) not in [list, _np_array] else w].values
    # shape is Jx1:
    P_t = df[[P_t]].values
    p_H = df[[p_H]].values
    p_n = df[[p_n]].values
    

    # if there are unequal number of rows (n_obs) among variables throw error
    if len(set([len(L_b),len(L),len(w),len(P_t),len(p_H),len(p_n)])) != 1:
        raise ValueError("\nDimension mismatch: variables do not have the same length:",
        "\nL_b: ",len(L_b), "\nL: ",len(L),"\nw: ",len(w),
        "\nP_t: ",len(P_t),"\np_H: ",len(p_H),"\np_n: ",len(p_n))
    
    # else save units of observation as J
    J = len(L_b)

    # if there are unequal number of dimensions throw an error
    if len(set([L_b.shape[1],L.shape[1],w.shape[1]])) != 1:
        raise ValueError("\nDimension mismatch: variables do not have the same number of columns:",
        "\nL_b: ",L_b.shape[1], "\nL: ",L.shape[1],"\nw:", w.shape[1])
    
    # else assign theta as the number of dimensions (mostly will be 1)
    Theta = L_b.shape[1]


    ## Inversion
    
    # Adjust L_b to have same sum as L
    L_bar = L.sum(axis=0) # total number of workers in dataset
    L_b_adjust = L_bar / L_b.sum(axis=0)
    L_b = L_b * L_b_adjust
    
    # Express all variables in relative differences
    # Calculate relative employment, L_hat
    L_hat = L / L[0]
    # Calculate relative wages, w_hat
    w_hat = w / w[0]
    # Calculate relative price levels
    P_t_hat = P_t / P_t[0]
    p_H_hat = p_H / p_H[0]
    p_n_hat = p_n / p_n[0]

    # Calculate aggregate price level
    P_hat = (P_t_hat **(alpha * beta)) * (p_n_hat **(alpha *(1-beta)))  * (p_H_hat **(1-alpha))
    P     = (P_t     **(alpha * beta)) * (p_n     **(alpha *(1-beta)))  * (p_H     **(1-alpha))

    # Relative Quality of life (A_hat)
    # Guess values relative QoL
    A_hat = _np_ones(shape=(J, Theta)) # First guess: all locations have the same QoL
    A = A_hat
    
    O_vector_total = list() # list to track convergence
    O_total = 100000 # Starting value for loop  
    count = 1 # Counts the number of iterations

    print("\nBegin loop to solve for quality of life measure:\n")
    while (O_total > tolerance) and (count <= maxiter):
        print("Itertion "+str(count)+"/"+str(maxiter)+
            ", value of objective function: "+str(O_total)+" > "+str(tolerance), end="\r")

        # (1) Calculate model-consistent aggregation shares, Psi_b
        nom = (A * w / P) **(gamma)
        Psi_b = ((_np_exp(xi) - 1) * nom / nom.sum(axis=0) + 1)**-1

        # (2) Calculate mathcal_L
        mathcal_L = ((L_b * Psi_b).sum(axis=0) + (L_b *Psi_b *(_np_exp(xi) - 1)))
        
        # (3) Calculate relative mathcal_L
        mathcal_L_hat = mathcal_L/mathcal_L[0]

        # (4) Calculate relative QoL, A_hat, according to equation (17)
        A_hat_up = P_hat * (1 / w_hat) * (L_hat / mathcal_L_hat) **(1 /gamma)

        # (5) Calculate deviations from inital guesses for QoL levels
        # print('A_hat_up-A_hat',A_hat_up.shape,A_hat.shape, A_hat_up,A_hat)
        O_total = abs(A_hat_up-A_hat).sum()/J
        O_vector_total.append(O_total)

        # Update QoL levels for next iteration of loop
        A_hat = conv * A_hat_up + (1-conv) * A_hat
        A = A_hat

        # Next iteration
        count += 1
    #
    print("\nQuality of life measure generated and returned as vector.")
    # return simple vector / array of shape=(J,)
    return(A[:,0])


