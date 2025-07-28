from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
import uuid
import json
import pickle
import tempfile

from autoeda_engine import generate_selected_plot

app = Flask(__name__)
app.secret_key = "supersecretkey123456789"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/plots', exist_ok=True)
os.makedirs('temp_data', exist_ok=True)

def cleanup_temp_files():
    """Clean up temporary files older than 1 hour"""
    import time
    current_time = time.time()
    temp_dir = 'temp_data'
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            if filename.endswith('.pkl'):
                filepath = os.path.join(temp_dir, filename)
                if current_time - os.path.getmtime(filepath) > 3600:  # 1 hour
                    try:
                        os.remove(filepath)
                        print(f"[INFO] Cleaned up old temp file: {filename}")
                    except:
                        pass

@app.route('/', methods=['GET'])
def upload_page():
    cleanup_temp_files()  # Clean up old files
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))

    if not file.filename.lower().endswith('.csv'):
        flash('Please upload a CSV file', 'error')
        return redirect(url_for('upload_page'))

    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Basic validation
        if df.empty:
            flash('The uploaded file is empty', 'error')
            return redirect(url_for('upload_page'))
        
        if len(df.columns) < 1:
            flash('The uploaded file has no valid columns', 'error')
            return redirect(url_for('upload_page'))

        print(f"[INFO] Uploaded: {file.filename}")
        print(f"[INFO] Shape: {df.shape}")
        print(f"[INFO] Columns: {df.columns.tolist()}")
        
        # Store data in temporary file
        data_id = str(uuid.uuid4())
        data_file = os.path.join('temp_data', f'{data_id}.pkl')
        
        # Save DataFrame to pickle file
        with open(data_file, 'wb') as f:
            pickle.dump({
                'df': df,
                'filename': file.filename,
                'columns': df.columns.tolist(),
                'shape': df.shape
            }, f)
        
        # Store reference in session
        session['data_id'] = data_id
        
        print(f"[INFO] Data saved to: {data_file}")
        print(f"[INFO] Data ID: {data_id}")
        
        flash(f'Successfully uploaded {file.filename} with {len(df.columns)} columns and {len(df)} rows', 'success')
        return redirect(url_for('options'))
        
    except pd.errors.EmptyDataError:
        flash('The uploaded file is empty or corrupted', 'error')
        return redirect(url_for('upload_page'))
    except pd.errors.ParserError:
        flash('Error parsing CSV file. Please check the file format', 'error')
        return redirect(url_for('upload_page'))
    except Exception as e:
        print(f"[ERROR] Reading CSV failed: {e}")
        flash(f'Error reading file: {str(e)}', 'error')
        return redirect(url_for('upload_page'))

@app.route('/options', methods=['GET'])
def options():
    try:
        if 'data_id' not in session:
            flash('No data available. Please upload a file first.', 'error')
            return redirect(url_for('upload_page'))

        # Load data from temporary file
        data_id = session['data_id']
        data_file = os.path.join('temp_data', f'{data_id}.pkl')
        
        if not os.path.exists(data_file):
            flash('Data file not found. Please upload a file again.', 'error')
            session.pop('data_id', None)
            return redirect(url_for('upload_page'))
        
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
        
        columns = data['columns']
        filename = data['filename']
        
        print(f"[INFO] Loaded data for: {filename}")
        print(f"[INFO] Columns: {len(columns)}")
        
        return render_template('options.html', 
                             columns=columns, 
                             filename=filename,
                             num_columns=len(columns))
    except Exception as e:
        print(f"[ERROR] Options page error: {e}")
        flash('Error loading options page', 'error')
        return redirect(url_for('upload_page'))

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'data_id' not in session:
            flash('No data available. Please upload a file first.', 'error')
            return redirect(url_for('upload_page'))

        # Get form data
        selected_columns = request.form.getlist('columns')
        plot_type = request.form.get('plot_type')

        if not selected_columns:
            flash('Please select at least one column', 'error')
            return redirect(url_for('options'))

        if not plot_type:
            flash('Please select a plot type', 'error')
            return redirect(url_for('options'))

        # Load data from temporary file
        data_id = session['data_id']
        data_file = os.path.join('temp_data', f'{data_id}.pkl')
        
        if not os.path.exists(data_file):
            flash('Data file not found. Please upload a file again.', 'error')
            session.pop('data_id', None)
            return redirect(url_for('upload_page'))
        
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
        
        df = data['df']
        
        # Validate selected columns exist in the data
        available_columns = set(df.columns)
        selected_columns = [col for col in selected_columns if col in available_columns]
        
        if not selected_columns:
            flash('None of the selected columns exist in the data', 'error')
            return redirect(url_for('options'))

        # Generate plots
        plots = generate_selected_plot(df, selected_columns, plot_type)
        
        if not plots:
            flash('Failed to generate plot. Please check your data and try again.', 'error')
            return redirect(url_for('options'))

        return render_template('results.html', 
                             plots=plots, 
                             plot_type=plot_type,
                             columns=selected_columns,
                             filename=data['filename'],
                             error=None)
                             
    except Exception as e:
        print(f"[ERROR] Analysis error: {e}")
        return render_template('results.html', 
                             plots=[], 
                             error=f"Error generating plot: {str(e)}")

@app.route('/clear', methods=['POST'])
def clear_session():
    # Clean up temporary files
    if 'data_id' in session:
        data_id = session['data_id']
        data_file = os.path.join('temp_data', f'{data_id}.pkl')
        if os.path.exists(data_file):
            os.remove(data_file)
    
    session.clear()
    flash('Session cleared. You can upload a new file.', 'info')
    return redirect(url_for('upload_page'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Please upload a file smaller than 16MB.', 'error')
    return redirect(url_for('upload_page'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

