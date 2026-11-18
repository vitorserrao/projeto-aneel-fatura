#!/bin/sh
TOKEN=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill | sed -n 's/^password=//p')
curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.github+json" "https://api.github.com/repos/vitorserrao/projeto-aneel-fatura/pulls?state=all&head=vitorserrao:fix-planejamento-demanda-verde" | node parse_prs.js
