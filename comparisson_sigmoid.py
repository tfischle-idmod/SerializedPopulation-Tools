import matplotlib.pyplot as plt
import numpy
import math
import bigfloat

x = numpy.linspace(-100, 100, num=10000)
value = 10
rate = 1.6
min_val = -100
max_val = 100

result0_bigf = []
with bigfloat.precision(200) + bigfloat.RoundTowardZero:
    for x_var in x:
        result0_bigf.append( 1.0 / (1.0 + bigfloat.exp(-x_var)) )


result = [{x: (1 / (1 + math.exp(-x))) } for x in range(-100, 100, 10)]
print( result )

result0 = 1.0 / (1.0 + numpy.exp(-x))
result1 = 1 / (1 + numpy.exp(-rate * x))
result2 = x / (1 + numpy.abs(-rate * x)) + 0.5
result3 = x / numpy.sqrt(1.0+(-rate * x)**2.0) + 0.5

result4 = min_val + (max_val-min_val) * 1.0/(1.0 + numpy.exp(-rate * x))
result5 = 0.5 + 0.5*numpy.tanh(x/2.0)
result6 = min_val + (max_val-min_val) * (0.5 + 0.5*numpy.tanh(rate*x/2.0))

#plt.plot(x, result0, "+", label="result0")
# plt.plot(x, result1, "+", label="result1")
# plt.plot(x, result2, "+", label="result2")
# plt.plot(x, result3, "+", label="result3")

result7 = 1.0 / (1.0 + numpy.exp( x ))
result8 = 0.5 + 0.5 * numpy.tanh(x / 2.0)

#plt.plot(x, result4, "+", label="sigmoid, exp")
#plt.plot(x, result5, "+", label="result5")
#plt.plot(x, result6, "+", label="sigmoid, tanh")


plt.plot(x, result0_bigf, "+", label="bigfloat")

error = result0-result5
print(max(error))
plt.plot(x, error, "+", label="error")
plt.legend(loc='upper left')
plt.show()
