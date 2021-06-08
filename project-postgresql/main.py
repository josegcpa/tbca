from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
import psycopg2
from random import shuffle
from .classification_hierarchies import *

from .connect_dbs import *

def extract_images(curs):
    curs.execute(
        "SELECT picture_id,label FROM labels WHERE user_id = %s::TEXT",
        [current_user.id])
    idxs_labels = curs.fetchall()
    shuffle(idxs_labels)
    idxs = [str(x[0]) for x in idxs_labels]
    labels = [x[1] for x in idxs_labels]
    idx2label = {x:y for x,y in zip(idxs,labels)}

    if len(idxs) > 0:
        curs.execute(
            "SELECT picture,id FROM images WHERE id IN ({})".format(
                ','.join(idxs)
            ))
        out = curs.fetchall()
    else:
        out = []

    o = [bytes(x[0]).decode('utf-8') for x in out]
    idxs = [x[1] for x in out]
    labels = [idx2label[str(x)] for x in idxs]
    return o,labels,idxs

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    cur_wbc = conn_wbc.cursor()
    cur_rbc = conn_rbc.cursor()
    all_wbc,wbc_labels,wbc_idxs = extract_images(cur_wbc)
    all_rbc,rbc_labels,rbc_idxs = extract_images(cur_rbc)
    wbc_labels = [wbc_cell_types[x] for x in wbc_labels if x != 'none']
    rbc_labels = [rbc_cell_types[x] for x in rbc_labels if x != 'none']
    all_images = all_wbc + all_rbc
    all_labels = wbc_labels + rbc_labels
    all_idxs = wbc_idxs + rbc_idxs
    all_cell_types = ["WBC" for _ in wbc_labels] + ["RBC" for _ in rbc_labels]
    blobs_labels = [
        {'image':x,'label':y,'idx':z,'cell':c}
        for x,y,z,c in zip(all_images,all_labels,all_idxs,all_cell_types)]
    return render_template('profile.html',
                           name=current_user.name,
                           blobs_labels=blobs_labels)
