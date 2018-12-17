# ulauncher-clipboard

[Ulauncher](https://ulauncher.io) extension for managing your clipboard, using Gpaste

Ulauncher-clipboard uses the keyword `c` for "copy" to searching your clipboard history and copy to your actual clipboard so you can paste it elsewhere.

New keyboards for `paste` and `delete` may be added (not sure how to implement paste though).

## Caveats

This extension is work in progress, and it's not stable yet. Besides this, it's pushing the boundaries of what Ulauncher's extensions API were designed to support. Both of these created caveats.

* It's not even tested with non-text entries
* Non-latin characters can't be searched. Since Ulauncher is moving to Python 3, I expect this to be fixed upstream eventually.
* The xml file is parsed and searched on every keystroke. I can't notice any real lag or issues about this, but it's inefficient. Unfortunately Ulauncher's events are a bit primitive for handling this, so some kind of time based workaround may be required.
* Search results are limited with a rather primitive method, that doesn't support highlighting and only formats/limits the context based on characters (not line breaks and characters)
* Features
  * Support for other clipboard managers would be nice (the current integration is not very deep and could be abstracted).
  * Paste isn't implemented (not supported by Ulauncher, but could perhaps be done separately). If paste is supported copy alone doesn't make much sense. (the paste action could actually do both).
  * Delete / Forget isn't implemented either.
  * Should the features use the same keyword or individual? Should another step be added where the user gets to see the full clipboard entry and choose to copy, paste or delete?

The icon is part of [Paper Icons](http://snwh.org/paper/icons) by [Sam Hewitt](http://samuelhewitt.com/), and is licensed under [CC-SA-4.0](http://creativecommons.org/licenses/by-sa/4.0/)
