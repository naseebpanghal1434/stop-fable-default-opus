# Stop Fable — Default Opus

Claude remembers the last model you used.

If a new chat opens on **Fable** and you leave it selected, later chats open on Fable too. Most chats do not need Fable — it burns usage faster than Opus.

This extension switches a **new** chat off Fable onto **Opus**, once. Pick Fable yourself when you actually want it. Existing chats are not changed.

```
new chat opens on Fable  →  switch to Opus once
you then pick Fable      →  leave it
existing chat            →  never touched
```

Unofficial. Not affiliated with Anthropic.

## Install from source

1. Open `chrome://extensions`
2. Turn on **Developer mode**
3. **Load unpacked** → this folder
4. Open [claude.ai/new](https://claude.ai/new)

## Chrome Web Store

Paste-ready listing copy, privacy answers, and image files are in [`store/LISTING.md`](store/LISTING.md).

Pack the upload zip:

```sh
./scripts/pack.sh
```

That writes `dist/stop-fable-default-opus.zip`. Upload that zip — not this whole repo.

Privacy policy (HTTPS): https://naseebpanghal1434.github.io/stop-fable-default-opus/privacy.html
