from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from . import db
from .classification_hierarchies import *
from .models import User
import psycopg2

from .connect_dbs import *

n_cols = 5
n_rows = 5

def extract_images(curs,cell_types):
    curs.execute(
        "SELECT picture_id,label FROM labels;"
        )
    idxs_labels = curs.fetchall()
    idxs = [str(x[0]) for x in idxs_labels]
    labels = [x[1] for x in idxs_labels]
    idx2labels = {}
    for x,y in zip(idxs,labels):
        if x in idx2labels:
            idx2labels[x].append(y)
        else:
            idx2labels[x] = [y]
    idxs = list(idx2labels.keys())

    if len(idxs) > 0:
        curs.execute(
            "SELECT picture,id FROM images WHERE id IN ({});".format(
                ','.join(idxs)
            ))
        out = curs.fetchall()
    else:
        out = []

    o = [[bytes(x[0]).decode('utf-8'),x[1]] for x in out]
    output_dict = {}

    for img,i in o:
        output_dict[i] = {
            'image':img,
            'labels':[cell_types[x] for x in idx2labels[str(i)] if x != 'none']
            }
    return output_dict

def extract_picture(cursor,picture_id):
    sql = "SELECT picture, slide_id FROM images WHERE id = %s;"
    param = [picture_id]
    try:
        cursor.execute(sql,param)
        ablob, slide_id = cursor.fetchone()
        ablob = bytes(ablob) # convert the memory view
        return ablob.decode('utf-8'),slide_id
    except:
        return 0,0

def extract_label(cursor,picture_id,cell_types):
    sql = "SELECT label FROM labels WHERE (picture_id = %s::INTEGER) AND (user_id = %s::TEXT);"
    param = [picture_id,current_user.id]

    cursor.execute(sql,param)
    o = cursor.fetchone()
    if o is None:
        o = "none"
    else:
        o = o[0]
    if o not in cell_types:
        o = "none"
    return o

def insert_label(curs,conn,picture_id,label):
    sql = 'DELETE FROM labels WHERE picture_id = %s::INTEGER AND user_id = %s::TEXT;'
    param = [picture_id,current_user.id]
    curs.execute(sql,param)
    sql = 'INSERT INTO labels (picture_id, label, user_id) VALUES (%s, %s, %s);'
    param = [picture_id,label,current_user.id]
    curs.execute(sql,param)
    conn.commit()

cur_wbc = conn_wbc.cursor()
cur_wbc.execute(
    "SELECT number_of_images FROM metadata WHERE id = 1;")
n_wbc = cur_wbc.fetchone()[0]
max_page_wbc = n_wbc // (n_cols * n_rows)

cur_rbc = conn_rbc.cursor()
cur_rbc.execute(
    "SELECT number_of_images FROM metadata WHERE id = 1;")
n_rbc = cur_rbc.fetchone()[0]
max_page_rbc = n_rbc // (n_cols * n_rows)

image_display = Blueprint('image', __name__)

# No authorisation routing

@image_display.route('/no-authorisation')
@login_required
def no_authorisation():
    return render_template('no-authorisation.html')

# Serving WBC images

@image_display.route('/wbc_label',methods=['POST'])
@login_required
def get_wbc_label():
    jsdata = request.form
    label = jsdata['label']
    form_id = jsdata['form_id']
    picture_id = int(form_id[10:])
    insert_label(cur_wbc,conn_wbc,picture_id,label)
    user = User.query.filter_by(email=current_user.email).first()
    user.n_cells += 1
    db.session.commit()
    return jsdata

@image_display.route('/wbc=<page>')
@login_required
def wbc(page):
    if current_user.is_authorised == False:
        return no_authorisation()
    cur = conn_wbc.cursor()
    page = int(page)
    if page > max_page_wbc:
        return redirect(url_for('image.wbc',page=str(max_page_wbc)))
    if page < 1:
        return redirect(url_for('image.wbc',page=str(1)))
    page_offset = (page-1) * n_cols * n_rows
    idxs = [i + page_offset for i in range(1,n_cols*n_rows+1)]
    images = [extract_picture(cur,i)
              for i in idxs]
    image_blobs = [x[0] for x in images]
    slide_ids = [x[1] for x in images]

    labels = [extract_label(cur,i,wbc_cell_types) for i in idxs]

    return render_template(
        'cell-displayer-wbc.html',
        name=current_user.name,
        n_cols=n_cols,
        n_rows=n_rows,
        image_blobs=image_blobs,
        page=page,
        max_page=max_page_wbc,
        slide_ids=slide_ids,
        labels=labels,
        cell_hierarchy=wbc_cell_hierarchy,
        cell_idxs=idxs)

@image_display.route('/wbc-all')
@login_required
def wbc_all():
    if current_user.is_authorised == False:
        return no_authorisation()
    image_dict = extract_images(cur_wbc,wbc_cell_types)

    return render_template('all-cells.html',
                           image_dict=image_dict)

# Serving RBC images

@image_display.route('/rbc_label',methods=['POST'])
@login_required
def get_rbc_label():
    jsdata = request.form
    label = jsdata['label']
    form_id = jsdata['form_id']
    picture_id = int(form_id[10:])
    insert_label(cur_rbc,conn_rbc,picture_id,label)
    user = User.query.filter_by(email=current_user.email).first()
    user.n_cells += 1
    db.session.commit()
    return jsdata

@image_display.route('/rbc=<page>')
@login_required
def rbc(page):
    if current_user.is_authorised == False:
        return no_authorisation()
    cur = conn_rbc.cursor()
    page = int(page)
    if page > max_page_rbc:
        return redirect(url_for('image.rbc',page=str(max_page_rbc)))
    if page < 1:
        return redirect(url_for('image.rbc',page=str(1)))
    page_offset = (page-1) * n_cols * n_rows
    idxs = [i + page_offset for i in range(1,n_cols*n_rows+1)]
    images = [extract_picture(cur,i)
              for i in idxs]
    image_blobs = [x[0] for x in images]
    slide_ids = [x[1] for x in images]

    labels = [extract_label(cur,i,rbc_cell_types) for i in idxs]

    return render_template(
        'cell-displayer-rbc.html',
        name=current_user.name,
        n_cols=n_cols,
        n_rows=n_rows,
        image_blobs=image_blobs,
        page=page,
        max_page=max_page_rbc,
        slide_ids=slide_ids,
        labels=labels,
        cell_hierarchy=rbc_cell_hierarchy,
        cell_idxs=idxs)

@image_display.route('/rbc-all')
@login_required
def rbc_all():
    if current_user.is_authorised == False:
        return no_authorisation()
    image_dict = extract_images(cur_rbc,rbc_cell_types)

    return render_template('all-cells.html',
                           image_dict=image_dict)
