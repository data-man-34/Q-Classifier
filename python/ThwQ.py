#!/usr/bin/env python
# This code uses the trained parameters of the Q-Classifier to predict the threshold for the test input data. 
# -- by Harsh Shrivastava, XRCI, IIT Kharagpur
import ImpactQ, sys, os, pickle
import numpy as np

def my_sigmoid(x):
    return 1.0/ (1 + np.exp(-x))

# the major and minor classes... Important to allocate them correctly as selection of threshold depends on them !

def threshold(Xnorm, L, rho, sigma, m, n, l, theta, y):
    F, Sigma, inv_Sigma = ImpactQ.Impact(Xnorm, L, rho, sigma, m, n, l)
    F = np.hstack((np.ones((m, 1), float), F)) # adding a column of 1's to F
    H = np.zeros((m, 1), float)
    Ht = np.zeros((m, 1), float) # threshold values for prediction
    
    # Some constants for the grid search 
    THRESH = 100.0 # grid search for threshold
    WEIGHT = 300.0 # WEIGHTed Thresholding values for grid search 
    HIGH = 0.5 # The range of weighted thresholding
    LOW = 0.2
    int_THRESH = int(THRESH)
    int_WEIGHT = int(WEIGHT)
    # Threshold value selection 
    Th = np.zeros((THRESH, WEIGHT), float) # the array of 100 threshold values ranging from 0.01 to 0.99
    count = 0
    for i in range(0, m):
        H[i] = my_sigmoid(F[i, :] * np.matrix(theta).transpose())
        if y[i] == 1:
            count = count + 1

    if count < m-count:
        MINOR = 1
    else :
        MINOR = 0
    
    MAJOR = 1-MINOR

    for t in range(0, int_THRESH):
        for w in range(0, int_WEIGHT):
            wt = (w-1)*(HIGH-LOW)/(WEIGHT-1)+LOW
            th = t/THRESH
            Ht = np.zeros((m, 1), float) # threshold values for prediction
            for i in range(0, m):
                if H[i] >= th:
                    Ht[i] = 1
            X1 = 0.0
            X2 = 0.0
            X3 = 0.0
            X4 = 0.0
            for i in range(0, m):
                if Ht[i] == MINOR and y[i] == MINOR:
                    X1 = X1 + 1
                elif Ht[i] == MINOR and y[i] == MAJOR:
                    X2 = X2 + 1
                elif Ht[i] == MAJOR and y[i] == MINOR:
                    X3 = X3 + 1
                elif Ht[i] == MAJOR and y[i] == MAJOR:
                    X4 = X4 + 1
            # decision criterion is maximizing the minimum of recall and precision
            if X1 + X3 == 0 or X1 + X2 == 0:
                Th[t][w] = 0
            else: 
                val = min(wt*X1/(X1+X3) ,(1-wt)* X1/(X1+X2)) 
                Th[t][w] = val
#    print Th
#    print len(Th)
    for t in range(0, int_THRESH):
        for w in range(0, int_WEIGHT):
            if t == 0 and w == 0:
                tf = t/THRESH
                wf = (w-1)*(HIGH-LOW)/(WEIGHT-1) + LOW
                max_val = Th[t][w]
            elif Th[t][w] > max_val:
                tf = t/THRESH
                wf = (w-1)*(HIGH-LOW)/(WEIGHT-1) + LOW
                max_val = Th[t][w]
    # tf = final threshold value selected

    Ht = np.zeros((m, 1), float) # threshold values for prediction
    for i in range(0, m):
        print('i = %d and H(i) = %f: y(i)=%d'%( i, H[i], y[i]))
        if H[i] >= tf:
            Ht[i] = 1

    misclassified = 0
    X1 = 0.0
    X2 = 0.0
    X3 = 0.0
    X4 = 0.0
    for i in range(0, m):
        if Ht[i] == MINOR and y[i] == MINOR:
            X1 = X1 + 1
        elif Ht[i] == MINOR and y[i] == MAJOR:
            X2 = X2 + 1
        elif Ht[i] == MAJOR and y[i] == MINOR:
            X3 = X3 + 1
        elif Ht[i] == MAJOR and y[i] == MAJOR:
            X4 = X4 + 1
    
    accuracy = float(X1 + X4)/float(X1 + X2 + X3 + X4) * 100.0
    sensitivity = X1/(X1 + X3)
    specificity = X4/(X2 + X4)
    print('The threshold value selected = %f for max ratio = %f and weight = %f\n' %(tf, max_val, wf))
    
    print('The classification table is given below, kindly note that sensitivity and specificity might be interchanged depending on the minor class label\n\n \t y=0 \t y=1 \n H=0\t %d\t%d\n H=1\t%d\t%d\n\n\n Accuracy = %f\nSensitivity = %f\nSpecificity = %f\n'%(X1, X2, X3, X4, accuracy, sensitivity, specificity))
    return tf
if __name__ == "__main__":
    main()

