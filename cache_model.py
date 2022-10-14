from detoxify import Detoxify

model = Detoxify('original')
model.predict('cache warm up')
model = Detoxify('unbiased')
model.predict('cache warm up')
model = Detoxify('multilingual')
model.predict('cache warm up')
