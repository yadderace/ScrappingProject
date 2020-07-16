from flask import Flask, request, jsonify
import numpy as np
import pickle 

app = Flask(__name__)

@app.route('/predict', methods = ['POST'])
def predict():
    #directory = 'C:/Users/yadde/Documents/'
    #model = pickle.load(open(directory + 'lr1594755397.679078.mdl', 'rb'))
    dfParams = pd.DataFrame(request.get_json)
    print(dfParams)

   # prediction = model.predict([np.array(list(data.values()))])
    #print(prediction)

    #output = prediction[0]

    #return jsonify(output)
    return "Hola"
    

if __name__ == "__main__":
    app.run()