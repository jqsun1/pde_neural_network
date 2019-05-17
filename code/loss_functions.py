import tensorflow as tf
import analytic_functions


# Old Derivatives

def first_order_central_finite_difference(tf_fx_delta_plus, tf_fx_delta_minus, delta):
    derivative = tf.subtract(tf_fx_delta_plus, tf_fx_delta_minus) / (2 * delta)

    return derivative


def second_order_central_finite_difference(tf_fx, tf_fx_delta_plus, tf_fx_delta_minus, delta):
    tf_fx = tf.Print(tf_fx, [tf_fx, tf_fx_delta_plus, tf_fx_delta_minus], "\nf(y) f(y+h) f(y-h): ")
    second_derivative = tf.add(tf.subtract(tf_fx_delta_plus, 2 * tf_fx), tf_fx_delta_minus) / (delta ** 2)

    return second_derivative


# New Integrals

def R1_integral(x2, tf_fx_x_plus, tf_fx_x_minus, delta_y):
    R1 = 2 * delta_y * tf.multiply(x2, tf.subtract(tf_fx_x_plus, tf_fx_x_minus))
    #R1 = tf.Print(R1, [tf.shape(x2), tf.shape(tf_fx_x_plus), tf.shape(tf_fx_x_minus)], message="shapes in R1")

    return R1

def R2_integral(x2, x2_delta_plus, x2_delta_minus, tf_fx, tf_fx_y_plus, tf_fx_y_minus, delta_x, delta_y):
    
    s1 = (2 * delta_x)*tf.subtract(tf.multiply(tf_fx_y_plus, x2_delta_plus), tf.multiply(tf_fx_y_minus, x2_delta_minus))
    s2 = 4*tf_fx * delta_x * delta_y
    
    R2 = tf.subtract(s1, s2)
    
    return R2

def R3_integral(x1, tf_fx_y_plus, tf_fx_y_minus, delta_x):
    R3 = 2 * delta_x * tf.multiply(x1, tf.subtract(tf_fx_y_plus, tf_fx_y_minus))
    
    return R3

def R4_integral(tf_fx_y_plus, tf_fx_y_minus, delta_x, delta_y):
    R4 = (delta_x/ delta_y) * tf.pow(tf.subtract(tf_fx_y_plus, tf_fx_y_minus), 2)
    
    return R4

def R5_integral(tf_fx, tf_fx_y_plus, tf_fx_y_minus, delta_x, delta_y):
    R5 = (2*delta_x/ delta_y) * tf.subtract(tf.add(tf_fx_y_plus, tf_fx_y_minus), 2*tf_fx)
    
    return R5



