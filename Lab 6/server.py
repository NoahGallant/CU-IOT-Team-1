from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient()
db = client.mydb

collection = db.noah_move 

import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

data = list(collection.find({}))

x = []
y = []

for d in data:
        r = np.array(d['data'], dtype='f')[:1].T.flatten()
        x.append(r)
        y.append(d['letter'])


X = np.array(x)
y = np.array(y)

pca = PCA(n_components=9)


X = normalize(X, axis=1)

pca.fit(X)

X = pca.transform(X)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)

split = int(len(X)*0.55)

X_train = X[:split]
y_train = y[:split]

X_test = X[split:]
y_test = y[split:]

model = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10),
                         n_estimators=500)
model.fit(X_train, y_train)

print(model.score(X_test, y_test))

@app.route('/insert', methods=['POST'])
def insert():
    data = request.get_json()
    if data['letter'] == '':
	inp = [np.array(data['data'][:1]).T.flatten()]
	inp = pca.transform(inp)
	inp = normalize(inp)
	res = model.predict(inp)
	print(res)
	return str(res)
    else:
	collection.insert_one(data)
    return "Data for letter: " + data['letter'] + " inserted"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
