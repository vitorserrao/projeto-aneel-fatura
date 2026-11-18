let data = '';
process.stdin.on('data', c => data += c);
process.stdin.on('end', () => {
  const arr = JSON.parse(data);
  if (!Array.isArray(arr)) { console.log(data); return; }
  for (const p of arr) {
    console.log(p.number + ' | ' + p.title + ' | ' + p.state + ' | ' + p.html_url);
  }
});