def squared_residual_function_wrapper2(k, c, D, deltas, num_feval, sigma_x, sigma_y):
    def squared_residual_function2(X, y_pred, y_real):
        num_output = tf.constant(1)
        num_features = tf.constant(2)

        shape_x = tf.shape(X)

        delta_x = deltas[0]
        delta_y = deltas[1]

        batch_size = tf.cast(shape_x[0] / num_feval, tf.int32)

        # Reset the tensor to 0,0 for every new batch
        begin_x = tf.get_variable("begin_x", initializer=[0, 0], dtype=tf.int32)
        begin_y = tf.get_variable("begin_y", initializer=[0, 0], dtype=tf.int32)
        begin_x = tf.assign(begin_x, [0, 0])
        begin_y = tf.assign(begin_y, [0, 0])
        multiplier_begin = tf.constant([1, 0])
        size_y = tf.stack([batch_size, num_output])
        size_x = tf.stack([batch_size, num_features])
        offset_increment_x = tf.multiply(size_x, multiplier_begin)
        offset_increment_y = tf.multiply(size_y, multiplier_begin)

        # Retrieve original points and predictions
        X_original = tf.slice(X, begin_x, size_x)
        y_pred_original = tf.slice(y_pred, begin_y, size_y)
        y_real_original = tf.slice(y_real, begin_y, size_y)

        #Retrieve original y
        y_original = tf.slice(y_real, begin_y, size_y)

        len_original = tf.shape(X_original[:,0])
        x1 = tf.slice(X_original, [0, 0], tf.stack([batch_size, 1]))
        x2 = tf.slice(X_original, [0, 1], tf.stack([batch_size, 1]))

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta1_plus = tf.slice(X, begin_x, size_x)
        y_pred_delta1_plus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta1_plus = tf.slice(y_real, begin_y, size_y)

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta1_minus = tf.slice(X, begin_x, size_x)
        y_pred_delta1_minus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta1_minus = tf.slice(y_real, begin_y, size_y)

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta2_plus = tf.slice(X, begin_x, size_x)
        y_pred_delta2_plus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta2_plus = tf.slice(y_real, begin_y, size_y)

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta2_minus = tf.slice(X, begin_x, size_x)
        y_pred_delta2_minus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta2_minus = tf.slice(y_real, begin_y, size_y)

        # compute the approximate derivatives (tensors) given y_pred
        nn_partial1_x = first_order_central_finite_difference(y_pred_delta1_plus, y_pred_delta1_minus, delta_x)
        nn_partial1_y = first_order_central_finite_difference(y_pred_delta2_plus, y_pred_delta2_minus, delta_y)
        nn_partial2_y = second_order_central_finite_difference(y_pred_original, y_pred_delta2_plus, y_pred_delta2_minus,
                                                               delta_y)

        # Compute real derivatives
        analytic_derivatives = analytic_functions.real_derivatives_tf(X_original, sigma_x, sigma_y)
        nn_partial1_x_real = analytic_derivatives[0]
        nn_partial1_y_real = analytic_derivatives[1]
        nn_partial2_y_real = analytic_derivatives[2]

        nn_partial1_x = tf.Print(nn_partial1_x, [nn_partial1_x_real, nn_partial1_y_real, nn_partial2_y_real], message="\nReal derivatives: ")
        nn_partial1_x = tf.Print(nn_partial1_x, [nn_partial1_x, nn_partial1_y, nn_partial2_y], message="\nAppr derivatives: ")

        r1 = tf.multiply(x2, nn_partial1_x)
        r2 = tf.multiply(c * x2, nn_partial1_y)
        r3 = tf.multiply(k * x1, nn_partial1_y)
        r4 = D * tf.subtract(tf.pow(nn_partial1_y, 2), nn_partial2_y)

        r_total = r1 + c - r2 - r3 + r4

        r = tf.reduce_sum(tf.pow(r_total, 2)) / (2 * tf.cast(batch_size, tf.float32))

        # e (compared with real phi)
        e = tf.reduce_sum(tf.pow(tf.subtract(y_original, y_pred_original), 2)) / (2 * tf.cast(batch_size, tf.float32))

        # R (integral)

        x2_plus = tf.slice(X_delta2_plus, [0,1], tf.stack([batch_size, 1]))
        x2_minus = tf.slice(X_delta2_minus, [0,1], tf.stack([batch_size, 1]))

        R1 = R1_integral(x2, y_pred_delta1_plus, y_pred_delta1_minus, delta_y)
        R2 = R2_integral(x2, x2_plus, x2_minus, y_pred_original, y_pred_delta2_plus,
                         y_pred_delta2_minus, delta_x, delta_y)
        R3 = R3_integral(x1, y_pred_delta2_plus, y_pred_delta2_minus, delta_x)
        R4 = R4_integral(y_pred_delta2_plus, y_pred_delta2_minus, delta_x, delta_y)
        R5 = R5_integral(y_pred_original, y_pred_delta2_plus, y_pred_delta2_minus, delta_x, delta_y)
        #tf.reshape(R1, tf.transpose(tf.shape(x2)))
        
        # R (integral)
        RR1 = R1_integral(x2, y_real_delta1_plus, y_real_delta1_minus, delta_y)
        RR2 = R2_integral(x2, x2_plus, x2_minus, y_real_original, y_real_delta2_plus, y_real_delta2_minus, delta_x, delta_y)
        RR3 = R3_integral(x1, y_real_delta2_plus, y_real_delta2_minus, delta_x)
        RR4 = R4_integral(y_real_delta2_plus, y_real_delta2_minus, delta_x, delta_y)
        RR5 = R5_integral(y_real_original, y_real_delta2_plus, y_real_delta2_minus, delta_x, delta_y)


        R_total = R1 + c*delta_x*delta_y - c*R2 - k*R3 + D*tf.subtract(R4, R5)
        RR_total = RR1 + c*delta_x*delta_y - c*RR2 - k*RR3 + D*tf.subtract(RR4, RR5)
        
        
        #R = tf.reduce_sum(tf.pow(R_total, 2)) / (2 * tf.cast(batch_size, tf.float32))
        #RR = tf.reduce_sum(tf.pow(RR_total, 2)) / (2 * tf.cast(batch_size, tf.float32))

        R = tf.reduce_sum(tf.pow(R_total, 2)) / (2 * tf.cast(batch_size, tf.float32))
        RR = tf.reduce_sum(tf.pow(RR_total, 2)) / (2 * tf.cast(batch_size, tf.float32))

        R = tf.Print(R, [R_total, R], message="Predicted integrals")
        R = tf.Print(R, [RR_total, RR], message="Real integrals")
    
        return R, e

    return squared_residual_function2


