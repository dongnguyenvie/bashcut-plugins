# BashCut Stickers

A sticker pack for BashCut's Stickers panel: 61 PNG and 20 animated GIF stickers. It needs BashCut with plugin API 6
(`contributes.stickers`); an older BashCut lists the plugin as outdated.

| Group | Stickers |
|---|---|
| Badges (`badge-*`) | WOW!, OMG, LOL, HOT, NEW, TOP 1, BEST, FREE, TIP, REVIEW, LIKE, FOLLOW, SUBSCRIBE, LIVE, YUMMY, NGON!, ĐỈNH, XỊN, QUÁ ĐÃ, XEM NGAY, MẸO HAY |
| Bursts (`burst-*`) | SALE, -50%, NEW, HOT DEAL, VS, GIẢM GIÁ, WOW |
| Speech bubbles (`bubble-*`) | empty, ?, !, HELLO, XIN CHÀO, HAHA |
| Arrows (`arrow-*`) | four directions in red and yellow, one white diagonal |
| Marks (`mark-*`) | heart, star, check, cross, ring, underline, pin, play, REC, viewfinder, bolt, crown, sparkles |
| Numbers (`number-*`) | 1 to 5 |
| Animated (`anim-*`) | pulsing heart, LIVE, SUBSCRIBE, FOLLOW and XEM NGAY; spinning star and SALE; bouncing arrows; blinking REC; wiggling WOW!, NGON! and ĐỈNH; NEW changing color; sparkles; a ring drawing itself; a check popping in; a typing bubble; a flashing bolt |

## Install and use

After a release is published, install it from **Plugins › Browse**. For a local checkout, run
`scripts/dev-link.sh stickers`, reopen **Plugins** in BashCut and choose **Trust**.

Open the **Stickers** panel: the pack is listed as **Essentials** under My stickers. Click a sticker to place it at
the playhead on an overlay layer at 35 % zoom; BashCut copies the image into the project's `stickers` folder, and
writes an animated one as a movie with alpha first. Agents use `bashcut stickers list` and `bashcut stickers add`.

## How it is made

The plugin is only images: BashCut lists the files in `stickers/` itself and never runs `bin/provider`, a stub that
exists because a manifest needs an entrypoint.

`src/sticker-pack.swift` draws every sticker with Core Graphics, so there is no third-party artwork and nothing is
downloaded. The images are committed. To change the pack, edit the lists in that script, run

```sh
swift plugins/stickers/src/sticker-pack.swift --sheet /tmp/stickers.png
```

look at the contact sheet, bump `version` in `plugin.json` and update the counts in `tests/test_pack.py`. GIF has
one transparent color, so the script hardens the edges of animated stickers and reads each file back to check that no
frame keeps pixels from the one before it.
