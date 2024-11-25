#! /usr/bin/env python
import torch
import torch.nn as nn
import torch.optim as optim

# Step 1: Define the Neural Network Class
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(2, 4)  # Input layer to hidden layer
        self.fc2 = nn.Linear(4, 1)   # Hidden layer to output layer

    def forward(self, x):
        x = torch.relu(self.fc1(x))  # Apply ReLU activation
        x = self.fc2(x)               # Output layer
        return x

# Step 2: Prepare the Data
# Sample training data (features and labels)
X_train = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])  # Inputs
y_train = torch.tensor([[0.0], [1.0], [1.0], [0.0]])  # Corresponding outputs (XOR)

# Step 3: Instantiate the Model, Define Loss Function and Optimizer
model = SimpleNN()  # Instantiate the model
criterion = nn.MSELoss()  # Mean Squared Error for regression
optimizer = optim.SGD(model.parameters(), lr=0.1)  # Stochastic Gradient Descent with learning rate of 0.1

# Step 4: Training the Model
for epoch in range(1000):  # Run for 100 epochs
    model.train()  # Set the model to training mode

    # Forward pass
    outputs = model(X_train)
    loss = criterion(outputs, y_train)  # Calculate the loss

    # Backward pass and optimize
    optimizer.zero_grad()  # Clear previous gradients
    loss.backward()  # Compute gradients
    optimizer.step()  # Update weights

    if (epoch + 1) % 10 == 0:  # Print loss every 10 epochs
        print(f'Epoch [{epoch + 1}/100], Loss: {loss.item():.4f}')

# Step 5: Testing the Model
model.eval()  # Set the model to evaluation mode
with torch.no_grad():  # Disable gradient calculation
    test_data = torch.tensor([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    predictions = model(test_data)  # Get predictions
    print(f'Predictions:\n{predictions}')