def squared_residual_function_wrapper(k, c, D, deltas, num_feval):

    def squared_residual_function2(X, y_pred):
        num_output = tf.constant(1)
        num_features = tf.constant(2)

        shape_x = tf.shape(X)

        delta_x = deltas[0]
        delta_y = deltas[1]

        batch_size = tf.cast(shape_x[0]/num_feval, tf.int32)

        # Reset the tensor to 0,0 for every new batch
        begin = tf.get_variable("begin", initializer=[0, 0], dtype=tf.int32)
        begin = tf.assign(begin, [0, 0])
        multiplier_begin = tf.constant([1, 0])
        size = tf.stack([batch_size, num_output])
        size_x = tf.stack([batch_size, num_features])
        offset_increment = tf.multiply(size, multiplier_begin)

        #Retrieve original points and predictions
        X_original = tf.slice(X, begin, size_x)
        y_pred_original = tf.slice(y_pred, begin, size)
        x1 = X_original[:, 0]
        x2 = X_original[:, 1]

        begin = tf.add(begin, offset_increment)
        y_pred_delta1_plus = tf.slice(y_pred, begin, size)

        begin = tf.add(begin, offset_increment)
        y_pred_delta1_minus = tf.slice(y_pred, begin, size)

        begin = tf.add(begin, offset_increment)
        y_pred_delta2_plus = tf.slice(y_pred, begin, size)

        begin = tf.add(begin, offset_increment)
        y_pred_delta2_minus = tf.slice(y_pred, begin, size)

        # compute the tensors given y_pred
        nn_partial1_x = first_order_central_finite_difference(y_pred_delta1_plus, y_pred_delta1_minus, delta_x)
        nn_partial1_y = first_order_central_finite_difference(y_pred_delta2_plus, y_pred_delta2_minus, delta_y)
        nn_partial2_y = second_order_central_finite_difference(y_pred_original, y_pred_delta2_plus, y_pred_delta2_minus,
                                                               delta_y)

        r1 = tf.multiply(x2, nn_partial1_x)
        r2 = tf.multiply(c * x2, nn_partial1_y)
        r3 = tf.multiply(k * x1, nn_partial1_y)
        r4 = D * tf.subtract(tf.pow(nn_partial1_y, 2), nn_partial2_y)

        r_total = r1 + c - r2 - r3 + r4

        r = tf.reduce_sum(tf.pow(r_total, 2))/(2*tf.cast(batch_size, tf.float32))

        return r

    return squared_residual_function2


