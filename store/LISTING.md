# Chrome Web Store listing

Copy these fields into [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole) after you upload `dist/stop-fable-default-opus.zip`.

Pack the zip from the repo root:

```sh
./scripts/pack.sh
```

## Item

| Field | Value |
| --- | --- |
| Name | Stop Fable — Default Opus |
| Version | 1.0.0 (from `manifest.json`) |
| Visibility | Public |
| Category | Productivity |
| Language | English |
| Mature content | No |

## Short description (max 132 characters)

```
New Claude chats that auto-pick Fable are switched to Opus once. You can still choose Fable.
```

Count: 92 characters.

## Detailed description

```
Claude remembers the last model you used.

If a new chat opens on Fable and you leave it selected, later chats open on Fable too. Most chats do not need Fable — it uses your limit faster than Opus.

Stop Fable — Default Opus switches a new Claude chat off Fable onto the best Opus in the menu (Opus 5 when it is listed). You can still pick Fable from the model menu when you want it. Existing chats are not changed.

How it works
• Only runs on claude.ai and claude.com
• Only acts on a new chat whose model chip says Fable
• Clicks Opus once, then stops
• If you choose Fable yourself, it leaves that choice alone

This is an unofficial extension. It is not affiliated with, endorsed by, or sponsored by Anthropic.
```

## Graphic assets to upload

Drag from `store/upload/` — these are **not** inside the zip.

Fill-the-form page: https://naseebpanghal1434.github.io/stop-fable-default-opus/form.html

| Dashboard field | File | Size | Caption |
| --- | --- | --- | --- |
| Store icon | `store/upload/01-store-icon-128.png` | 128×128 | — |
| Screenshot 1 | `store/upload/02-screenshot-fable-sticks.png` | 1280×800 | Leave Fable selected, and later chats stay on Fable. |
| Screenshot 2 | `store/upload/03-screenshot-switched-to-opus.png` | 1280×800 | New chats are switched to Opus once. |
| Screenshot 3 | `store/upload/04-screenshot-toolbar-popup.png` | 1280×800 | Toolbar popup — pick Fable yourself when you want it. |
| Small promo tile (required) | `store/upload/05-promo-small-440x280.png` | 440×280 | — |
| Marquee promo (optional) | `store/upload/06-promo-marquee-1400x560.png` | 1400×560 | — |
| Extra 512 icon (if asked) | `store/upload/07-store-icon-512.png` | 512×512 | — |

## Privacy policy URL

```
https://naseebpanghal1434.github.io/stop-fable-default-opus/privacy.html
```

Repo: https://github.com/naseebpanghal1434/stop-fable-default-opus

## Privacy practices tab

**Single purpose:** On a new Claude chat, if Fable is auto-selected, switch the model menu to Opus once.

Does this item:

| Question | Answer |
| --- | --- |
| Collect personally identifiable info | No |
| Collect health info | No |
| Collect financial and payment info | No |
| Collect authentication info | No |
| Collect personal communications | No |
| Collect location | No |
| Collect web history | No |
| Collect user activity | No |
| Collect website content | Yes — the on-screen model name only, in the current tab, in memory, not stored, not transmitted |
| Transmit user data off the device | No |
| Sell user data | No |
| Use data for ads / credit / lending | No |

Certify Limited Use: Yes.

## Permission justifications

The zip has **no** `permissions` array. Only host access:

| Permission | Type | Justification |
| --- | --- | --- |
| `https://claude.ai/*` | host_permissions | Content script must run on Claude’s site to read the model chip and click Opus when a new chat auto-selects Fable. |
| `https://claude.com/*` | host_permissions | Same feature on the claude.com host, which serves the same app. |

Do not add `storage`, `tabs`, `scripting`, or `<all_urls>`. They are unused.

## Distribution checklist

1. Pay the one-time Chrome Web Store developer fee if this is a new publisher account.
2. `./scripts/pack.sh`
3. Dashboard → New item → upload the zip.
4. Paste the listing fields above.
5. Upload the six image files.
6. Paste the hosted privacy policy URL.
7. Fill Privacy practices to match the table.
8. Save draft → Submit for review.

Review often takes a few days. Host permissions on a specific site are expected for this item; keep the justification specific.
