from glob import glob
from importlib.abc import Traversable
import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,jsonify
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.utils import secure_filename
import pandas as pd
from ANN import predict

pd.options.display.float_format = "{:,.2f}".format
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'upload')
ALLOWED_EXTENSIONS = {'xlsx', 'xls','sql','csv','epw'}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])

def get_data():
    if request.method == 'POST':

        wall_transmittance = request.form.get('thermalwall')
        roof_transmittance = request.form.get('thermalroof')
        wall_absorptance = request.form.get('wallabs')
        roof_absorptance = request.form.get('roofabs')
        internal_wall_option = request.form.get('wallint')
        solar_heat_gain = request.form.get('sghglazing')
        light_density  = request.form.get('lightdensity')
        weather = request.form.get('weather')

        if internal_wall_option == 'Light 1':
            internal_wall1 = 1
            internal_wall2 = 0
            internal_wall3 = 0
        if internal_wall_option == 'Light 2':
            internal_wall1 = 0
            internal_wall2 = 1
            internal_wall3 = 0
        else:
            internal_wall1 = 0
            internal_wall2 = 0
            internal_wall3 = 1

        data = {
            'Rooftransmittance': roof_transmittance,
            'Walltransmittance': wall_transmittance,
            'RoofAbsortance': roof_absorptance,
            'WallAbsortance': wall_absorptance,
            'SGH': solar_heat_gain,
            'DPI': light_density,
            'CDH': weather,
            'InternalWall1': internal_wall1,
            'InternalWall2': internal_wall2,
            'InternalWall3': internal_wall3, }

        df_ann = pd.DataFrame([data])

        prediction = predict(df_ann)
        prediction.to_csv('ThermalLoad.csv', index = False)


        consumo = prediction['Consumo']
        consumo = float(consumo)
        consumo = "{:.2f}".format(consumo)
        
        return render_template('sghospital.html',  consumo = consumo)
    consumo = 'not calculated'
    return render_template('sghospital.html', consumo = consumo)      
    
  
@app.route('/upload/<name>')
def download_file(name):
    return send_from_directory(UPLOAD_FOLDER, name)

if __name__ == "__main__":
    app.run(debug=True)