def squared_residual_function(X, y_pred, deltas, k, c, D, batch_size):
    num_output = tf.constant(1)
    num_features = tf.constant(2)

    delta_x = deltas[0]
    delta_y = deltas[1]

    # Reset the tensor to 0,0 for every new batch
    begin = tf.get_variable("begin", initializer=[0, 0], dtype=tf.int32)
    begin = tf.assign(begin, [0, 0])
    multiplier_begin = tf.constant([1, 0])
    size = tf.stack([batch_size, num_output])
    size_x = tf.stack([batch_size, num_features])
    offset_increment = tf.multiply(size, multiplier_begin)

    #Retrieve original points and predictions
    X_original = tf.slice(X, begin, size_x)
    y_pred_original = tf.slice(y_pred, begin, size)
    x1 = X_original[:, 0]
    x2 = X_original[:, 1]

    begin = tf.add(begin, offset_increment)
    y_pred_delta1_plus = tf.slice(y_pred, begin, size)

    begin = tf.add(begin, offset_increment)
    y_pred_delta1_minus = tf.slice(y_pred, begin, size)

    begin = tf.add(begin, offset_increment)
    y_pred_delta2_plus = tf.slice(y_pred, begin, size)

    begin = tf.add(begin, offset_increment)
    y_pred_delta2_minus = tf.slice(y_pred, begin, size)

    # compute the tensors given y_pred
    nn_partial1_x = first_order_central_finite_difference(y_pred_delta1_plus, y_pred_delta1_minus, delta_x)
    nn_partial1_y = first_order_central_finite_difference(y_pred_delta2_plus, y_pred_delta2_minus, delta_y)
    nn_partial2_y = second_order_central_finite_difference(y_pred_original, y_pred_delta2_plus, y_pred_delta2_minus,
                                                           delta_y)

    r1 = tf.multiply(x2, nn_partial1_x)
    r2 = tf.multiply(tf.multiply(c, x2), nn_partial1_y)
    r3 = tf.multiply(tf.multiply(k, x1), nn_partial1_y)
    r4 = tf.multiply(D, tf.subtract(tf.pow(nn_partial1_y, 2), nn_partial2_y))

    r_total = r1 + c - r2 - r3 + r4

    r = tf.reduce_sum(tf.pow(r_total, 2))/(2*tf.cast(batch_size, tf.float32))

    return r

