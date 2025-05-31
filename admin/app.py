from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from livereload import Server
import os
from dotenv import load_dotenv
from database import send_data_to_db, get_manual
import qrcode
from ytapi import get_youtube_videos

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
ADMIN_PASS = os.getenv('ADMIN_PASS')
main_website = os.getenv('MAIN_WEBSITE_NAME')
streamlit_app = os.getenv('STREAMLIT_APP_NAME')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if password == ADMIN_PASS:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('admin'))
        else:
            flash('Incorrect Password. Access Denied.')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('admin.html')


@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    data = request.form
    send_data_to_db(data)
    manual_id = data['id']
    return redirect(url_for('manual_created', id=manual_id))


@app.route('/manual-created/<id>')
def manual_created(id):
    manual_url = f"http://{main_website}/manual/{id}"

    qr_folder = os.path.join('static', 'qr')
    os.makedirs(qr_folder, exist_ok=True)
    qr_path = os.path.join(qr_folder, f'manual_{id}.png')

    # generates and save qr code
    img = qrcode.make(manual_url)
    img.save(qr_path)

    qr_image_url = f'/static/qr/manual_{id}.png'

    return render_template('qr_display.html', qr_image_url=qr_image_url, manual_url=manual_url)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/manual/<string:id>')
def view_manual(id):
    manual = get_manual(id)
    videos = get_youtube_videos(manual['title'], results=3)
    return render_template('manual.html', manual=manual, videos=videos)


@app.route('/api/manual/<manual_id>', methods=['GET'])
def api_get_manual(manual_id):
    manual = get_manual(manual_id)
    if manual:
        return jsonify({
            'id': manual['id'],
            'outcomes': manual['outcomes'],
            'title': manual['title'],
            'apparatus': manual['apparatus'],
            'theory': manual['theory'],
            'procedures': manual['procedures'],
            'result': manual['result'],
            'precautions': manual['precautions'],
            'qna': manual['qna'],
            'link': manual['link']
        })
    else:
        return jsonify({
            'error': 'Manual Not Found'
        })


@app.route('/chat-with-ai/<manual_id>')
def chat_redirect(manual_id):
    return redirect(f'http://{streamlit_app}/?id={manual_id}')


if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('templates/')
    server.watch('static/')
    server.serve(debug=True, port=5000)
