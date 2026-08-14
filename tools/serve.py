#!/usr/bin/env python3
"""
Servidor local de desenvolvimento, com cache desligado.

Por que não usar `python -m http.server` direto: ele responde apenas com
`Last-Modified`, sem `Cache-Control` nem `ETag`. O navegador então aplica
cache heurístico e continua exibindo CSS antigo depois de uma alteração — o
HTML é rebuscado, o CSS não, e a página aparece meio nova e meio velha.

Isso aconteceu de verdade neste projeto: depois da troca de paleta, o
servidor já entregava o verde novo (verificado por curl) enquanto o
navegador ainda mostrava o dourado antigo e o desalinhamento já corrigido.
Custou uma rodada inteira de conversa até ficar claro que o defeito era de
cache, não de código.

`Cache-Control: no-store` elimina a classe inteira desse problema — em
desenvolvimento, sempre queremos o arquivo do disco.

Uso:
    python tools/serve.py          # porta 8080
    python tools/serve.py 3000     # outra porta
"""

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


class SemCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, formato, *args):
        # Silencia o ruído de 200 em asset; só erro interessa no terminal.
        if args and len(args) > 1 and str(args[1]).startswith(("4", "5")):
            super().log_message(formato, *args)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = partial(SemCache, directory=str(RAIZ))
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), handler)
    print(f"Lumina em http://localhost:{porta}  (cache desligado)")
    print("Ctrl+C para parar.")
    servidor.serve_forever()
