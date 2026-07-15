Render a MtG decklist to an image using Typst.

```bash
./render-decklist.py <decklist-url-or-file> [--name "My Deck"]    \
                                            [--date "01/01/2026"] \
                                            [--score "5-0-0"]     \
                                            [-o "my-file.png"]    \
                                            [--debug]
```

<img src="bogles.png" alt="Preview of a rendererd decklist">

You can debug/watch the output by passing `--debug` to the python script and then
use `typst watch template.typ --open` to watch the template file for changes.