def linear_residual_function_wrapper(num_inputs, num_outputs, deltas, num_feval, num_conditions, alpha=1):
    def linear_residual_function(X, y_pred, y_real):

        num_output = tf.constant(num_outputs)
        num_features = tf.constant(num_inputs)

        delta_x = deltas[0]
        shape_x = tf.shape(X)

        batch_size = tf.cast(shape_x[0] / num_feval, tf.int32)

        # Reset the tensor to 0,0 for every new batch
        begin_x = tf.get_variable("begin_x", initializer=[0, 0], dtype=tf.int32)
        begin_y = tf.get_variable("begin_y", initializer=[0, 0], dtype=tf.int32)
        begin_x = tf.assign(begin_x, [0, 0])
        begin_y = tf.assign(begin_y, [0, 0])
        multiplier_begin = tf.constant([1, 0])
        size_y = tf.stack([batch_size, num_output])
        size_x = tf.stack([batch_size, num_features])
        size_x_initial = tf.stack([num_conditions, num_features])
        size_y_initial = tf.stack([num_conditions, num_output])
        offset_increment_x = tf.multiply(size_x, multiplier_begin)
        offset_increment_y = tf.multiply(size_y, multiplier_begin)

        # Retrieve original points and predictions
        X_original = tf.slice(X, begin_x, size_x)
        y_pred_original = tf.slice(y_pred, begin_y, size_y)
        y_real_original = tf.slice(y_real, begin_y, size_y)

        # Retrieve original y
        y_original = tf.slice(y_real, begin_y, size_y)

        len_original = tf.shape(X_original[:, 0])
        x1 = tf.slice(X_original, [0, 0], tf.stack([batch_size, 1]))
        #x2 = tf.slice(X_original, [0, 1], tf.stack([batch_size, 1]))

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta1_plus = tf.slice(X, begin_x, size_x)
        y_pred_delta1_plus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta1_plus = tf.slice(y_real, begin_y, size_y)

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_delta1_minus = tf.slice(X, begin_x, size_x)
        y_pred_delta1_minus = tf.slice(y_pred, begin_y, size_y)
        y_real_delta1_minus = tf.slice(y_real, begin_y, size_y)
        
        begin_x = tf.Print(begin_x, [begin_x, begin_y, size_x_initial, size_y_initial], message='bx, by, sxi, syi')

        begin_x = tf.add(begin_x, offset_increment_x)
        begin_y = tf.add(begin_y, offset_increment_y)
        X_initial = tf.slice(X, begin_x, size_x_initial)
        y_real_initial = tf.slice(y_real, begin_y, size_y_initial)
        y_pred_initial = tf.slice(y_pred, begin_y, size_y_initial)

        #r_total = y_pred_delta1_plus*(1 - delta_x/2) - y_pred_original*(1 + delta_x/2)
        r_total = first_order_central_finite_difference(y_pred_delta1_plus, y_pred_delta1_minus, delta_x) + y_pred_original - tf.ones(tf.shape(y_pred_original), dtype=tf.float32, name=None)
        
        r_total = tf.Print(r_total, [X_initial,y_real_initial, y_pred_initial], message='x_init, y_init_r, y_init_p')

        e1 = tf.reduce_sum(tf.pow(r_total, 2))/(2*tf.cast(batch_size, tf.float32))                                               
        e2 = tf.reduce_sum(tf.pow(tf.subtract(y_pred_initial, y_real_initial), 2))
        
        e = tf.reduce_sum(tf.pow(tf.subtract(y_original, y_pred_original), 2)) / (2 * tf.cast(batch_size, tf.float32))
                                                                                   
        r = e1 + alpha*e2
        
        
        d1 = first_order_central_finite_difference(y_pred_delta1_plus, y_pred_delta1_minus, delta_x)
        ic = tf.multiply(y_real_initial, tf.ones(tf.shape(y_pred_original)))
        d1 = tf.Print(d1, [tf.shape(X_original), tf.shape(d1)])
        
        
        r_total2 = tf.multiply(X_original, d1)  + y_pred_original + ic +  tf.multiply(X_original, y_pred_original) - tf.ones(tf.shape(y_pred_original), dtype=tf.float32, name=None)
        r2 = tf.reduce_sum(tf.pow(r_total2, 2))/(2*tf.cast(batch_size, tf.float32))   

        
        # expamles
        
        # our r
        #1
        try1_total = d1 + (X_original + (1 + 3 * tf.pow(X_original, 2))/(1 + X_original + tf.pow(X_original, 3))) * y_pred_original - tf.pow(X_original, 3) - 2 * X_original - tf.pow(X_original, 2) * (1 + 3 * tf.pow(X_original, 2))/(1 + X_original + tf.pow(X_original, 3))
        try1 = tf.reduce_sum(tf.pow(try1_total, 2))/(2*tf.cast(batch_size, tf.float32))+ alpha*e2
        
        #2
        try2_total = d1 + y_pred_original/5 - tf.exp(-X_original/5) * tf.cos(X_original)
        try2 = tf.reduce_sum(tf.pow(try2_total, 2))/(2*tf.cast(batch_size, tf.float32))+ alpha*e2
        
#         d2 = second_order_central_finite_difference(y_pred_original, y_pred_delta1_plus, y_pred_delta1_minus, delta_x)
#         try3_total = d2 + d1/5 + y_pred_original + tf.exp(-X_original/5) * tf.cos(X_original)/5
        
        # paper's r
        try1_ex_total = y_pred_original + X_original * d1 - (- (ic + tf.multiply(X_original, y_pred_original)) * (X_original + (1 + 3 * tf.pow(X_original, 2))/(1 + X_original + tf.pow(X_original, 3))) + tf.pow(X_original, 3) + 2 * X_original + tf.pow(X_original, 2) * (1 + 3 * tf.pow(X_original, 2))/(1 + X_original + tf.pow(X_original, 3)))
        try1_ex = tf.reduce_sum(tf.pow(try1_ex_total, 2))/(2*tf.cast(batch_size, tf.float32))
        
        try2_ex_total = y_pred_original + X_original * d1 - (- tf.multiply(X_original, y_pred_original)/5 + tf.exp(-X_original/5) * tf.cos(X_original))
        try2_ex = tf.reduce_sum(tf.pow(try2_ex_total, 2))/(2*tf.cast(batch_size, tf.float32))
        
        return try1, e

    return linear_residual_function
