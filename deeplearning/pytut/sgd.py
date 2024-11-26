import numpy as np
import sys

# Initialize parameters
def initialize_params(n_features):
    weights = np.random.randn(n_features) * 0.01
    bias = 0.0
    return weights, bias

def sgd(X, y, learning_rate=0.01, epochs=100):
    weights, bias = initialize_params(X.shape[1])
    n_samples = X.shape[0]

    for epoch in range(epochs):
        for i in range(n_samples):
            # Select one sample
            x_i = X[i]
            y_i = y[i]

            # Predict the output
            prediction = np.dot(x_i, weights) + bias
            #print(f'prediction\n{prediction}')

            # Calculate gradients
            dw = (prediction - y_i) * x_i
            db = (prediction - y_i)

            # Update weights and bias
            weights -= learning_rate * dw
            bias -= learning_rate * db
            #print(f'i{i} weights\n{weights}\nbias\n{bias}')

        # Optionally, print the cost for tracking
        cost = np.mean((np.dot(X, weights) + bias - y) ** 2)
        if ((epoch+1) % 10) == 0:
        	print(f'Epoch {epoch+1}, Cost: {cost}')
    
    return weights, bias

def init_matrix(xlen,ylen):
	x = np.random.normal(0.0,2.0,(xlen,ylen))
	y = np.random.normal(3.0,10.0,(xlen,1))
	return x,y


def main():
	xlen = 10
	ylen = 10
	if len(sys.argv) > 1:
		xlen = int(sys.argv[1])
	if len(sys.argv) > 2:
		ylen = int(sys.argv[2])
	x,y = init_matrix(xlen,ylen)
	sys.stdout.write(f'x\n{x}\ny\n{y}\n')
	w,b = sgd(x,y)
	print(f'w {w} b {b}')
	return

main()

