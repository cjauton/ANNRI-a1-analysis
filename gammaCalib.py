import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Step 1: Define your gamma-ray peak energies and widths
# Specify the known gamma-ray peak energies and corresponding widths
known_peak_energies = [511, 662, 1173, 1332]  # Energy values in keV
known_peak_widths = [10, 12, 15, 18]  # Width values in channels

# Step 2: Generate synthetic training data
# Assuming you have a gamma-ray spectrum stored in the `spectrum` variable

# Define a function to generate synthetic training data
def generate_training_data(energies, widths, num_samples):
    x = []
    y = []

    for _ in range(num_samples):
        peak_index = np.random.randint(len(energies))
        energy = energies[peak_index]
        width = widths[peak_index]

        # Generate synthetic peak with noise
        peak = np.random.normal(loc=energy, scale=width)
        x.append([peak])
        y.append([energy])

    return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32)

# Generate synthetic training data
train_x, train_y = generate_training_data(known_peak_energies, known_peak_widths, num_samples=10000)

# Step 3: Define and train the model
class LinearRegression(nn.Module):
    def __init__(self):
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(1, 1)

    def forward(self, x):
        return self.linear(x)

model = LinearRegression()

criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

num_epochs = 100
for epoch in range(num_epochs):
    inputs = torch.from_numpy(train_x)
    labels = torch.from_numpy(train_y)

    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f'Epoch: {epoch+1}/{num_epochs}, Loss: {loss.item()}')

# Step 4: Calibrate the gamma-ray spectrum
# Assuming you have a gamma-ray spectrum stored in the `spectrum` variable

# Prepare the spectrum data for calibration
spectrum_data = np.array(spectrum)  # Convert the spectrum to a numpy array
calibration_input = torch.from_numpy(spectrum_data.reshape(-1, 1)).float()

# Use the trained model for calibration
calibrated_spectrum = model(calibration_input).detach().numpy()

# Print the calibrated spectrum
print(calibrated_spectrum)
