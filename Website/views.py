from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import boto3
from werkzeug.utils import secure_filename
import pinecone
import pinecone.info
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from PyPDF2 import PdfFileReader
from io import BytesIO



views = Blueprint('views', __name__)

access_key = 'AKIA2BIH4HLCO6DGGAG7'
secret_access_key = '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'

s3 = boto3.resource(
    service_name = 's3',
    region_name = 'ap-south-1',
    aws_access_key_id = 'AKIA2BIH4HLCO6DGGAG7',
    aws_secret_access_key = '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'
)


@views.route('/')
# @login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/upload', methods = ['POST'])
@login_required
def upload():
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)

            img.save(filename)
            

            s3.Bucket('varunkalbhore-s3').upload_file(
                # Bucket = 'varunkalbhore-s3',
                Filename = filename,
                Key = 'PlagCheck/' + str(current_user.email) + '/' + str(filename)
            )

            # s3_object = s3.get_object(Bucket = 'varunkalbhore-s3', Key = 'PlagCheck/' + str(current_user.email) + '/' + str(filename))
            #print(s3_object)
            
            obj = s3.Bucket('varunkalbhore-s3').Object('PlagCheck/' + str(current_user.email) + '/' + str(filename)).get()
            text = obj['Body'].read().decode('ISO-8859-1')
            # print(text)
            
            # obj2 = s3.Object('varunkalbhore-s3', 'PlagCheck/' + str(current_user.email) + '/' + str(filename))
            # fs = obj2.get()['Body'].read()
            # pdf = PdfFileReader(BytesIO(fs))
            # print(pdf)
            # text2 = pdf.getFormTextFields()
            # print(text2)

            api_key = "533be2c5-142e-47e7-9a66-30252953adeb"
            pinecone.init(api_key=api_key, environment='us-west1-gcp')
            model = SentenceTransformer('all-mpnet-base-v2')
            index = pinecone.Index('dataset')
            encoding = model.encode(text).tolist()
            # print(encoding)
            top_k = 1
            result = index.query(queries=[encoding], top_k = top_k )
            print(result)
            abc=[x['score']for x in result['results'][0]['matches']]
            plag = int(abc[0]*100)
            

            if plag>30:
                msg = "Alert! " + str(plag) +"% Plagiarism found"
            else:
                msg = "Hurray! No Plagiarism Detected"    
            # msg = obj
        else:
            msg = "No files selected"

    return render_template("index.html", msg = msg, user=current_user)

