import json

with open('data/masterpieces.js', 'r', encoding='utf-8') as f:
    c = f.read()

start = c.find('window.MASTERPIECES =')
start_bracket = c.find('[', start)
end_bracket = c.rfind('];')
arts = json.loads(c[start_bracket:end_bracket+1])

for a in arts:
    if 'madonna' in a['id'].lower() or 'raphael' in a['id'].lower():
        print(a['id'], '->', a['title'], 'file:', a['file'])
