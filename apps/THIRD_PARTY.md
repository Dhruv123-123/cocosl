# Third-party code and data

Everything in `apps/` is our own work except what's listed here. When you copy MIT or BSD code or data in,
add it to this file with its copyright line and licence text (that's the licence's one condition), and say
on the page where the data comes from. Never imply endorsement: "uses data from X", not "X-approved".

## Scam Shield link checker: reported-phishing domains

- **What:** a hashed, trimmed copy of two public phishing-domain lists, shipped as
  `scam-checker/phishlist/phish.bin` (under 420 KB) and checked in the browser. The address someone checks is
  never sent anywhere.
- **Sources:** [DestroyList](https://github.com/phishdestroy/destroylist) "Primary Active" domains, plus
  [Phishing.Database](https://github.com/Phishing-Database/Phishing.Database) "ACTIVE" domains that DestroyList
  also lists. DestroyList's allowlist and our known official domains are removed.
- **Refresh:** `node scam-checker/tools/refresh-blocklist.mjs`, then `node tools/build-app-shell.mjs`,
  `npm test`, commit. Every week or two is plenty.
- **Credit on the page:** footer of `/link/` and `/es/enlace/`, plus the date line under each result. A
  listed result links to DestroyList's appeals form for site owners.
- **Licence copy that ships with the data:** `scam-checker/phishlist/NOTICE.txt`.

### DestroyList licence

```
MIT License

Copyright (c) 2019 PhishDestroy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Phishing.Database licence

```
MIT License

Copyright (c) 2018-2025 Mitchell Krog - github.com/mitchellkrogza
Copyright (c) 2018-2025 Nissar Chababy - github.com/funilrys
Copyright (c) 2018-2025 Phishing.Database Contributors - github.com/Phishing-Database

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
