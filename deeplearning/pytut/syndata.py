#! /usr/bin/env python

import sys
import torch
import os
import random
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
import d2ltorch


def data_iter(batch_size, features, labels):
    num_examples = len(features)
    indices = list(range(num_examples))
    #print(f'indices\n{indices}')
    # 这些样本是随机读取的，没有特定的顺序
    random.shuffle(indices)
    #print(f'shuffle indices\n{indices}')
    for i in range(0, num_examples, batch_size):
        batch_indices = torch.tensor(
            indices[i: min(i + batch_size, num_examples)])
        #print(f'{i} batch_indices\n{batch_indices}')
        yield features[batch_indices], labels[batch_indices]


torch.set_printoptions(threshold=100000)
true_w = torch.tensor([2, -3.4])
true_b = 4.2
features, labels = d2ltorch.synthetic_data(true_w, true_b, 1000)
print(f'features\n{features}')
print(f'labels\n{labels}')

batch_size = 10

#for X, y in data_iter(batch_size, features, labels):
#    print(X, '\n', y)    


w = torch.normal(0, 0.01, size=(2,1), requires_grad=True)
b = torch.zeros(1, requires_grad=True)

lr = 0.03
num_epochs = 3
net = d2ltorch.linreg
loss = d2ltorch.squared_loss

for epoch in range(num_epochs):
    for X, y in data_iter(batch_size, features, labels):
        l = loss(net(X, w, b), y)  # X和y的小批量损失
        # 因为l形状是(batch_size,1)，而不是一个标量。l中的所有元素被加到一起，
        # 并以此计算关于[w,b]的梯度
        l.sum().backward()
        d2ltorch.sgd([w, b], lr, batch_size)  # 使用参数的梯度更新参数
    with torch.no_grad():
        train_l = loss(net(features, w, b), labels)
        print(f'epoch {epoch + 1}, loss {float(train_l.mean()):f}')


print(f'w errloss: {true_w - w.reshape(true_w.shape)}')
print(f'b errloss: {true_b - b}')