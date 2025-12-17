from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the stock data
df = pd.read_excel('data/data_j.xls', engine='xlrd')

# Create indices for faster search
df['コード'] = df['コード'].astype(str)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '').strip()
    search_type = data.get('type', 'auto')

    if not query:
        return jsonify({'error': '検索キーワードを入力してください'}), 400

    results = []

    if search_type == 'code':
        # Search by code
        matches = df[df['コード'] == query]
    elif search_type == 'name':
        # Search by name (partial match)
        matches = df[df['銘柄名'].str.contains(query, case=False, na=False, regex=False)]
    elif search_type == 'auto':
        # Auto detect: if query is ASCII alphanumeric and <= 5 chars, search by code, otherwise by name
        if query.isascii() and query.isalnum() and len(query) <= 5:
            matches = df[df['コード'] == query]
        else:
            matches = df[df['銘柄名'].str.contains(query, case=False, na=False, regex=False)]
    else:
        return jsonify({'error': '無効な検索タイプです'}), 400

    if matches.empty:
        return jsonify({'results': [], 'message': '該当する銘柄が見つかりませんでした'})

    # Format results
    for _, row in matches.iterrows():
        result = {
            'code': str(row['コード']),
            'name': str(row['銘柄名']),
            'market': str(row['市場・商品区分']),
            'industry17': str(row['17業種区分']) if pd.notna(row['17業種区分']) else '-'
        }
        results.append(result)

    return jsonify({'results': results, 'count': len(results)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
