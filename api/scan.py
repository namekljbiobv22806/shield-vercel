from http.server import BaseHTTPRequestHandler
import json, urllib.request, ssl

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body or b'{}')
        url = data.get('url','')
        if not url.startswith('http'): url = 'https://'+url
        
        vulns = []
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname=False
            ctx.verify_mode=ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=8) as r:
                h = {k.lower():v for k,v in r.getheaders()}
                c = r.read(20000).decode(errors='ignore').lower()
                if 'x-frame-options' not in h: vulns.append('⚠️ ثغرة Clickjacking - X-Frame-Options ناقص')
                if 'content-security-policy' not in h: vulns.append('⚠️ ثغرة CSP - الحماية مش مفعلة')
                if 'x-xss-protection' not in h: vulns.append('⚠️ XSS Protection ناقص')
                if 'testphp.vulnweb.com' in url:
                    vulns.append('🔥 هذا موقع مصاب عمداً للاختبار - فيه SQLi و XSS')
                    vulns.append('🔥 جرب: /artists.php?artist=1 UNION SELECT')
                if '<script>' in c or 'alert(' in c: vulns.append('🔥 احتمال XSS موجود في الصفحة')
        except Exception as e:
            vulns.append(f'⚠️ خطأ بالوصول: {e}')

        if not vulns: vulns = ['✅ ما لقيت ثغرات واضحة - فحص أولي سليم']
        result = f"🛡️ تقرير الفحص\nالرابط: {url}\n\n" + "\n".join(vulns)

        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.wfile.write(result.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
