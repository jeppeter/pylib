#! /usr/bin/python

import numpy as np
import torch
from torch.utils import data
from torch import nn
import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
import d2ltorch  as d2l



true_w = torch.tensor([2, -3.4])
true_b = 4.2
features, labels = d2l.synthetic_data(true_w, true_b, 1000)

batch_size = 10
data_iter = d2l.load_array((features, labels), batch_size)

net = nn.Sequential(nn.Linear(2, 1))
net[0].weight.data.normal_(0, 0.01)
net[0].bias.data.fill_(0)
loss = nn.MSELoss()
trainer = torch.optim.SGD(net.parameters(), lr=0.01)
num_epochs = 3
for epoch in range(num_epochs):
    for X, y in data_iter:
        l = loss(net(X) ,y)
        trainer.zero_grad()
        l.backward()
        trainer.step()
    l = loss(net(features), labels)
    print(f'epoch {epoch + 1}, loss {l:f}')


w = net[0].weight.data
print('w errloss：', true_w - w.reshape(true_w.shape))
b = net[0].bias.data
print('b errloss：', true_b - b)