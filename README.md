giri
====

OS X only
brew install flac
run and speak to the mic (first second is usually lost though)

```py
from giri.speech import recognize
print recognize(lang='sv-SE', seconds=3, bits=16)
```
