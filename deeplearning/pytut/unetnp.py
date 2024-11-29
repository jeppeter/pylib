import numpy as np

class ConvLayer:
    def __init__(self, input_channels, output_channels, kernel_size, stride, padding):
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.weights = np.random.randn(output_channels, input_channels, kernel_size, kernel_size)
        self.biases = np.zeros(output_channels)

    def forward(self, input_data):
        output_data = np.zeros((input_data.shape[0], self.output_channels, input_data.shape[2] - self.kernel_size + 1, input_data.shape[3] - self.kernel_size + 1))
        for i in range(self.output_channels):
            for j in range(input_data.shape[0]):
                for k in range(input_data.shape[2] - self.kernel_size + 1):
                    for l in range(input_data.shape[3] - self.kernel_size + 1):
                        output_data[j, i, k, l] = np.sum(input_data[j, :, k:k+self.kernel_size, l:l+self.kernel_size] * self.weights[i, :, :, :]) + self.biases[i]
        return output_data


class PoolingLayer:
    def __init__(self, pool_size, stride, padding):
        self.pool_size = pool_size
        self.stride = stride
        self.padding = padding

    def forward(self, input_data):
        output_data = np.zeros((input_data.shape[0], input_data.shape[2] - self.pool_size + 1, input_data.shape[3] - self.pool_size + 1))
        for i in range(input_data.shape[0]):
            for j in range(output_data.shape[1]):
                for k in range(output_data.shape[2]):
                    for l in range(self.stride):
                        output_data[i, j, k] = np.max(input_data[i, :, j*self.stride:j*self.stride+self.pool_size, k*self.stride:k*self.stride+self.pool_size])
        return output_data


class FullyConnectedLayer:
    def __init__(self, input_channels, output_channels, activation_function):
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.weights = np.random.randn(output_channels, input_channels)
        self.biases = np.zeros(output_channels)
        self.activation_function = activation_function

    def forward(self, input_data):
        output_data = np.zeros((input_data.shape[0], self.output_channels))
        for i in range(self.output_channels):
            for j in range(input_data.shape[0]):
                output_data[j, i] = np.dot(input_data[j, :], self.weights[i, :]) + self.biases[i]
                if self.activation_function == 'relu':
                    output_data[j, i] = np.maximum(0, output_data[j, i])
                elif self.activation_function == 'sigmoid':
                    output_data[j, i] = 1 / (1 + np.exp(-output_data[j, i]))
                elif self.activation_function == 'softmax':
                    output_data[j, i] /= np.sum(np.exp(output_data[j, :]))
        return output_data
