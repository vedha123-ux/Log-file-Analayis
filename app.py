import os
import re
from flask import Flask, render_template, request
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        file = request.files['logfile']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:2000]

            status_counts = Counter()
            url_counts = Counter()
            response_times = []

            log_pattern = re.compile(r'\"(GET|POST|PUT|DELETE|HEAD) (.*?) HTTP/1.[01]\" (\d{3}) (\d+)?$')

            for line in lines:
                match = log_pattern.search(line)
                if match:
                    method, url, status, *rest = match.groups()
                    status_counts[status] += 1
                    url_counts[url] += 1
                    if rest and rest[0]:
                        try:
                            response_times.append(int(rest[0]))
                        except:
                            pass

            results['status_codes'] = dict(status_counts)
            results['top_urls'] = url_counts.most_common(5)
            results['avg_response_time'] = round(sum(response_times)/len(response_times), 2) if response_times else None

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
